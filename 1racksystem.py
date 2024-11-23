import pygame
import serial
import time

# Initialize Pygame
pygame.init()

# Set up the display
window_size = (400, 400)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Touch Sensor Color Box")

# Define colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
current_color = RED

# Set thresholds for detecting the touch cycle
downward_peak_threshold = 100  # Value when the sensor is pressed
upward_peak_threshold = 601  # Value when the sensor is released

# State to track if the sensor is in a touch cycle
in_touch_cycle = False

# Open serial port (replace 'COM9' with your port)
ser = serial.Serial('COM9', 19200)
time.sleep(2)  # Wait for the serial connection to initialize

# User input variables
user_number = 0
input_active = True
input_box = pygame.Rect(100, 300, 200, 50)
font = pygame.font.Font(None, 36)
user_text = ""

# Function to draw the input box
def draw_input_box():
    pygame.draw.rect(window, (255, 255, 255), input_box)
    pygame.draw.rect(window, (0, 0, 0), input_box, 2)  # Border
    text_surface = font.render(user_text, True, (0, 0, 0))
    window.blit(text_surface, (input_box.x + 10, input_box.y + 10))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if input_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        user_number = int(user_text)
                        if user_number == 1:
                            # Reset state when user enters 1
                            current_color = RED
                            in_touch_cycle = False
                            print("System reset. Waiting for Arduino data...")
                        else:
                            print(f"Invalid input: {user_number}")
                    except ValueError:
                        print("Invalid input: Not a number")
                    user_text = ""  # Clear the input field
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode

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
                sense_value = int(data_decoded)
            except ValueError:
                # If conversion to int fails, skip this iteration
                continue

            # Check for the downward peak (touch detected)
            if not in_touch_cycle and sense_value < downward_peak_threshold:
                current_color = GREEN  # Turn the box green when touched
                in_touch_cycle = True  # Mark the start of a touch cycle

            # Check for the upward peak (release detected)
            if in_touch_cycle and sense_value > upward_peak_threshold:
                current_color = YELLOW  # Turn the box yellow when released
                in_touch_cycle = False  # End the touch cycle

    # Fill the window with a white background
    window.fill((255, 255, 255))

    # Draw the box with the current color (Red, Green, or Yellow)
    pygame.draw.rect(window, current_color, (100, 100, 200, 200))

    # Draw the input box for user input
    draw_input_box()

    # Update the display
    pygame.display.update()

# Close the serial port and Pygame
ser.close()
pygame.quit()
