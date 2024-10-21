"""
Car game project. October 2024.
- Programming a car game using an LLM
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 4 09:22:12 2024

@author: sila
"""

import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 480, 640
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Game with Moving Road")

# Define colors
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
GREEN = (34, 139, 34)  # Dark green for grass
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Road parameters
road_width = 200
road_x = (WIDTH - road_width) // 2
road_y = 0
road_height = HEIGHT

# Car parameters
car_width = 40
car_height = 60
car_x = WIDTH // 2 - car_width // 2
car_y = HEIGHT - car_height - 20
car_speed = 5

# Lane markings parameters
lane_width = 5
lane_height = 30
lane_gap = 20
lane_markings = []

# Initialize lane markings positions
for i in range(-lane_height - lane_gap, HEIGHT, lane_height + lane_gap):
    lane_markings.append(i)

# Scrolling speed
scroll_speed = 5

# Road curve parameters
curve_direction = 0  # -1 for left, 1 for right, 0 for straight
curve_speed = 1  # How quickly the road curves
curve_timer = 0
curve_change_interval = 120  # Frames before changing curve direction

# Create clock object
clock = pygame.time.Clock()

# Main game loop
running = True
while running:
    clock.tick(60)  # Limit frame rate to 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get pressed keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        car_x -= car_speed
    if keys[pygame.K_RIGHT]:
        car_x += car_speed

    # Ensure the car doesn't go off the screen
    car_x = max(0, min(WIDTH - car_width, car_x))

    # Update car position
    car_rect = pygame.Rect(car_x, car_y, car_width, car_height)

    # Check if car is outside the road
    if car_rect.left < road_x or car_rect.right > road_x + road_width:
        off_road = True
    else:
        off_road = False

    # Move lane markings downward
    lane_markings = [y + scroll_speed for y in lane_markings]
    # Reset lane markings when they move off the screen
    for i in range(len(lane_markings)):
        if lane_markings[i] > HEIGHT:
            lane_markings[i] = -lane_height - lane_gap

    # Update road curve
    curve_timer += 1
    if curve_timer >= curve_change_interval:
        curve_timer = 0
        curve_direction = random.choice([-1, 0, 1])  # Randomly change direction

    # Move road to simulate curves
    road_x += curve_direction * curve_speed
    # Keep road within screen bounds
    if road_x < 0:
        road_x = 0
        curve_direction = random.choice([0, 1])  # Can't curve further left
    elif road_x > WIDTH - road_width:
        road_x = WIDTH - road_width
        curve_direction = random.choice([-1, 0])  # Can't curve further right

    # Clear the screen
    window.fill(GREEN)  # Background color (grass)

    # Draw the road
    road_rect = pygame.Rect(road_x, road_y, road_width, road_height)
    pygame.draw.rect(window, GRAY, road_rect)

    # Draw lane markings
    for lane_y in lane_markings:
        lane_rect = pygame.Rect(
            road_x + road_width // 2 - lane_width // 2, lane_y, lane_width, lane_height
        )
        pygame.draw.rect(window, WHITE, lane_rect)

    # Draw the car
    car_color = YELLOW if off_road else RED
    pygame.draw.rect(window, car_color, car_rect)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
