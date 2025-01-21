from JuniorCode import *
import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
from io import StringIO
from typing import Any, List, Optional, Dict, Union
import queue
import threading

class CustomStringIO(StringIO):
    """Custom StringIO class to capture and redirect stdout to the GUI"""
    def __init__(self, gui):
        super().__init__()
        self.gui = gui
    
    def write(self, text):
        self.gui.update_output(text)

class JuniorCodeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JuniorCode IDE")
        self.root.geometry("800x600")
        
        # Input handling setup
        self.input_queue = queue.Queue()
        self.input_event = threading.Event()
        self.waiting_for_input = False
        
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Create title label
        self.title_label = ttk.Label(
            self.main_container,
            text="JuniorCode IDE",
            font=("Arial", 16, "bold")
        )
        self.title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Create PanedWindow for code and output
        self.paned_window = ttk.PanedWindow(self.main_container, orient=tk.VERTICAL)
        self.paned_window.grid(row=1, column=0, sticky="nsew")
        
        # Create code frame
        self.code_frame = ttk.LabelFrame(self.paned_window, text="Code Editor")
        self.code_frame.grid_rowconfigure(0, weight=1)
        self.code_frame.grid_columnconfigure(0, weight=1)
        self.code_editor = scrolledtext.ScrolledText(
            self.code_frame,
            wrap=tk.WORD,
            width=80,
            height=15,
            font=("Courier New", 12)
        )
        self.code_editor.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create output frame
        self.output_frame = ttk.LabelFrame(self.paned_window, text="Output")
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)
        
        # Create output text
        self.output_text = scrolledtext.ScrolledText(
            self.output_frame,
            wrap=tk.WORD,
            width=80,
            height=10,
            font=("Courier New", 12)
        )
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add frames to PanedWindow
        self.paned_window.add(self.code_frame)
        self.paned_window.add(self.output_frame)
        
        # Create button frame
        self.button_frame = ttk.Frame(self.main_container)
        self.button_frame.grid(row=2, column=0, pady=(10, 0))
        
        # Create Run button
        self.run_button = ttk.Button(
            self.button_frame,
            text="Run Code",
            command=self.run_code
        )
        self.run_button.grid(row=0, column=0, padx=5)
        
        # Create Clear button
        self.clear_button = ttk.Button(
            self.button_frame,
            text="Clear All",
            command=self.clear_all
        )
        self.clear_button.grid(row=0, column=1, padx=5)
        
        # Create example code button
        self.example_button = ttk.Button(
            self.button_frame,
            text="Load Example",
            command=self.load_example
        )
        self.example_button.grid(row=0, column=2, padx=5)
        
        # Create input frame
        self.input_frame = ttk.Frame(self.main_container)
        self.input_frame.grid(row=3, column=0, pady=(10, 0))
        
        # Create input entry
        self.input_entry = ttk.Entry(self.input_frame, width=40)
        self.input_entry.grid(row=0, column=0, padx=5)
        
        # Create submit button
        self.submit_button = ttk.Button(
            self.input_frame,
            text="Submit Input",
            command=self.submit_input,
            state="disabled"
        )
        self.submit_button.grid(row=0, column=1, padx=5)
        
        # Bind enter key to submit input
        self.input_entry.bind("<Return>", lambda e: self.submit_input())
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Custom Interpreter class with GUI input handling
        class GUIInterpreter(Interpreter):
            def __init__(self, gui):
                super().__init__()
                self.gui = gui
                self._stdout = CustomStringIO(gui)
                sys.stdout = self._stdout

            def evaluate(self, node: ASTNode) -> Any:
                if isinstance(node, AskNode):
                    return self.gui.get_input(node.prompt)
                return super().evaluate(node)

            def __del__(self):
                sys.stdout = sys.__stdout__
        
        self.interpreter_class = GUIInterpreter
        
        # Initialize input entry as disabled
        self.input_entry.config(state="disabled")

    def update_output(self, text):
        """Thread-safe method to update the output text widget"""
        self.root.after(0, self._update_output_safe, str(text))

    def _update_output_safe(self, text):
        """Internal method to perform the actual output update"""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)

    def get_input(self, prompt):
        """Get input from the user through the GUI"""
        # Reset input state
        self.input_event.clear()
        
        # Enable input controls on the main thread
        self.root.after(0, self._enable_input_controls, prompt)
        
        # Wait for input
        self.input_event.wait()
        
        # Get and return the result
        return self.input_queue.get()

    def _enable_input_controls(self, prompt):
        """Enable input controls and display prompt"""
        self.update_output(prompt + " ")
        self.waiting_for_input = True
        self.input_entry.config(state="normal")
        self.submit_button.config(state="normal")
        self.input_entry.focus()

    def submit_input(self):
        """Handle input submission"""
        if self.waiting_for_input:
            user_input = self.input_entry.get()
            self.input_queue.put(user_input)
            self.input_entry.delete(0, tk.END)
            self.input_entry.config(state="disabled")
            self.submit_button.config(state="disabled")
            self.waiting_for_input = False
            self.input_event.set()
            self.update_output(user_input + "\n")

    def run_code(self):
        """Execute the code in the editor"""
        # Clear previous output
        self.output_text.delete(1.0, tk.END)
        
        # Get code from editor
        code = self.code_editor.get(1.0, tk.END).strip()
        
        # Disable run button during execution
        self.run_button.config(state="disabled")
        
        def execute():
            try:
                # Create lexer and tokenize the code
                lexer = Lexer(code)
                tokens = lexer.tokenize()
                
                # Create parser and parse the tokens
                parser = Parser(tokens)
                ast = parser.parse()
                
                # Create interpreter and run the code
                interpreter = self.interpreter_class(self)
                interpreter.interpret(ast)
                
            except Exception as e:
                self.update_output(f"Error: {str(e)}\n")
            finally:
                # Re-enable run button after execution
                self.root.after(0, lambda: self.run_button.config(state="normal"))
                # Reset input state if execution ends while waiting for input
                if self.waiting_for_input:
                    self.root.after(0, self._reset_input_state)
        
        # Run code in a separate thread
        threading.Thread(target=execute, daemon=True).start()

    def _reset_input_state(self):
        """Reset the input state and controls"""
        self.waiting_for_input = False
        self.input_entry.config(state="disabled")
        self.submit_button.config(state="disabled")
        self.input_event.set()

    def clear_all(self):
        """Clear all text in the editor and output"""
        self.code_editor.delete(1.0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.input_entry.delete(0, tk.END)

    def load_example(self):
        """Load example code into the editor"""
        example_code = """var name = ask "What's your name?"
show "Hello, " + name + "!"

var age = 20
if age >= 18 {
    show "You are an adult!"
} else {
    show "You are still growing up!"
}

show "Counting from 1 to 5:"
repeat i 1 to 5 {
    show i
}"""
        self.code_editor.delete(1.0, tk.END)
        self.code_editor.insert(1.0, example_code)

    def on_closing(self):
        """Handle window closing event"""
        # Ensure any waiting input operations are unblocked
        if self.waiting_for_input:
            self._reset_input_state()
        self.root.destroy()

def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = JuniorCodeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()