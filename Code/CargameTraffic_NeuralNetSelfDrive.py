"""
Car game project. October 2024.
- Programming a car game using an LLM
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 14:32:10 2024

@author: sila
"""

import pygame
import math
import random
import time

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import numpy as np

# Load the data from the Excel file
df = pd.read_excel('game_data.xlsx')

# Prepare features and target variable
X = df[['Car_Offset', 'Traffic_Position']].to_numpy()  # Convert selected features to NumPy array
y = df['User_action'].to_numpy()

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale data set
scaler = StandardScaler()
scaler.fit(X_train)
xtrain = scaler.transform(X_train)
xtest= scaler.transform(X_test)

from sklearn.neural_network import MLPClassifier
mlp = MLPClassifier( hidden_layer_sizes =( 5, 5 ), max_iter = 100000 , random_state = 42 )
mlp.fit(xtrain, y_train)

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 480, 640
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Game with Curving Road and Scoring. Neural Net self drive")

# Define colors
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
GREEN = (34, 139, 34)  # Dark green for grass
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)  # Color for traffic cars

# Road parameters
road_width = 200
slice_height = 5  # Height of each road slice
road_slices = []
curve_amplitude = 100  # Maximum horizontal offset due to curvature
curve_frequency = 0.005  # Frequency of the curve

# Traffic parameters
traffic_width = 30
traffic_height = 50
traffic_speed = 5
traffic_spawn_interval = 20  # Time in milliseconds between spawns
last_spawn_time = 0

# Initialize road slices
for y in range(0, HEIGHT, slice_height):
    slice_info = {'y': y, 'x': (WIDTH - road_width) // 2, 'width': road_width, 'traffic_road_offset': 0, 'DoneCrash': False}
    road_slices.append(slice_info)

# Car parameters
car_width = 40
car_height = 60
car_x = WIDTH // 2 - car_width // 2
car_y = HEIGHT - car_height - 20
car_speed = 5

# Lane markings parameters
lane_width = 5
lane_height = 20
lane_gap = 20

# Scrolling speed
scroll_speed = 5

# Total distance traveled (used for curve calculation)
total_distance = 0

# Initialize score
score = 0

# Set up font for displaying score
pygame.font.init()
font = pygame.font.SysFont(None, 36)  # Use default font and size 36

# Create clock object
clock = pygame.time.Clock()

#Here we store the data that we write to the excel file
Store_Data = []

TRAFFIC_IN_LEFT_LANE = -1
TRAFFIC_IN_RIGHT_LANE = 1
Store_where_is_traffic = 0

#Store traffic lane
def store_traffic_lane(traffic_lane_offset):
    global Store_where_is_traffic
    if (traffic_lane_offset<100):
        Store_where_is_traffic = TRAFFIC_IN_LEFT_LANE
    else:
        Store_where_is_traffic = TRAFFIC_IN_RIGHT_LANE

Store_car_offset = 0
#Calculate car offset
def calc_car_offset(car_position, middle_road_x_at_car):
    global Store_car_offset
    Store_car_offset = car_position - middle_road_x_at_car

    return Store_car_offset

SELF_DRIVE = True
TURN_RIGHT = 1
TURN_LEFT = -1
WHEEL_TURN = TURN_LEFT # Starting position
def store_self_drive(car_position, middle_road_x_at_car):
    global WHEEL_TURN
    if (car_position - middle_road_x_at_car)<0:
        WHEEL_TURN = TURN_RIGHT
    else:
        WHEEL_TURN = TURN_LEFT

#Render collected data
def render_collected_data(calculated_car_offset):
    # Render the offset
    car_offset_text = font.render(f"Car Offset: {calculated_car_offset}", True, BLACK)
    window.blit(car_offset_text, (10, 100))  # Draw car offset at top-left corner

    where_is_traffic_text = font.render(f"Where is Traffic: {Store_where_is_traffic}", True, BLACK)
    window.blit(where_is_traffic_text, (10, 150))  # Draw car offset at top-left corner

    # time.sleep(0.1)

# Main game loop
running = True
while running:
    dt = clock.tick(60)  # Limit frame rate to 60 FPS

    total_distance += scroll_speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Prepare the input for self drive
    new_instance = np.array([[Store_car_offset, Store_where_is_traffic]])

    # Scale
    new_instance_scaled = scaler.transform(new_instance)

    # Predict the user action
    predicted_action_encoded = mlp.predict(new_instance_scaled)
    if predicted_action_encoded < 0:
        car_x -= car_speed
    else:
        car_x += car_speed

    # Ensure the car doesn't go off the screen
    car_x = max(0, min(WIDTH - car_width, car_x))

    # Update car position
    car_rect = pygame.Rect(car_x, car_y, car_width, car_height)

    # Calculate road x-position at car's y-coordinate
    curve_at_car = math.sin((car_y + total_distance) * curve_frequency) * curve_amplitude
    road_x_at_car = (WIDTH - road_width) // 2 + curve_at_car

    # Check if car is outside the road at its position
    if car_rect.left < road_x_at_car or car_rect.right > road_x_at_car + road_width:
        off_road = True
        score -= 1  # Subtract points when off the road
    else:
        off_road = False
        score += 1  # Add points when on the road

    # Check traffic collides with car
    slice_info = road_slices[0]
    # Traffic y coordinate
    traffic_lane_y = slice_info['y']
    if (abs(car_y - traffic_lane_y) < 20) and (slice_info['DoneCrash'] == False):
        # Calculate the curvature offset for this slice
        curve = math.sin((slice_info['y'] + total_distance) * curve_frequency) * curve_amplitude
        # Update the x-coordinate of the slice
        traffic_lane_x = (WIDTH - road_width) // 2 + curve + slice_info['traffic_road_offset']
        if abs(car_x - traffic_lane_x) < 20:
           # Crash
           slice_info['DoneCrash'] = True
           crash_text = font.render(f"Crash: -1000 Points", True, RED)
           window.blit(crash_text, (10, 50))  # Draw score at top-left corner
           # Update the display
           pygame.draw.rect(window, WHITE, car_rect)
           pygame.display.update()
           time.sleep(2)
           score -= 1000

    # Spawn traffic cars
    current_time = pygame.time.get_ticks()
    if (current_time - last_spawn_time) > traffic_spawn_interval:
        last_spawn_time = current_time

        # Spawn traffic for slice
        slice_info = road_slices[0]
        # Traffic y coordinate
        traffic_lane_y = slice_info['y']

        # Calculate the curvature offset for this slice
        curve = math.sin((slice_info['y'] + total_distance) * curve_frequency) * curve_amplitude
        # Update the x-coordinate of the slice
        traffic_lane_x = (WIDTH - road_width) // 2 + curve + slice_info['traffic_road_offset']

        # Create traffic car rect
        traffic_rect = pygame.Rect(traffic_lane_x, traffic_lane_y, traffic_width, traffic_height)

        # Store where traffic is
        store_traffic_lane(slice_info['traffic_road_offset'])

    # Update road slices
    for slice_info in road_slices:
        # Move the slice down the screen
        slice_info['y'] += scroll_speed

        # If the slice is off the bottom, reset to the top
        if slice_info['y'] > HEIGHT:
            slice_info['y'] -= HEIGHT + slice_height
            # Random x spawn position. Update traffic spawn x position, for slice.
            if 50 <= random.randrange(100):
                slice_info['traffic_road_offset'] = 25
            else:
                slice_info['traffic_road_offset'] = 125
            # No crashes yet
            slice_info['DoneCrash'] = False

        # Calculate the curvature offset for this slice
        curve = math.sin((slice_info['y'] + total_distance) * curve_frequency) * curve_amplitude

        # Update the x-coordinate of the slice
        slice_info['x'] = (WIDTH - road_width) // 2 + curve

    # Clear the screen
    window.fill(GREEN)  # Background color (grass)

    # Draw the road slices
    for slice_info in road_slices:
        pygame.draw.rect(window, GRAY, (slice_info['x'], slice_info['y'], slice_info['width'], slice_height))

        # Draw lane markings
        lane_y = slice_info['y']
        if (lane_y // (lane_height + lane_gap)) % 2 == 0:
            lane_x = slice_info['x'] + slice_info['width'] // 2 - lane_width // 2
            pygame.draw.rect(window, WHITE, (lane_x, lane_y, lane_width, slice_height))

    if (Store_where_is_traffic == TRAFFIC_IN_LEFT_LANE):
        car_offset = calc_car_offset(car_rect.left + (car_width // 2), road_x_at_car + 180)
    else:
        car_offset = calc_car_offset(car_rect.left + (car_width // 2), road_x_at_car + 5)

    # Draw the car
    car_color = YELLOW if off_road else RED
    pygame.draw.rect(window, car_color, car_rect)

    # Draw traffic cars
    pygame.draw.rect(window, BLUE, traffic_rect)

    # Render the score
    score_text = font.render(f"Score: {score}", True, BLACK)
    window.blit(score_text, (10, 10))  # Draw score at top-left corner

    # Render collected data
    render_collected_data(car_offset)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
