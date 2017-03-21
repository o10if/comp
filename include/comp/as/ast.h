#include "comp/as/ast/align_directive.h"
#include "comp/as/ast/asciz_directive.h"
#include "comp/as/ast/big_integer_literal.h"
#include "comp/as/ast/binary_expression.h"
#include "comp/as/ast/cfi_startproc_directive.h"
#include "comp/as/ast/cfi_endproc_directive.h"
#include "comp/as/ast/current_address.h"
#include "comp/as/ast/directive.h"
#include "comp/as/ast/empty_statement.h"
#include "comp/as/ast/expression.h"
#include "comp/as/ast/global_directive.h"
#include "comp/as/ast/global_symbol.h"
#include "comp/as/ast/immediate_operand.h"
#include "comp/as/ast/instruction.h"
#include "comp/as/ast/integer_literal.h"
#include "comp/as/ast/literal.h"
#include "comp/as/ast/local_symbol.h"
#include "comp/as/ast/memory_reference.h"
#include "comp/as/ast/mnemonic.h"
#include "comp/as/ast/node.h"
#include "comp/as/ast/operand.h"
#include "comp/as/ast/program.h"
#include "comp/as/ast/quad_directive.h"
#include "comp/as/ast/register_operand.h"
#include "comp/as/ast/simple_operand.h"
#include "comp/as/ast/size_directive.h"
#include "comp/as/ast/statement.h"
#include "comp/as/ast/symbol.h"
#include "comp/as/ast/text_directive.h"
#include "comp/as/ast/type_directive.h"