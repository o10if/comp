"""
This script visits each sub-directory in `end-to-end` and compiles its source file.
Currently it only compiles with GCC and clang but the goal is to also run our compiler and check
the output.
"""

import argparse
import json
import os
import subprocess

END_TO_END_ROOT = os.path.dirname(os.path.realpath(__file__))
PROJECT_ROOT = os.path.realpath(os.path.join(END_TO_END_ROOT, ".."))
CONFIG_FILE_NAME = "test.json"
DEFAULT_CLANG_PATH = "clang"
DEFAULT_DOT_PATH = "dot"
DEFAULT_GCC_PATH = "gcc"
DEFAULT_O10C_PATH = os.path.join(PROJECT_ROOT, "build", "o10c")


####################################################################################################
# Global options                                                                                   #
####################################################################################################


class GlobalOptions:
    def __init__(self):
        self.clang_path = DEFAULT_CLANG_PATH
        self.dot_path = DEFAULT_DOT_PATH
        self.gcc_path = DEFAULT_GCC_PATH
        self.o10c_path = os.environ["O10C_PATH"] if "O10C_PATH" in os.environ else DEFAULT_O10C_PATH
        self.no_dot = False


GLOBAL_OPTIONS = GlobalOptions()


####################################################################################################
# Command line options                                                                             #
####################################################################################################

# Main parser
CLI_PARSER = argparse.ArgumentParser()  # type: argparse.ArgumentParser

CLI_PARSER.add_argument(u'--gcc-path',
                        action=u'store',
                        nargs=1,
                        type=str,
                        help=u'The path to the local directory to synchronize (default: current '
                             u'working directory)')
CLI_PARSER.add_argument(u'--no-dot',
                        action=u'store_true',
                        default=False,
                        help=u'Ignore PNG rendition for dot files')


####################################################################################################
# Test configurations                                                                              #
####################################################################################################


class AstTestConfig():
    def __init__(self):
        self.skip = False
        self.hidden = False
        self.actual_ast_path = None
        self.expected_ast_path = None
        self.expected_return_code = 0

    @staticmethod
    def from_json(doc, test_dir):
        config = AstTestConfig()
        if "skip" in doc and doc["skip"]:
            config.skip = True
            return config
        if "hidden" in doc and doc["hidden"]:
            config.hidden = True
            return config

        if "return-code" in doc:
            config.expected_return_code = doc["return-code"]

        if "actual-json" in doc:
            config.actual_ast_path = os.path.join(test_dir, doc["actual-json"])

        if "expected-json" in doc:
            config.expected_ast_path = os.path.join(test_dir, doc["expected-json"])

        return config


class IrTestConfig():
    def __init__(self):
        self.skip = False
        self.hidden = False
        self.actual_dot_path = None
        self.actual_png_path = None
        self.expected_ir_path = None
        self.expected_return_code = 0

    @staticmethod
    def from_json(doc, test_dir, optimized=False):
        config = IrTestConfig()
        if "skip" in doc and doc["skip"]:
            config.skip = True
            return config
        if "hidden" in doc and doc["hidden"]:
            config.hidden = True
            return config

        prefix = "optimized__" if optimized else ""

        if "return-code" in doc:
            config.expected_return_code = doc["return-code"]

        if "actual-dot" in doc:
            config.actual_dot_path = os.path.join(test_dir, prefix + doc["actual-dot"])

        if "actual-png" in doc:
            config.actual_png_path = os.path.join(test_dir, prefix + doc["actual-png"])

        if "expected-dot" in doc:
            config.expected_ir_path = os.path.join(test_dir, prefix + doc["expected-dot"])

        return config


class RunTestConfig():
    def __init__(self):
        self.skip = False
        self.hidden = False
        self.actual_assembly_path = None
        self.actual_stdout_path = None
        self.actual_stderr_path = None
        self.executable_path = None
        self.expected_assembly_path = None
        self.expected_stdout_path = None
        self.expected_stderr_path = None
        self.expected_return_code = None
        self.stdin_path = None


    @staticmethod
    def from_json(doc, test_dir, optimized=False):
        config = RunTestConfig()
        if "skip" in doc and doc["skip"]:
            config.skip = True
            return config
        if "hidden" in doc and doc["hidden"]:
            config.hidden = True
            return config

        prefix = "optimized__" if optimized else ""

        config.actual_assembly_path = os.path.join(test_dir, prefix + doc["actual-assembly"])
        config.executable_path = os.path.join(test_dir, prefix + doc["executable"])

        if "return-code" in doc:
            config.expected_return_code = doc["return-code"]

        if "actual-stdout" in doc:
            config.actual_stdout_path = os.path.join(test_dir, prefix + doc["actual-stdout"])

        if "actual-stderr" in doc:
            config.actual_stderr_path = os.path.join(test_dir, prefix + doc["actual-stderr"])

        if "expected-assembly" in doc:
            config.expected_assembly_path = os.path.join(test_dir, prefix + doc["expected-assembly"])

        if "expected-stderr" in doc:
            config.expected_stderr_path = os.path.join(test_dir, prefix + doc["expected-stderr"])

        if "expected-stdout" in doc:
            config.expected_stdout_path = os.path.join(test_dir, prefix + doc["expected-stdout"])

        if "stdin" in doc:
            config.stdin_path = os.path.join(test_dir, prefix + doc["stdin"])

        return config


class TestConfig():
    def __init__(self):
        self.skip = False
        self.hidden = False
        self.source_path = None  # type: str
        self.ast = None  # type: AstTestConfig
        self.ir = None  # type: IrTestConfig
        self.ir_optimized = None  # type: IrTestConfig
        self.run = None  # type: RunTestConfig
        self.run_optimized = None  # type: RunTestConfig

    @staticmethod
    def from_json(doc, test_dir):
        config = TestConfig()
        if "skip" in doc and doc["skip"]:
            config.skip = True
            return config
        if "hidden" in doc and doc["hidden"]:
            config.hidden = True
            return config

        if "source" in doc:
            config.source_path = os.path.join(test_dir, doc["source"])
        else:
            raise RuntimeError("Missing source path for: {}".format(test_dir))

        if "ast" in doc:
            config.ast = AstTestConfig.from_json(doc["ast"], test_dir)

        if "ir" in doc:
            config.ir = IrTestConfig.from_json(doc["ir"], test_dir)
            config.ir_optimized = IrTestConfig.from_json(doc["ir"], test_dir, optimized=True)

        if "run" in doc:
            config.run = RunTestConfig.from_json(doc["run"], test_dir)
            config.run_optimized = RunTestConfig.from_json(doc["run"], test_dir, optimized=True)

        return config


####################################################################################################
# Test suite                                                                                       #
####################################################################################################


class TestCase:
    def __init__(self, dir):
        self.dir = dir  # type: str
        self.config = None  # type: TestConfig
        try:
            with open(os.path.join(dir, CONFIG_FILE_NAME), "r") as config_file:
                config_content = config_file.read()
                config_doc = json.loads(config_content)
                self.config = TestConfig.from_json(config_doc, dir)
        except:
            raise Exception("Invalid test config: {}".format(os.path.join(dir, CONFIG_FILE_NAME)))

    def test(self):
        if self.config.hidden:
            return {}
        elif self.config.skip:
            result = {}
            if self.config.ast is not None and not self.config.ast.hidden:
                result["ast"] = ("skipped", None)
            if self.config.ir is not None and not self.config.ir.hidden:
                result["ir"] = ("skipped", None)
            if self.config.run is not None and not self.config.run.hidden:
                result["run"] = ("skipped", None)
            if len(result.items()) == 0:
                result["*"] = ("skipped", None)
            return result
        else:
            return {
                "ast": self.test_ast(),
                "ir": self.test_ir(),
                "ir-optimized": self.test_ir(optimized=True),
                "run": self.test_run(),
                "run-optimized": self.test_run(optimized=True)
            }

    def test_ast(self):
        if self.config.ast is None or self.config.ast.hidden:
            return "hidden", None
        elif self.config.ast.skip:
            return "skipped", None

        process = subprocess.Popen(
            [GLOBAL_OPTIONS.o10c_path, "--ast", self.config.source_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate()
        utf8_stdout = stdout.decode("UTF-8")
        utf8_stderr = stderr.decode("UTF-8")

        if process.returncode != self.config.ast.expected_return_code:
            msg = ("Unexpected return code. Actual: {}, Expected: {}\n"
                   "stdout:\n"
                   "{}\n"
                   "stderr:\n"
                   "{}"
                   ).format(process.returncode, self.config.ast.expected_return_code, utf8_stdout, utf8_stderr)
            return "failed", msg

        if process.returncode == 0:
            try:
                actual_ast_doc = json.loads(utf8_stdout)
            except json.decoder.JSONDecodeError as err:
                msg = ("Unable to parse the AST returned by the compiler:\n"
                       "stdout:\n"
                       "{}\n"
                       "stderr:\n"
                       "{}\n"
                       "Parse error:\n"
                       "{}"
                       ).format(utf8_stdout, utf8_stderr, err)
                return "failed", msg

            if self.config.ast.actual_ast_path is not None:
                with open(self.config.ast.actual_ast_path, "w") as actual_ast_file:
                    actual_ast_file.buffer.write(stdout)

            if self.config.ast.expected_ast_path is not None:
                with open(self.config.ast.expected_ast_path, "r") as expected_ast_file:
                    try:
                        expected_ast_doc = json.loads(expected_ast_file.read())
                    except:
                        msg = ("Parse error:\n"
                               "{}"
                               ).format(self.config.ast.expected_ast_path)
                        return "failed", msg
                    if expected_ast_doc != actual_ast_doc:
                        msg = ("Actual AST does not match the expected AST:\n"
                               "Expected AST:\n"
                               "{}\n"
                               "Actual AST:\n"
                               "{}"
                               ).format(expected_ast_doc, actual_ast_doc)
                        return "failed", msg

        return "ok", None

    def test_ir(self, optimized=False):
        ir_config = self.config.ir_optimized if optimized else self.config.ir
        if ir_config is None or ir_config.hidden:
            return "hidden", None
        elif ir_config.skip:
            return "skipped", None

        compiler_options = [GLOBAL_OPTIONS.o10c_path]
        if optimized:
            compiler_options.append("-o")
        compiler_options += ["--ir", self.config.source_path]

        process = subprocess.Popen(
            compiler_options,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate()
        utf8_stdout = stdout.decode("UTF-8")
        utf8_stderr = stderr.decode("UTF-8")

        if process.returncode != ir_config.expected_return_code:
            msg = ("Unexpected return code. Actual: {}, Expected: {}\n"
                   "stdout:\n"
                   "{}\n"
                   "stderr:\n"
                   "{}"
                   ).format(process.returncode, ir_config.expected_return_code, utf8_stdout, utf8_stderr)
            return "failed", msg

        if process.returncode == 0:
            if ir_config.actual_dot_path is not None:
                with open(ir_config.actual_dot_path, "w") as actual_ir_file:
                    actual_ir_file.buffer.write(stdout)

                if ir_config.actual_png_path is not None and not GLOBAL_OPTIONS.no_dot:
                    # TODO: Pipe to stdin
                    dot_process = subprocess.Popen(
                        [GLOBAL_OPTIONS.dot_path, "-Tpng", ir_config.actual_dot_path, "-o", ir_config.actual_png_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    dot_stdout, dot_stderr = dot_process.communicate()
                    utf8_dot_stdout = dot_stdout.decode("UTF-8")
                    utf8_dot_stderr = dot_stderr.decode("UTF-8")

                    if process.returncode != 0:
                        msg = ("Error while rendering IR with `dot`:\n"
                               "stdout:\n"
                               "{}\n"
                               "stderr:\n"
                               "{}"
                               ).format(utf8_dot_stdout, utf8_dot_stderr)
                        return "failed", msg

        return "ok", None

    def test_run(self, optimized=False):
        run_config = self.config.run_optimized if optimized else self.config.run
        if run_config is None or run_config.hidden:
            return "hidden", None
        elif run_config.skip:
            return "skipped", None

        compiler_process = subprocess.Popen(
            [GLOBAL_OPTIONS.o10c_path, "-co" if optimized else "-c", "--output={}".format(run_config.actual_assembly_path), self.config.source_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = compiler_process.communicate()

        if compiler_process.returncode is not None and compiler_process.returncode != 0:
            msg = ("Compilation failed:\n"
                   "stdout:\n"
                   "{}\n"
                   "stderr:\n"
                   "{}"
                   ).format(stdout.decode("UTF-8"), stderr.decode("UTF-8"))
            return "failed", msg

        compiler_process = subprocess.Popen(
            [GLOBAL_OPTIONS.gcc_path, "-ggdb", "-x", "assembler", "-s", run_config.actual_assembly_path, "-o", run_config.executable_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = compiler_process.communicate()

        if compiler_process.returncode is not None and compiler_process.returncode != 0:
            msg = ("Link failed:\n"
                   "stdout:\n"
                   "{}\n"
                   "stderr:\n"
                   "{}"
                   ).format(stdout.decode("UTF-8"), stderr.decode("UTF-8"))
            return "failed", msg

        process = subprocess.Popen(
            [run_config.executable_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate()
        stdout = stdout.replace(b"\r\n", b"\n")
        stderr = stderr.replace(b"\r\n", b"\n")

        if run_config.actual_stdout_path is not None:
            with open(run_config.actual_stdout_path, "w") as actual_stdout_file:
                actual_stdout_file.buffer.write(stdout)

        if run_config.actual_stderr_path is not None:
            with open(run_config.actual_stderr_path, "w") as actual_stderr_file:
                actual_stderr_file.buffer.write(stderr)

        if run_config.expected_return_code is not None:
            if process.returncode != run_config.expected_return_code:
                msg = ("Unexpected return code. Actual: {}, Expected: {}\n"
                       "stdout:\n"
                       "{}\n"
                       "stderr:\n"
                       "{}"
                       ).format(process.returncode, run_config.expected_return_code, repr(stdout), repr(stderr))
                return "failed", msg

        if run_config.expected_stdout_path is not None:
            try:
                with open(run_config.expected_stdout_path, "rb") as expected_stdout_file:
                    expected_stdout = expected_stdout_file.read()
                    if expected_stdout != stdout:
                        msg = ("Actual STDOUT does not match the expected STDOUT:\n"
                               "Expected:\n"
                               "{}\n"
                               "Actual:\n"
                               "{}"
                               ).format(repr(expected_stdout), repr(stdout))
                        return "failed", msg
            except:
                return "failed", "Unable to read file: {}".format(run_config.expected_stdout_path)

        if run_config.expected_stderr_path is not None:
            try:
                with open(run_config.expected_stderr_path, "rb") as expected_stderr_file:
                    expected_stderr = expected_stderr_file.read()
                    if expected_stderr != stderr:
                        msg = ("Actual STDERR does not match the expected STDERR:\n"
                               "Expected:\n"
                               "{}\n"
                               "Actual:\n"
                               "{}"
                               ).format(repr(expected_stderr), repr(stderr))
                        return "failed", msg
            except:
                return "failed", "Unable to read file: {}".format(run_config.expected_stderr_path)

        return "ok", None


####################################################################################################
# Tests discovery                                                                                  #
####################################################################################################


def dir_content(dir_path):
    """
    Returns a set of directories and a set of other FS nodes
    """
    files = set()
    dirs = set()
    for node_name in os.listdir(dir_path):
        abs_path = os.path.join(dir_path, node_name)
        if os.path.isdir(abs_path):
            dirs.add(abs_path)
        else:
            files.add(abs_path)
    return files, dirs


def discover_tests(tests_dir, recursive=True):
    """
    Yields the test cases in the provided directory
    """
    for fs_node in os.listdir(tests_dir):
        fs_node_path = os.path.join(tests_dir, fs_node)
        if not os.path.isdir(fs_node_path):
            continue
        test_dir_path = fs_node_path
        test_files, test_dirs = dir_content(test_dir_path)
        if os.path.join(test_dir_path, CONFIG_FILE_NAME) in test_files:
            yield TestCase(test_dir_path)
        elif recursive:
            for test_case in discover_tests(test_dir_path, True):
                yield test_case


####################################################################################################
# Test report                                                                                      #
####################################################################################################


class TestReport:
    def __init__(self):
        self.results = []
        self.messages = []
        self.total = 0
        self.skipped = 0
        self.failed = 0
        self.ok = 0

    def add(self, status, full_name, message = None):
        if status == "hidden":
            return

        self.total += 1
        if status == "skipped":
            self.skipped += 1
        elif status == "failed":
            self.failed += 1
        elif status == "ok":
            self.ok += 1
        else:
            raise RuntimeError("Unexpected test status: {}".format(status))

        if message is None:
            result = (status, full_name, None)
            self.results.append(result)
            return result
        else:
            result = (status, full_name, len(self.messages))
            self.results.append(result)
            self.messages.append(message)
            return result

    @staticmethod
    def print_result(result):
        if result is None:
            return
        status, name, msg_id = result
        if status == "skipped":
            status_str = "SKIPPED"
        elif status == "failed":
            status_str = "FAILED "
        elif status == "ok":
            status_str = "OK     "
        else:
            raise RuntimeError("Unexpected test status: {}".format(status))
        if msg_id is None:
            msg_id_str = "       "
        else:
            msg_id_str = "< {0: 3d} >".format(msg_id)
        print("[{}] {} {}".format(status_str, msg_id_str, name))

    def print(self, skip_details=False):
        """
        Print the report
        """
        if not skip_details:
            print("====================================")
            for result in self.results:
                TestReport.print_result(result)

        if len(self.messages) > 0:
            print("====================================")
            print("MESSAGES:")
            for id, message in enumerate(self.messages):
                if id > 0:
                    print("")
                print("< {0: 3d} >".format(id))
                print(message)

        print("====================================")
        print("     ok: {}".format(self.ok))
        print(" failed: {}".format(self.failed))
        if self.skipped > 0:
            print("skipped: {}".format(self.skipped))
        print("  total: {}".format(self.total))


####################################################################################################
# Main                                                                                             #
####################################################################################################

def main():
    args = CLI_PARSER.parse_args()  # type: argparse.Namespace

    GLOBAL_OPTIONS.no_dot = args.no_dot

    test_report = TestReport()

    # Discover and run the tests
    test_suites = list(discover_tests(END_TO_END_ROOT, recursive=True))
    for test_case in sorted(test_suites, key=lambda x: x.dir):
        for name, (status, message) in test_case.test().items():
            full_name = "{} + {}".format(test_case.dir[len(END_TO_END_ROOT):], name)
            TestReport.print_result(test_report.add(status, full_name, message))

    test_report.print(skip_details=True)

    return 0 if test_report.failed == 0 else 1


if __name__ == u'__main__':
    exit(main())
