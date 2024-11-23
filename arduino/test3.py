import tkinter as tk
from tkinter import messagebox

# Configuration Variables
MAIN_WINDOW_WIDTH = 700
MAIN_WINDOW_HEIGHT = 700
BUTTON_WIDTH = 10
BUTTON_HEIGHT = 3
BUTTON_FONT = ('Arial', 16)
BUTTON_PADX = 10
BUTTON_PADY = 10
INPUT_WINDOW_WIDTH = 300
INPUT_WINDOW_HEIGHT = 150
INPUT_WINDOW_X_OFFSET = MAIN_WINDOW_WIDTH+200
INPUT_WINDOW_Y_OFFSET = 150
ENTRY_FONT = ('Arial', 14)

# Custom Row Configurations (Dynamic row and element count)
# You can change this list to have as many rows as you want with as many elements as needed.
row_config = [2, 1, 4, 2]  # Example row configuration

# Generate a matrix based on the custom row configuration
def generate_matrix(row_config):
    current_number = 1
    matrix = []
    for num_elements in row_config:
        row = list(range(current_number, current_number + num_elements))
        matrix.append(row)
        current_number += num_elements
    return matrix

# Store the current state of the buttons (whether they are marked yellow or not)
marked_numbers = set()

# Function to highlight the number entered by the user and clear the input box for the next number
def highlight_number(event=None):
    try:
        # Get user input, ensure it's between 1 and the total number of elements
        number = int(entry.get())
        if 1 <= number <= sum(row_config):  # Ensure number is within the range of total elements
            # Calculate row and column in the user-defined matrix
            found = False
            for row_idx, row in enumerate(matrix_structure):
                if number in row:
                    col_idx = row.index(number)
                    # If the button has already been marked yellow, show a message and turn it red temporarily
                    if number in marked_numbers:
                        buttons[row_idx][col_idx].config(bg="red")
                        # Display the message
                        messagebox.showinfo("Already Marked", "This number is already marked.")
                        # After the message box is dismissed, reset the color back to yellow
                        root.after(100, reset_red_color, row_idx, col_idx)
                    else:
                        # Mark the button as yellow and add it to the set of marked numbers
                        buttons[row_idx][col_idx].config(bg="yellow")
                        marked_numbers.add(number)
                    found = True
                    break

            if not found:
                messagebox.showwarning("Invalid Input", "Number not found in the matrix.")
            
            # Clear the input box for the next number
            entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Invalid Input", f"Please enter a number between 1 and {sum(row_config)}.")
    except ValueError:
        messagebox.showwarning("Invalid Input", "Please enter a valid integer.")

# Function to reset red-colored buttons back to yellow
def reset_red_color(row, col):
    buttons[row][col].config(bg="yellow")

# Create the main window for the matrix
root = tk.Tk()
root.title("User-Defined Matrix")

# Generate the matrix structure with numbers based on custom row configuration
matrix_structure = generate_matrix(row_config)

# Set the size of the matrix window (using the variables)
root.geometry(f"{MAIN_WINDOW_WIDTH}x{MAIN_WINDOW_HEIGHT}")  # Width x Height

# Create a frame for the matrix
matrix_frame = tk.Frame(root)
matrix_frame.grid(row=0, column=0, padx=10, pady=10)

# Create the matrix with buttons (with numbers 1 to N)
buttons = []
for i, row in enumerate(matrix_structure):
    row_buttons = []
    for j, element in enumerate(row):
        button = tk.Button(matrix_frame, text=str(element), width=BUTTON_WIDTH, height=BUTTON_HEIGHT, font=BUTTON_FONT)  # Use variables for size and font
        button.grid(row=i, column=j, padx=BUTTON_PADX, pady=BUTTON_PADY)  # Padding between buttons
        row_buttons.append(button)
    buttons.append(row_buttons)

# Create the input window to enter a number between 1 and NUM_ROWS * NUM_COLUMNS
input_window = tk.Toplevel(root)
input_window.title("Enter a Number")

# Set the size of the input window and position it to the right of the main window (using variables)
input_window.geometry(f"{INPUT_WINDOW_WIDTH}x{INPUT_WINDOW_HEIGHT}+{INPUT_WINDOW_X_OFFSET}+{INPUT_WINDOW_Y_OFFSET}")  # Width x Height + X Offset + Y Offset

# Create an input label and entry field
input_label = tk.Label(input_window, text=f"Enter a number between 1 and {sum(row_config)}:", font=ENTRY_FONT)
input_label.pack(padx=10, pady=10)

entry = tk.Entry(input_window, font=ENTRY_FONT)
entry.pack(padx=10, pady=10)

# Bind the Enter key to trigger the submit function
entry.bind("<Return>", highlight_number)

# Create a button to submit the number and highlight it in the matrix
submit_button = tk.Button(input_window, text="Submit", command=highlight_number)
submit_button.pack(padx=10, pady=10)

# Run the Tkinter event loop
root.mainloop()
