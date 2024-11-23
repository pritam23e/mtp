import numpy as np
import pygame
import matplotlib.pyplot as plt

# Simulation Parameters
L_rows, L_cols = 200, 200
J = 1
T = 2.5
H_vals = np.linspace(0, 3, 1000) 
steps_per_H = 5000  
H_vals_back = np.linspace(3, -3, 1000)
H_vals_forw = np.linspace(-3, 3, 1000)

# Initialize spin lattice with random spins (-1 or +1)
spin_lattice = 2 * np.random.randint(0, 2, (L_rows, L_cols)) - 1
magnetization = np.zeros(len(H_vals))
magnetization_back = np.zeros(len(H_vals_back))
magnetization_forw = np.zeros(len(H_vals_forw))

# Calculate energy difference (dE) if a spin is flipped
def calculate_dE(spin_lattice, i, j, H):
    S = spin_lattice[i, j]
    neighbors = (
        spin_lattice[(i + 1) % L_rows, j] + spin_lattice[(i - 1) % L_rows, j] +
        spin_lattice[i, (j + 1) % L_cols] + spin_lattice[i, (j - 1) % L_cols]
    )
    dE = 2 * S * (J * neighbors + H)
    return dE

# Initialize Pygame
pygame.init()
cell_size = 3
margin_top = 40
screen_height = L_rows * cell_size + margin_top + 60
screen_width = L_cols * cell_size + 160  # Extra space for H slider and labels
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Spin Lattice Evolution")

font = pygame.font.SysFont(None, 24)

# Function to draw the vertical H slider on the right
def draw_H_slider(H):
    slider_x = screen_width - 60  # Position it on the right side
    slider_height = screen_height - 80
    slider_y = 40
    # Draw slider background (gray)
    pygame.draw.rect(screen, (200, 200, 200), (slider_x, slider_y, 10, slider_height))
    
    # Correct the mapping of H to slider position
    # Map H [-3, 3] to [slider_y, slider_y + slider_height]
    H_position = slider_y + (3-H) * slider_height/6  # This formula maps H from [-3, 3] to [slider_y, slider_y + slider_height]
    pygame.draw.line(screen, (255, 0, 0), (slider_x, H_position), (slider_x + 20, H_position), 4)
    
    # Draw labels for -3 and 3
    label_top = font.render("3", True, (0, 0, 0))
    label_bottom = font.render("-3", True, (0, 0, 0))
    screen.blit(label_top, (slider_x + 25, slider_y))
    screen.blit(label_bottom, (slider_x + 25, slider_y + slider_height - label_bottom.get_height()))
    
    # Display current value of H at the top of the slider
    H_label = font.render(f"H = {H:.2f}", True, (0, 0, 0))
    screen.blit(H_label, (slider_x - 10, slider_y - 25))  # Position the value above the slider

def update_display(spin_lattice, phase_label, step_count, H):
    # Update display only every 10 steps to reduce computation
    if step_count % 10 != 0:
        return

    screen.fill((255, 255, 255))  # Clear screen with white background
    
    # Draw lattice with alternating colors for spins to improve visibility
    for i in range(L_rows):
        for j in range(L_cols):
            color = (255, 255, 255) if spin_lattice[i, j] == 1 else (0, 0, 0)  # Blue for -1, White for +1
            pygame.draw.rect(screen, color, (40 + j * cell_size, margin_top + i * cell_size, cell_size, cell_size))

    # Display phase label above the lattice
    phase_text = font.render(phase_label, True, (0, 0, 0))
    screen.blit(phase_text, (screen_width // 2 - phase_text.get_width() // 2, 10))

    # Display lattice label below
    lattice_label = font.render("Space Lattice", True, (0, 0, 0))
    screen.blit(lattice_label, (screen_width // 2 - lattice_label.get_width() // 2, L_rows * cell_size + margin_top + 20))
    
    # Draw row and column scales along the axes
    for i in range(0, L_rows, 25):
        row_label = font.render(str(i), True, (0, 0, 0))
        screen.blit(row_label, (15, margin_top + (L_rows - 1 - i) * cell_size - row_label.get_height() // 2))
        
    for j in range(0, L_cols, 25):
        col_label = font.render(str(j), True, (0, 0, 0))
        screen.blit(col_label, (40 + j * cell_size - col_label.get_width() // 2, margin_top + L_rows * cell_size + 5))

    # Draw the vertical H slider with the current H value
    draw_H_slider(H)
    
    pygame.display.flip()

# Monte Carlo Metropolis algorithm
def monte_carlo(spin_lattice, H, steps):
    for _ in range(steps):
        i, j = np.random.randint(0, L_rows), np.random.randint(0, L_cols)
        dE = calculate_dE(spin_lattice, i, j, H)
        if dE < 0 or np.random.rand() < np.exp(-dE / T):
            spin_lattice[i, j] *= -1

# Simulation phases
def run_phase(H_values, spin_lattice, magnetization, label):
    running = True
    step_count = 0
    for h in range(len(H_values)):
        if not running:
            break
        H = H_values[h]
        monte_carlo(spin_lattice, H, steps_per_H)
        magnetization[h] = np.mean(spin_lattice)
        step_count += steps_per_H
        update_display(spin_lattice, label, step_count, H)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
    return running

# Run simulation with phase continuity
if run_phase(H_vals, spin_lattice, magnetization, "1st Phase: Forward Sweep"):
    if run_phase(H_vals_back, spin_lattice, magnetization_back, "2nd Phase: Reverse Sweep"):
        run_phase(H_vals_forw, spin_lattice, magnetization_forw, "3rd Phase: Forward Back Sweep")

pygame.quit()

# Plot Hysteresis Curve
plt.figure()
plt.plot(H_vals, magnetization, 'o', label='Forward Sweep')
plt.plot(H_vals_back, magnetization_back, 'o', label='Reverse Sweep')
plt.plot(H_vals_forw, magnetization_forw, 'o', label='Forward Back Sweep')
plt.xlabel('Magnetic Field H')
plt.ylabel('Magnetization M')
plt.title('Hysteresis Curve using Ising Model and Monte Carlo Method')
plt.legend()
plt.grid(True)
plt.show()
