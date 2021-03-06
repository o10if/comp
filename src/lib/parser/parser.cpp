#include <cerrno>
#include <iostream>
#include <string>

#include <comp/ast.h>
#include <comp/parser/parser_config.h>
#include <comp/utils.h>

// Generated with bison by CMake (parser.tab.hpp is in the build directory)
#include "parser.tab.hpp"
// Generated with flex by CMake (lexer.yy.h is in the build directory)
#include "lexer.yy.h"

void yyerror(
  YYLTYPE *locp,
  yyscan_t scanner,
  comp::ast::Program *res,
  const char *msg
) {
  UNUSED(scanner);
  UNUSED(res);
  throw comp::SyntaxException(
    msg,
    std::make_shared<comp::ast::SourceLocation>(
      comp::ast::Position(
        locp->first_index,
        locp->first_line,
        locp->first_column),
      comp::ast::Position(
        locp->last_index,
        locp->last_line,
        locp->last_column)));
}

namespace comp {
namespace parser {
std::shared_ptr<comp::ast::Program> parse(const std::string &input) {
  yyscan_t scanner;
  if (yylex_init(&scanner)) {
    switch (errno) {
      case ENOMEM:
        throw Exception(
          "Failed to initialize parser: Could not allocate memory");
      case EINVAL:
        throw Exception("Failed to initialize parser: Invalid scanner");
      default:
        throw Exception("Failed to initialize parser: Unknown error");
    }
  }

  comp::ast::Program *root = nullptr;
  yy_scan_string(input.c_str(), scanner);
  yyparse(scanner, root);
  yylex_destroy(scanner);
  return std::shared_ptr<comp::ast::Program>(root);
}
}  // namespace parser
}  // namespace comp
