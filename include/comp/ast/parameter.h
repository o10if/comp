#pragma once

#include "comp/ast/data_type.h"
#include "comp/ast/declaration.h"
#include "comp/ast/identifier.h"

namespace comp {
namespace ast {
struct Parameter final : public Node {
  static std::unique_ptr<Parameter> Create(
    std::shared_ptr<DataType> data_type,
    std::shared_ptr<Identifier> identifier,
    std::shared_ptr<SourceLocation> location = nullptr);

  Parameter(
    std::shared_ptr<DataType> data_type,
    std::shared_ptr<Identifier> identifier,
    std::shared_ptr<SourceLocation> location = nullptr);

  ~Parameter();

  const std::shared_ptr<DataType> data_type;
  const std::shared_ptr<Identifier> identifier;
};
}  // namespace ast
}  // namespace comp
