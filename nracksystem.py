import pygame
import serial
import time

# Initialize Pygame
pygame.init()

# Set up the display
window_size = (1400, 700)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Touch Sensor Color Boxes")

# Define colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Variables to track rows and boxes
rows = []  # Number of sensors (boxes) per row
current_colors = []  # Colors of the boxes
in_touch_cycle = []  # Tracks if a box is in a touch cycle

# Dynamic thresholds for sensors (default values)
downward_peak_threshold = []
upward_peak_threshold = []

# Cumulative input records for each row
input_records = []

# Open serial port (replace 'COM9' with your port)
ser = serial.Serial('COM9', 19200)
time.sleep(2)  # Wait for the serial connection to initialize

# User input variables
user_text_row = ""
user_text_quantity = ""
row_input_active = True  # To track if the user is typing the row number
quantity_input_active = False  # To track if the user is typing the quantity input
input_box_row = pygame.Rect(1000, 100, 300, 50)
input_box_quantity = pygame.Rect(1000, 200, 300, 50)
font = pygame.font.Font(None, 36)

# Error message handling
error_message = ""  # Stores the error message to display
error_display_time = 0  # Timer for how long the error message is shown

# Predefined array of rack labels
racks = ["Orange", "Apple", "Cake", "Biscuit", "Noodles"]

# Function to dynamically initialize thresholds for all sensors
def initialize_thresholds(total_boxes):
    global downward_peak_threshold, upward_peak_threshold, input_records
    downward_peak_threshold = [100,100,100] 
    upward_peak_threshold = [900,900,900]
    input_records = [0] * len(rows)  # Reset input records for all rows

# Function to draw the input boxes
def draw_input_box():
    # Row input box
    pygame.draw.rect(window, (255, 255, 255), input_box_row)
    pygame.draw.rect(window, (0, 0, 0), input_box_row, 2)  # Border
    text_surface_row = font.render("Item: " + user_text_row, True, (0, 0, 0))
    window.blit(text_surface_row, (input_box_row.x + 10, input_box_row.y + 10))

    # Quantity input box
    pygame.draw.rect(window, (255, 255, 255), input_box_quantity)
    pygame.draw.rect(window, (0, 0, 0), input_box_quantity, 2)  # Border
    text_surface_quantity = font.render("Quantity: " + user_text_quantity, True, (0, 0, 0))
    window.blit(text_surface_quantity, (input_box_quantity.x + 10, input_box_quantity.y + 10))

    # Display the error message (if any)
    if error_message:
        error_surface = font.render(error_message, True, (255, 0, 0))
        window.blit(error_surface, (800, 500))

# Function to reset boxes in the selected row based on user input
def reset_boxes_in_row(row_number, quantity):
    global current_colors, input_records
    row_start_idx = sum(rows[:row_number - 1])  # Start index for the row
    row_end_idx = row_start_idx + rows[row_number - 1]  # End index for the row

    # Validate quantity (ensure it's within bounds for the row)
    if quantity > rows[row_number - 1]:
        handle_invalid_number_input("Quantity exceeds the number of boxes in the row.")
        return

    # Increment the cumulative input record for the row
    input_records[row_number - 1] += quantity

    reset_count = 0
    for i in range(row_start_idx, row_end_idx):
        # Reset as many boxes as possible, up to the input quantity
        if current_colors[i] == YELLOW and reset_count < quantity:
            current_colors[i] = RED
            reset_count += 1

    # Notify if fewer boxes were actually reset
    if reset_count < quantity:
        print(f"Warning: Only {reset_count} boxes were reset in row {row_number}.")

# Function to process grouped sensor data
def process_grouped_sensor_data(grouped_data):
    global rows, current_colors, in_touch_cycle
    rows = [len(group.split(',')) for group in grouped_data]  # Determine number of sensors per group

    # Initialize color and cycle tracking arrays based on total boxes
    total_boxes = sum(rows)
    if len(current_colors) != total_boxes:
        current_colors = [RED] * total_boxes
        in_touch_cycle = [False] * total_boxes
        initialize_thresholds(total_boxes)

    # Parse and process sensor data for each box
    for row_idx, group in enumerate(grouped_data):
        sensor_values = list(map(int, group.split(',')))
        row_start_idx = sum(rows[:row_idx])
        for i, sensor_value in enumerate(sensor_values):
            box_idx = row_start_idx + i
            # Process thresholds
            if not in_touch_cycle[box_idx] and sensor_value < downward_peak_threshold[box_idx]:
                current_colors[box_idx] = GREEN
                in_touch_cycle[box_idx] = True
            elif in_touch_cycle[box_idx] and sensor_value > upward_peak_threshold[box_idx]:
                current_colors[box_idx] = YELLOW
                in_touch_cycle[box_idx] = False

# Function to display records of current and cumulative states
def display_records():
    y_offset = 550
    x_left = 50
    x_right = 800

    # Function to display the table
def display_table():
    x_left = 50  # Left margin for the table
    x_right = 600  # Right margin for the "Billed" column
    y_offset = 400  # Y-position of the first row of the table
    column_width = 150  # Column width

    # Header row
    headers = ["No.", "Item", "Handled", "Empty", "Billed"]
    for col_idx, header in enumerate(headers):
        header_text = font.render(header, True, (0, 0, 0))
        window.blit(header_text, (x_left + col_idx * column_width, y_offset))

    # Data rows
    y_offset += 40  # Space after the header
    for row_idx in range(len(rows)):
        row_start_idx = sum(rows[:row_idx])
        yellow_count = sum(1 for i in range(row_start_idx, row_start_idx + rows[row_idx]) if current_colors[i] == YELLOW)
        red_count = sum(1 for i in range(row_start_idx, row_start_idx + rows[row_idx]) if current_colors[i] == RED)
        
        # Calculate the cumulative billed
        billed_count = input_records[row_idx]

        # Prepare the row data
        row_data = [
            f"{row_idx + 1}",  # Row number
            racks[row_idx % len(racks)],  # Rack label (e.g., "orange", "apple")
            str(yellow_count),  # Handled (YELLOW count)
            str(red_count),  # Empty (RED count)
            str(billed_count),  # Billed (cumulative input count)
        ]

        # Display the row data
        for col_idx, data in enumerate(row_data):
            row_text = font.render(data, True, (0, 0, 0))
            window.blit(row_text, (x_left + col_idx * column_width, y_offset))

        y_offset += 40  # Space for the next row

# Handle invalid number input
def handle_invalid_number_input(message):
    global error_message, error_display_time
    error_message = message
    error_display_time = pygame.time.get_ticks() + 2000  # Show the message for 2 seconds

# Main loop
running = True
while running:
    current_time = pygame.time.get_ticks()
    if error_message and current_time > error_display_time:
        error_message = ""  # Clear the error message after the timer expires

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle text input for row and quantity
        if event.type == pygame.KEYDOWN:
            if row_input_active:
                if event.key == pygame.K_RETURN:
                    try:
                        row_number = int(user_text_row)
                        if 1 <= row_number <= len(rows):  # Check valid row number
                            quantity_input_active = True
                            row_input_active = False
                            user_text_quantity = ""  # Reset quantity text box
                        else:
                            handle_invalid_number_input("Invalid row number.")
                    except ValueError:
                        handle_invalid_number_input("Invalid input. Enter a number.")
                elif event.key == pygame.K_BACKSPACE:
                    user_text_row = user_text_row[:-1]
                else:
                    user_text_row += event.unicode

            elif quantity_input_active:
                if event.key == pygame.K_RETURN:
                    try:
                        quantity = int(user_text_quantity)
                        reset_boxes_in_row(int(user_text_row), quantity)
                        quantity_input_active = False
                        row_input_active = True
                        user_text_row = ""
                        user_text_quantity = ""
                    except ValueError:
                        handle_invalid_number_input("Invalid input. Enter a number.")
                elif event.key == pygame.K_BACKSPACE:
                    user_text_quantity = user_text_quantity[:-1]
                else:
                    user_text_quantity += event.unicode

    # Read data from Arduino
    if ser.in_waiting > 0:
        data = ser.readline()
        try:
            data_decoded = data.decode('utf-8').strip()
            grouped_data = data_decoded.split(';')
            process_grouped_sensor_data(grouped_data)
        except (UnicodeDecodeError, ValueError):
            continue

    # Fill the window with a white background
    window.fill((255, 255, 255))

    # Draw the boxes based on the row configuration
    x_offset = 200
    y_offset = 50
    box_width = 50
    box_height = 50
    for row_idx, row in enumerate(rows):
        row_start_idx = sum(rows[:row_idx])
        for box_idx in range(row):
            idx = row_start_idx + box_idx
            pygame.draw.rect(window, current_colors[idx],
                             (x_offset + box_idx * (box_width + 10),
                              y_offset + row_idx * (box_height + 10),
                              box_width, box_height))
         # Draw the row number on the left side of each row
        rack_label = racks[row_idx % len(racks)]  # This cycles through the racks array
        row_label = font.render(f"{row_idx + 1}: {rack_label}", True, (0, 0, 0))
        window.blit(row_label, (x_offset - 150, y_offset + row_idx * (box_height + 10)))

    # Draw input boxes and display records
    draw_input_box()
    display_records()

    # Update the display
    #pygame.display.flip()

    # Display the table
    display_table()

    # Update the display
    pygame.display.update()

# Quit Pygame and close serial
pygame.quit()
ser.close()
