# Junior Code

## Introduction

This report provides a comprehensive overview of the Junior Code compiler project, including its design, implementation, and testing. Junior Code features a custom programming language with a graphical interface, enabling users to write, execute, and test code in a user-friendly environment.

## Language Design and Features

The Junior Code language is simple yet expressive, catering to beginners. Its key features include:

### Grammar and Syntax

- **Printing**: Output text or variable values using the `show` keyword.
  ```juniorcode
  show "Hello, World!"
  show variable_name
  ```

- **Variable Declaration**: Declare variables with the `var` keyword.
  ```juniorcode
  var x = 10
  ```

- **Input Handling**: Prompt user input using the `ask` keyword.
  ```juniorcode
  var name = ask "What is your name?"
  ```

- **Conditionals**: Implement branching logic with `if` and `else`.
  ```juniorcode
  if condition {
      # code block
  } else {
      # code block
  }
  ```

- **Loops**: Use the `repeat` keyword for iteration over a range.
  ```juniorcode
  repeat i 1 to 10 {
      show i
  }
  ```

## Components of the Compiler

### 1. Lexer (Tokenizer)

The Lexer scans the input source code and breaks it into tokens, categorizing them into keywords, operators, identifiers, and literals.

- **Keywords**: `show`, `var`, `ask`, `if`, `else`, `repeat`, `to`.
- **Operators**: `=`, `+`, `-`, `*`, `/`, `<`, `>`.
- **Output**: Tokens are structured objects containing the token type, value, and position (line and column).

### 2. Parser

The Parser validates the sequence of tokens against the language grammar, constructing an Abstract Syntax Tree (AST) for syntactically correct code.

### 3. Interpreter

The Interpreter executes the instructions defined by the AST, performing actions like:

- Variable initialization and assignment.
- Loop execution.
- Conditional branching.
- Displaying output.

## Graphical User Interface (GUI)

The GUI, built with Tkinter, offers:

- A code editor for users to write Junior Code programs.
- A button to execute the code.
- An output area displaying execution results or errors.

### Implementation Highlights

- **Output Redirection**: Captures the standard output (stdout) using a custom StringIO class to display results in the GUI.
- **Threading**: Ensures smooth interaction by running the compiler in a separate thread.
- **Error Handling**: Provides real-time feedback on syntax or runtime errors.

## Test Cases and Results

The compiler was tested with various programs, validating its correctness and functionality. Example test cases include:

- **Test Case 1**: Multiplication Table
- **Test Case 2**: Sum of First 5 Numbers
- **Test Case 3**: Factorial Calculation

## Usage Instructions

### Writing Code

1. Open the GUI application.
2. Write Junior Code programs in the provided text area.
3. Click the "Run" button to run the program.
4. View results or errors in the output section.

### Supported Features

- Arithmetic operations: `+`, `-`, `*`, `/`.
- Looping constructs: `repeat` for fixed-range loops.
- Conditionals: `if-else` for decision-making.

## Conclusion

The Junior Code compiler is a user-friendly tool designed for learning and experimentation. Its integration with a GUI enhances accessibility for beginners, while its robust implementation ensures functionality and correctness.

---

Feel free to contribute or share feedback to improve Junior Code!
