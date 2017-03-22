#include <comp/ast/array_declarator.h>

namespace comp {
namespace ast {
std::unique_ptr<ArrayDeclarator> ArrayDeclarator::Create(
  std::shared_ptr<Declarator> declarator,
  std::shared_ptr<RExpression> size,
  std::shared_ptr<SourceLocation> location
) {
  return std::unique_ptr<ArrayDeclarator>(
    new ArrayDeclarator(declarator, size, location));
}

ArrayDeclarator::ArrayDeclarator(
  std::shared_ptr<Declarator> declarator,
  std::shared_ptr<RExpression> size,
  std::shared_ptr<SourceLocation> location
) :
  Declarator(Type::ArrayDeclarator, location),
  declarator_(declarator),
  size_(size) {
}

ArrayDeclarator::~ArrayDeclarator() {
}

std::string ArrayDeclarator::GetName() {
  return declarator_->GetName();
}
}  // namespace ast
}  // namespace comp
