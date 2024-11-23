import pygame
import serial
import time

# Initialize Pygame
pygame.init()

# Set up the display (increased height for larger sequence display)
window_size = (900, 500)  # Adjusted window size for larger sequence display
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Touch Sensor Color Boxes for A1, A2, and A3")

# Define colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
A1_color = RED
A2_color = RED
A3_color = RED

# Set thresholds for detecting the touch cycle for the sensors
A1_downward_threshold = 400  # Value when A1 sensor is pressed
A1_upward_threshold = 650    # Value when A1 sensor is released

A2_downward_threshold = 350  # Value when A2 sensor is pressed
A2_upward_threshold = 700   # Value when A2 sensor is released

A3_downward_threshold = 350  # Value when A3 sensor is pressed
A3_upward_threshold = 700   # Value when A3 sensor is released

# State to track if each sensor is in a touch cycle
A1_in_touch_cycle = False
A2_in_touch_cycle = False
A3_in_touch_cycle = False

# Font settings
font = pygame.font.SysFont(None, 55)  # Font size 55 for numbers inside the boxes
large_font = pygame.font.SysFont(None, 70)  # Larger font for the sequence display

# Open serial port (replace 'COM3' with your port)
ser = serial.Serial('COM9', 19200)
time.sleep(2)  # Wait for the serial connection to initialize

# List to keep track of the sequence of touches
touch_sequence = ""

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read data from Arduino
    if ser.in_waiting > 0:
        data = ser.readline()

        try:
            # Try to decode the data using UTF-8
            data_decoded = data.decode('utf-8').strip()
        except UnicodeDecodeError:
            # If decoding fails, skip this iteration
            continue

        # Check if data is not empty
        if data_decoded:
            try:
                # Assuming Arduino sends values in the format "A1_value,A2_value,A3_value"
                A1_value, A2_value, A3_value = map(int, data_decoded.split(','))
            except ValueError:
                # If conversion to int or split fails, skip this iteration
                continue

            # Handle A1 sensor
            if not A1_in_touch_cycle and A1_value < A1_downward_threshold:
                A1_color = GREEN  # Turn the A1 box green when touched
                A1_in_touch_cycle = True  # Mark the start of a touch cycle for A1
                touch_sequence += '1'  # Add '1' to the touch sequence

            if A1_in_touch_cycle and A1_value > A1_upward_threshold:
                A1_color = RED  # Turn the A1 box red when released
                A1_in_touch_cycle = False  # End the touch cycle for A1

            # Handle A2 sensor
            if not A2_in_touch_cycle and A2_value < A2_downward_threshold:
                A2_color = GREEN  # Turn the A2 box green when touched
                A2_in_touch_cycle = True  # Mark the start of a touch cycle for A2
                touch_sequence += '2'  # Add '2' to the touch sequence

            if A2_in_touch_cycle and A2_value > A2_upward_threshold:
                A2_color = RED  # Turn the A2 box red when released
                A2_in_touch_cycle = False  # End the touch cycle for A2

            # Handle A3 sensor
            if not A3_in_touch_cycle and A3_value < A3_downward_threshold:
                A3_color = GREEN  # Turn the A3 box green when touched
                A3_in_touch_cycle = True  # Mark the start of a touch cycle for A3
                touch_sequence += '3'  # Add '3' to the touch sequence

            if A3_in_touch_cycle and A3_value > A3_upward_threshold:
                A3_color = RED  # Turn the A3 box red when released
                A3_in_touch_cycle = False  # End the touch cycle for A3

    # Fill the window with a white background
    window.fill(WHITE)

    # Draw the box for A1 (left side, smaller and higher)
    pygame.draw.rect(window, A1_color, (150, 50, 150, 150))

    # Draw the box for A2 (middle, smaller and higher)
    pygame.draw.rect(window, A2_color, (375, 50, 150, 150))

    # Draw the box for A3 (right side, smaller and higher)
    pygame.draw.rect(window, A3_color, (600, 50, 150, 150))

    # Render text "1" inside the first box (A1)
    text_A1 = font.render('1', True, WHITE)
    window.blit(text_A1, (210, 110))  # Position the text inside the first box

    # Render text "2" inside the second box (A2)
    text_A2 = font.render('2', True, WHITE)
    window.blit(text_A2, (435, 110))  # Position the text inside the second box

    # Render text "3" inside the third box (A3)
    text_A3 = font.render('3', True, WHITE)
    window.blit(text_A3, (660, 110))  # Position the text inside the third box

    # Render "Final Sequence" label in the large display box
    final_sequence_label = large_font.render("Final Sequence:", True, BLACK)
    window.blit(final_sequence_label, (150, 250))  # Position for "Final Sequence"

    # Render the actual sequence of touches
    sequence_text = large_font.render(touch_sequence, True, BLACK)
    window.blit(sequence_text, (150, 350))  # Position for sequence text below the label

    # Update the display
    pygame.display.update()

# Close the serial port and Pygame
ser.close()
pygame.quit()
