import pygame
import serial
import time

# Initialize Pygame
pygame.init()

# Set up the display
window_size = (1500, 700)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Race Track Checkpoint Timer")

# Define colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ROAD_COLOR = (128, 128, 128)  # Grey for road path

A1_color = RED
A2_color = RED
A3_color = RED

# Threshold values for sensors
A1_downward_threshold = 100
A1_upward_threshold = 600
A2_downward_threshold = 150
A2_upward_threshold = 600
A3_downward_threshold = 100
A3_upward_threshold = 600

# Sensor states
A1_active = True  # A1 is active initially
A2_active = False
A3_active = False
process_complete = False

# Distance variables (in meters)
distance_A1_to_A2 = 20.0  # Distance between A1 and A2
distance_A2_to_A3 = 30.0  # Distance between A2 and A3

# Timing variables
start_time = 0
start_time_A2 = 0
end_time_A3 = 0

# Timing for crossing checkpoints
time_A1_crossed = 0
time_A2_crossed = 0
time_A3_crossed = 0

# Lap variables
lap_count = 1  # Start from Lap 1
lap_times = []  # List to store times for each lap
lap_speeds = []  # List to store average speeds for each lap

# Font settings
font = pygame.font.SysFont(None, 55)
large_font = pygame.font.SysFont(None, 50)

# Open serial port (replace 'COM3' with your port)
ser = serial.Serial('COM9', 19200)
time.sleep(2)

running = True
start_time = time.time()  # Start the global timer
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read data from Arduino
    if ser.in_waiting > 0:
        data = ser.readline()

        try:
            # Decode the data
            data_decoded = data.decode('utf-8').strip()
        except UnicodeDecodeError:
            continue

        if data_decoded:
            try:
                A1_value, A2_value, A3_value = map(int, data_decoded.split(','))
            except ValueError:
                continue

            # Handle A1
            if A1_active:
                if A1_value < A1_downward_threshold and time_A1_crossed == 0:
                    A1_color = GREEN
                    time_A1_crossed = time.time() - start_time  # Elapsed time for A1
                elif A1_value > A1_upward_threshold and time_A1_crossed != 0:
                    A1_color = RED
                    A1_active = False
                    A2_active = True

            # Handle A2
            if A2_active:
                if A2_value < A2_downward_threshold and time_A2_crossed == 0:
                    A2_color = GREEN
                    time_A2_crossed = time.time() - start_time  # Elapsed time for A2
                elif A2_value > A2_upward_threshold and time_A2_crossed != 0:
                    A2_color = RED
                    A2_active = False
                    A3_active = True

            # Handle A3
            if A3_active:
                if A3_value < A3_downward_threshold and time_A3_crossed == 0:
                    A3_color = GREEN
                    time_A3_crossed = time.time() - start_time  # Elapsed time for A3
                elif A3_value > A3_upward_threshold and time_A3_crossed != 0:
                    A3_color = RED
                    A3_active = False
                    process_complete = True

                    # Calculate lap time and speed
                    lap_time = time_A3_crossed - time_A1_crossed
                    lap_times.append(lap_time)  # Store lap time

                    # Calculate average speed for the lap
                    total_distance = distance_A1_to_A2 + distance_A2_to_A3
                    avg_speed = total_distance / lap_time
                    lap_speeds.append(avg_speed)  # Store average speed

                    # Increment lap count and reset for next lap
                    lap_count += 1
                    start_time = time.time()  # Reset the global timer
                    time_A1_crossed = 0
                    time_A2_crossed = 0
                    time_A3_crossed = 0
                    A1_active = True  # Re-activate A1 for the next lap
                    A2_active = False
                    A3_active = False
                    process_complete = False

    # Fill the window
    window.fill(WHITE)

    # Draw the road path from A1 to A2 to A3 (as lines or boxes)
    pygame.draw.line(window, ROAD_COLOR, (175, 135), (745, 135), 50)  # Line from A1 to A2
    pygame.draw.line(window, ROAD_COLOR, (745, 135), (1360, 135), 50)  # Line from A2 to A3

    # Display segment lengths on the road
    segment_text_A1_A2 = large_font.render(f"Distance: {distance_A1_to_A2:.2f} m", True, WHITE)
    segment_text_A2_A3 = large_font.render(f"Distance: {distance_A2_to_A3:.2f} m", True, WHITE)
    window.blit(segment_text_A1_A2, (320, 125))
    window.blit(segment_text_A2_A3, (920, 125))

    # Draw boxes for sensors
    pygame.draw.rect(window, A1_color, (100, 60, 150, 150))
    pygame.draw.rect(window, A2_color, (670, 60, 150, 150))
    pygame.draw.rect(window, A3_color, (1283, 60, 150, 150))

    # Render sensor labels
    text_A1 = font.render('A1', True, WHITE)
    window.blit(text_A1, (150, 120))
    text_A2 = font.render('A2', True, WHITE)
    window.blit(text_A2, (720, 120))
    text_A3 = font.render('A3', True, WHITE)
    window.blit(text_A3, (1335, 120))

    # Render clock at the top middle (MM:SS:msms s)
    current_time = time.time() - start_time
    clock_text = large_font.render(f"Timer: {int(current_time // 60):02}:{int(current_time % 60):02}:{int((current_time % 1) * 100):02} s", True, BLACK)
    window.blit(clock_text, (1000, 10))

    # Render checkpoint labels and times
    if time_A1_crossed > 0:
        a1_text = large_font.render(f"A1 Crossed", True, BLACK)
        window.blit(a1_text, (80, 220))  # Below A1 box
        a1_time = large_font.render(f"{int(time_A1_crossed // 60):02}:{int(time_A1_crossed % 60):02}:{int((time_A1_crossed % 1) * 100):02} s", True, BLACK)
        window.blit(a1_time, (90, 260))

    if time_A2_crossed > 0:
        a2_text = large_font.render(f"A2 Crossed", True, BLACK)
        window.blit(a2_text, (650, 220))  # Below A2 box
        a2_time = large_font.render(f"{int(time_A2_crossed // 60):02}:{int(time_A2_crossed % 60):02}:{int((time_A2_crossed % 1) * 100):02} s", True, BLACK)
        window.blit(a2_time, (660, 260))

    if time_A3_crossed > 0:
        a3_text = large_font.render(f"A3 Crossed", True, BLACK)
        window.blit(a3_text, (1250, 220))  # Below A3 box
        a3_time = large_font.render(f"{int(time_A3_crossed // 60):02}:{int(time_A3_crossed % 60):02}:{int((time_A3_crossed % 1) * 100):02} s", True, BLACK)
        window.blit(a3_time, (1260, 260))

     # Display speed from A1 to A2 between A1 and A2
    if time_A1_crossed > 0 and time_A2_crossed > 0:
        time_A1_to_A2 = time_A2_crossed - time_A1_crossed
        speed_A1_to_A2 = distance_A1_to_A2 / time_A1_to_A2
        speed_label = font.render("Speed A1 to A2:", True, BLACK)
        speed_value = font.render(f"{speed_A1_to_A2:.2f} m/s", True, BLACK)
        window.blit(speed_label, (305, 300))  # Display "Speed A1 to A2"
        window.blit(speed_value, (330, 340))  # Display the speed value below it
    # Display average speed between A2 and A3
    if time_A2_crossed > 0 and time_A3_crossed > 0:
        time_A2_to_A3 = time_A3_crossed - time_A2_crossed
        speed_A2_to_A3 = distance_A2_to_A3 / time_A2_to_A3
        speed_label = font.render("Speed A2 to A3:", True, BLACK)
        speed_value = font.render(f"{speed_A2_to_A3:.2f} m/s", True, BLACK)
        window.blit(speed_label, (905, 300))  # Display "Speed A1 to A2"
        window.blit(speed_value, (930, 340))  # Display the speed value below it

    # Display lap count and times for each lap
    lap_text = large_font.render(f"Lap {lap_count}", True, BLACK)
    window.blit(lap_text, (300, 10))  # Display current lap

    # Display lap time and average speed for each lap
    if lap_times:
        for i, (lap_time, avg_speed) in enumerate(zip(lap_times, lap_speeds)):
            lap_time_text = large_font.render(f"Lap {i+1}: {lap_time:.2f} s, Avg Speed: {avg_speed:.2f} m/s", True, BLACK)
            window.blit(lap_time_text, (200, 380 + i * 40))  # Display lap times and speeds

    # Update the display
    pygame.display.update()

# Close the serial port and Pygame
ser.close()
pygame.quit()
