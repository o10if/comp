#include "gtest/gtest.h"
#include <comp/parser.h>
#include <comp/eval.h>
#include <cstddef>
#include <sstream>
#include <iomanip>

TEST(comp__parser__parser, BinaryExpression) {
  std::shared_ptr<comp::ast::RExpression> expr = comp::parser::parse("123+456");
  EXPECT_EQ(579, comp::eval::eval_expression(*expr));
}

TEST(comp__parser__parser, CharLiteralFromSourceChar) {
  std::shared_ptr<comp::ast::RExpression> expr = comp::parser::parse("'a'");
  EXPECT_EQ(comp::ast::Node::Type::Uint8Literal, expr->node_type);
  std::shared_ptr<comp::ast::Uint8Literal> uint8Literal = std::static_pointer_cast<comp::ast::Uint8Literal>(expr);
  EXPECT_EQ('a', uint8Literal->value);
}

TEST(comp__parser__parser, CharLiteralFromOctalEscape) {
  uint8_t i = 0;
  do {
    std::stringstream input_stream;
    input_stream << std::setbase(8) << "'\\" << uint64_t(i) << "'";
    std::string input(input_stream.str());
    std::shared_ptr<comp::ast::RExpression> expr = comp::parser::parse(input);
    EXPECT_EQ(comp::ast::Node::Type::Uint8Literal, expr->node_type);
    std::shared_ptr<comp::ast::Uint8Literal> uint8Literal = std::static_pointer_cast<comp::ast::Uint8Literal>(expr);
    EXPECT_EQ(i, uint8Literal->value);
  } while (i++ < 255);
}

TEST(comp__parser__parser, CharLiteralFromHexEscape) {
  uint8_t i = 0;
  do {
    std::stringstream input_stream;
    input_stream << std::setbase(16) << "'\\x" << uint64_t(i) << "'";
    std::string input(input_stream.str());
    std::shared_ptr<comp::ast::RExpression> expr = comp::parser::parse(input);
    EXPECT_EQ(comp::ast::Node::Type::Uint8Literal, expr->node_type);
    std::shared_ptr<comp::ast::Uint8Literal> uint8Literal = std::static_pointer_cast<comp::ast::Uint8Literal>(expr);
    EXPECT_EQ(i, uint8Literal->value);
  } while (i++ < 255);
}

TEST(comp__parser__parser, CharLiteralFromEscapeSourceChar) {
  std::shared_ptr<comp::ast::RExpression> expr = comp::parser::parse("'\\a'");
  EXPECT_EQ(comp::ast::Node::Type::Uint8Literal, expr->node_type);
  std::shared_ptr<comp::ast::Uint8Literal> uint8Literal = std::static_pointer_cast<comp::ast::Uint8Literal>(expr);
  EXPECT_EQ(0x07, uint8Literal->value);
}

TEST(comp__parser__parser, CharLiteralFromEscapeSourceChar2) {
  std::shared_ptr<comp::ast::RExpression> expr = comp::parser::parse("'\\\"'");
  EXPECT_EQ(comp::ast::Node::Type::Uint8Literal, expr->node_type);
  std::shared_ptr<comp::ast::Uint8Literal> uint8Literal = std::static_pointer_cast<comp::ast::Uint8Literal>(expr);
  EXPECT_EQ(0x22, uint8Literal->value);
}

TEST(comp__parser__parser, CharLiteralFromEscapeSourceChar3) {
  std::shared_ptr<comp::ast::RExpression> expr = comp::parser::parse("'\\\''");
  EXPECT_EQ(comp::ast::Node::Type::Uint8Literal, expr->node_type);
  std::shared_ptr<comp::ast::Uint8Literal> uint8Literal = std::static_pointer_cast<comp::ast::Uint8Literal>(expr);
  EXPECT_EQ(0x27, uint8Literal->value);
}

TEST(comp__parser__parser, CharLiteralFromEscapeSourceChar4) {
  std::shared_ptr<comp::ast::RExpression> expr = comp::parser::parse("'\\?'");
  EXPECT_EQ(comp::ast::Node::Type::Uint8Literal, expr->node_type);
  std::shared_ptr<comp::ast::Uint8Literal> uint8Literal = std::static_pointer_cast<comp::ast::Uint8Literal>(expr);
  EXPECT_EQ(0x3f, uint8Literal->value);
}

TEST(comp__parser__parser, CharLiteralFromEscapeSourceChar5) {
  std::shared_ptr<comp::ast::RExpression> expr = comp::parser::parse("'\\\\'");
  EXPECT_EQ(comp::ast::Node::Type::Uint8Literal, expr->node_type);
  std::shared_ptr<comp::ast::Uint8Literal> uint8Literal = std::static_pointer_cast<comp::ast::Uint8Literal>(expr);
  EXPECT_EQ(0x5c, uint8Literal->value);
}