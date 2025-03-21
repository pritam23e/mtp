import pygame
import serial
import time

# Initialize Pygame
pygame.init()

# Set up the display
window_size = (1000, 700)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Touch Sensor Shape Detection")

# Define colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
current_color = RED

# Thresholds
downward_peak_threshold = 2  # Value when the sensor is pressed
touch_initiation_threshold = 50  # Value to indicate touch cycle initiation
edge_down_threshold = 10  # Value to detect the start of an edge
edge_up_threshold = 50  # Value to detect the end of an edge
end_cycle_threshold = 1020  # Value to detect the end of the touch cycle
steep_slope_threshold = 50  # Threshold for steep slope detection

# Variables to track the touch cycle
in_touch_cycle = False
cycle_initiated = False
edge_detected = False
edge_count = 0

# Time tracking for shape detection
time_stamps = []
shape = "Unknown"
start_time = 0

# Open serial port (replace 'COM3' with your port)
ser = serial.Serial('COM9', 9600)
time.sleep(2)  # Wait for the serial connection to initialize

# Function to check if the slope is steep enough (based on crossing)
def is_steep_slope(prev_value1, prev_value2, current_value):
    # Calculate the slope between previous two points (i-3 and i-2) and the current one (i)
    slope = abs(current_value - prev_value2)
    return slope > steep_slope_threshold

# Track previous sensor values (last 3 values)
previous_values = []

# Initialize Pygame font
font = pygame.font.Font(None, 36)

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
                sense_value = int(data_decoded)
            except ValueError:
                # If conversion to int fails, skip this iteration
                continue

            # Track previous values
            previous_values.append(sense_value)

            # Keep the last 3 values for checking the steepness
            if len(previous_values) > 3:
                previous_values.pop(0)

            # Detect the start of a touch cycle
            if not in_touch_cycle and sense_value < downward_peak_threshold and len(previous_values) >= 3:
                # Check if the slope is steep enough using the previous 2 values (i-3 and i-2)
                if is_steep_slope(previous_values[-3], previous_values[-2], sense_value):
                    in_touch_cycle = True
                    edge_count = 0
                    time_stamps = []
                    shape = "Unknown"
                    start_time = time.time()
                    current_color = BLUE

            # Confirm touch cycle initiation after stabilizing
            elif in_touch_cycle and not cycle_initiated and sense_value > touch_initiation_threshold:
                cycle_initiated = True
                current_color = GREEN

            # Detect edges within the touch cycle
            if cycle_initiated:
                # Detect the start of an edge
                if not edge_detected and sense_value < edge_down_threshold and len(previous_values) >= 3:
                    # Check if the slope is steep enough using the previous 2 values (i-3 and i-2) for edge detection
                    if is_steep_slope(previous_values[-3], previous_values[-2], sense_value):
                        edge_detected = True
                        time_stamps.append(time.time() - start_time)
                        current_color = BLUE

                # Confirm the edge detection
                elif edge_detected and sense_value > edge_up_threshold:
                    edge_detected = False
                    edge_count += 1
                    current_color = GREEN

            # Detect the end of the touch cycle and determine the shape
            if in_touch_cycle and sense_value > end_cycle_threshold:
                if edge_count == 0:
                    shape = "Circle"
                elif edge_count == 3:
                    shape = "Triangle"
                elif edge_count == 4:
                    if len(time_stamps) >= 4:
                        side_lengths = [time_stamps[i + 1] - time_stamps[i] for i in range(len(time_stamps) - 1)]
                        if max(side_lengths) - min(side_lengths) < 0.1:  # Threshold to check equality
                            shape = "Square"
                        else:
                            shape = "Rectangle"
                elif edge_count == 5:
                    shape = "Pentagon"
                elif edge_count == 6:
                    shape = "Hexagon"
                else:
                    shape = f"{edge_count}-sided polygon"

                current_color = RED

                # Reset after the object is removed
                print(f"Shape detected: {shape}")
                in_touch_cycle = False
                cycle_initiated = False
                edge_detected = False

    # Fill the window with a white background
    window.fill(WHITE)

    # Draw the box with the current color (Red or Green)
    pygame.draw.rect(window, current_color, (350, 300, 300, 300))

    # Display the edge count and shape
    font = pygame.font.Font(None, 100)  # 48 is the font size, you can adjust it
    edge_text = font.render(f"Edges: {edge_count}", True, (0, 0, 0))

    window.blit(edge_text, (10, 10))

    shape_text = font.render(f"Shape: {shape}", True, (0, 0, 0))
    window.blit(shape_text, (10, 100))

    # Update the display
    pygame.display.update()

# Close the serial port and Pygame
ser.close()
pygame.quit()
