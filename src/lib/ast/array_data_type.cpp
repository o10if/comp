#include <comp/ast.h>

namespace comp {
namespace ast {
ArrayDataType::ArrayDataType(
  std::shared_ptr<DataType> itemType,
  std::shared_ptr<SourceLocation> location
) :
  DataType(Node::Type::ArrayDataType, location),
  itemType(itemType) {
}

ArrayDataType::~ArrayDataType() {
}
}
}