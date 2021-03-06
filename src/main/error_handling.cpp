#include "error_handling.h"

#include <iostream>
#include <vector>

#include <comp/ast/position.h>

static const unsigned int TAB_WIDTH = 8;

void PrintException(const std::exception &exception) {
  std::cerr << "o10c: fatal error: " << exception.what();
  std::cerr << std::endl;
}

void PrintSyntaxException(
  const comp::CompilationException &exception,
  const std::string &content,
  const std::string &filename) {
  std::shared_ptr<comp::ast::SourceLocation> l = exception.GetLocation();

  // Display the error and its message
  std::cerr << filename << ':';
  std::cerr << l->start.line + 1 << ':' << l->start.column + 1 << ':';
  std::cerr << " error: " << exception.what() << std::endl;

  // Display each line, underling the relevant parts
  size_t idx = GetLineStartFromIndex(l->start.index, content);
  for (size_t line = l->start.line; line <= l->end.line; line++) {
    std::vector<char> underline;

    // Display the line
    unsigned int display_col = 1;  // The current column, as displayed on-screen
    for (size_t line_end_idx = GetLineEndFromIndex(idx, content);
         idx < line_end_idx; idx++) {
      unsigned int width = 1;
      char c = content[idx];
      if (c == '\t') {
        width = -display_col % TAB_WIDTH + 1;
        c = ' ';
      }

      for (unsigned int i = 0; i < width; i++) {
        std::cerr << c;
        if (idx < l->start.index) {
          underline.push_back(' ');
        } else if (idx < l->end.index) {
          underline.push_back('^');
        }
      }
      display_col += width;
    }
    idx++;
    std::cerr << std::endl;

    // Display the underline
    for (char &c : underline) {
      std::cerr << c;
    }
    std::cerr << std::endl;
  }
}

size_t GetLineStartFromIndex(size_t start_idx, const std::string &content) {
  size_t idx = start_idx;
  while (idx-- > 0 && content[idx] != '\n') {
  }
  return idx + 1;  // Shift back to the line's first character
}

size_t GetLineEndFromIndex(size_t start_idx, const std::string &content) {
  size_t idx = start_idx;
  while (content[idx++] != '\n' && idx < content.size()) {
  }
  return idx - 1;  // Remove the newline
}
