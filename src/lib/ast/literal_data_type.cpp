#include <comp/ast.h>

namespace comp {
namespace ast {
std::unique_ptr<LiteralDataType> LiteralDataType::Create(
  std::shared_ptr<Identifier> identifier,
  std::shared_ptr<SourceLocation> location
) {
  return std::unique_ptr<LiteralDataType>();
}

LiteralDataType::LiteralDataType(
  std::shared_ptr<Identifier> identifier,
  std::shared_ptr<SourceLocation> location
) :
  DataType(Node::Type::LiteralDataType, location),
  identifier(identifier) {
}

LiteralDataType::~LiteralDataType() {
}
}
}
