from os import access
from webbrowser import BackgroundBrowser
from matplotlib import container
from matplotlib.patches import Circle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pygame
import sys
import math
import pymunk
import pymunk.pygame_util
import random

pygame.init()
# Screen properties
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bouncy balls")

clock = pygame.time.Clock()
FPS = 60
background_color = (30, 30, 30)

# Constants
g = 500
restitution = 1.01
physics_steps_per_frame = 10
space = pymunk.Space()
space.gravity = (0, g)
space.iterations = 30


class Ball:
    def __init__(self, space, pos, vel, radius, color):

        self.radius = radius
        self.color = color
        mass = 1
        moment = pymunk.moment_for_circle(mass, 0, radius)

        self.body = pymunk.Body(mass, moment)
        self.body.position = pos
        self.body.velocity = vel

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = restitution
        self.shape.friction = 0

        space.add(self.body, self.shape)

    def draw(self, screen):
        # Draw the ball as a circle on the given surface
        pos = self.body.position
        pygame.draw.circle(screen, self.color, (int(pos.x), int(pos.y)), self.radius)


def create_container(space, pos, radius, num_segments=32, thickness=3, elasticity=1.0):
    static_body = space.static_body
    segments = []
    for i in range(num_segments):
        angle1 = 2 * math.pi * i / num_segments
        angle2 = 2 * math.pi * (i + 1) / num_segments

        p1 = pos + pymunk.Vec2d(radius * math.cos(angle1), radius * math.sin(angle1))
        p2 = pos + pymunk.Vec2d(radius * math.cos(angle2), radius * math.sin(angle2))

        segment = pymunk.Segment(static_body, p1, p2, thickness)
        segment.elasticity = elasticity
        segment.friction = 0
        segments.append(segment)
        space.add(segment)
    return segments


container_centre = pymunk.Vec2d(width / 2, height / 2)
container_radius = 280
container_segments = create_container(space, container_centre, container_radius)

"""possible_colors = {
    "Violet": (144, 0, 211),
    "Indigo": (75, 0, 130),
    "Blue": (0, 0, 255),
    "Green": (0, 255, 0),
    "Yellow": (255, 255, 0),
    "Orange": (255, 127, 0),
    "Red": (255, 0, 0),
}"""
possible_colors = [
    (144, 0, 211),
    (75, 0, 130),
    (0, 0, 255),
    (0, 255, 0),
    (255, 255, 0),
    (255, 127, 0),
    (255, 0, 0),
]
unused_colors = possible_colors.copy()


def draw_container(screen, pos, radius, color=(155, 155, 155), line_width=2):
    pygame.draw.circle(screen, color, (int(pos.x), int(pos.y)), radius, line_width)


def get_rand_color(colors):
    if not colors:
        colors = possible_colors.copy()
    color = random.choice(colors)
    colors.remove(color)
    return color


balls = [
    Ball(
        space,
        pos=(400, 100),
        vel=(0, 0),
        radius=10,
        color=get_rand_color(unused_colors),
    ),
    Ball(
        space,
        pos=(300, 100),
        vel=(0, 0),
        radius=10,
        color=get_rand_color(unused_colors),
    ),
    Ball(
        space,
        pos=(500, 100),
        vel=(0, 0),
        radius=10,
        color=get_rand_color(unused_colors),
    ),
]

running = True


while running:
    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    sub_dt = dt / physics_steps_per_frame
    for _ in range(physics_steps_per_frame):
        space.step(sub_dt)


    screen.fill(background_color)
    draw_container(screen, container_centre, container_radius)
    for ball in balls:
        ball.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
