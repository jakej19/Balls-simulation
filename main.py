from os import access
from webbrowser import BackgroundBrowser
from matplotlib.patches import Circle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pygame
import sys
import math

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
restitution = 1.001


class Ball:
    def __init__(self, pos, vel, radius, color):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.radius = radius
        self.color = color

    def update(self, dt):
        """update ball location given acceleration and change in time.
        Args:
            acceleration (np.array): [x_acceleration, y_acceleration]
            dt (float): time step size
        """
        self.vel.y += g * dt

        self.pos += self.vel * dt

    def draw(self, surface):
        # Draw the ball as a circle on the given surface
        pygame.draw.circle(
            surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius
        )

    def collides_with_circle(self, other):
        distance_sq = (self.pos - other.pos).length_squared()
        radii_sum_sq = (self.radius + other.radius) ** 2
        return distance_sq <= radii_sum_sq


class CircleObject:
    def __init__(self, pos, radius, color, width=3):
        self.pos = pygame.Vector2(pos)
        self.radius = radius
        self.color = color
        self.width = width

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.pos.x), int(self.pos.y)),
            self.radius,
            self.width,
        )


def handle_ball_collision(ball1, ball2):
    """
    Process an elastic collision between two balls.
    Assumes equal mass for both balls.
    """
    # Vector from ball1 to ball2
    collision_vector = ball2.pos - ball1.pos
    distance = collision_vector.length()

    # If the distance is zero (overlapping centers), skip collision response to avoid division by zero.
    if distance == 0:
        normal = pygame.Vector2(1, 0)
        distance = 0.01  # minimal distance
    else:
        normal = collision_vector / distance

    penetration_depth = (ball1.radius + ball2.radius) - distance

    if penetration_depth > 0:
        # Position correction: push each ball away by half of the overlap distance
        angle = -math.atan2(ball1.pos.y - ball2.pos.y, ball1.pos.x - ball2.pos.x)

        correction = penetration_depth / 2

        ball1.pos.x += math.cos(angle) * correction
        ball1.pos.y += math.sin(angle) * correction
        ball2.pos.x -= math.cos(angle) * correction
        ball1.pos.y -= math.sin(angle) * correction

        # Compute relative velocity along the collision normal.
        relative_velocity = ball1.vel - ball2.vel
        vel_along_normal = relative_velocity.dot(normal)

        if vel_along_normal < 0:
            # Compute impulse scalar.
            # Using equal mass (assumed 1) for simplicity. Adjust the denominator if masses differ.
            impulse_magnitude = -(1 + restitution) * vel_along_normal / 2
            impulse = normal * impulse_magnitude

            # Apply impulse (adjust velocities)
            ball1.vel += impulse
            ball2.vel -= impulse


def handle_ball_container_collision(ball, container):
    """
    Check and handle a collision of a ball with the interior boundary of the container.
    The ball collides with the wall if the distance between its center and the container's
    center is greater than container.radius - ball.radius.
    """
    collision_vector = ball.pos - container.pos
    distance = collision_vector.length()
    allowed_distance = container.radius - ball.radius

    if distance > allowed_distance:
        # Compute the collision normal (from container to ball).
        normal = collision_vector.normalize()
        # Reflect ball's velocity: v' = v - 2*(v dot n)*n.
        ball.vel = ball.vel - 2 * ball.vel.dot(normal) * normal
        # Correct the ball's position to sit exactly on the boundary.
        ball.pos = container.pos + normal * allowed_distance


def check_all_collisions(balls, objects):
    """
    Check collisions between all balls (pairwise) and between each ball and static objects.
    """
    # Check collisions among balls
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            if balls[i].collides_with_circle(balls[j]):
                handle_ball_collision(balls[i], balls[j])

    # Check collisions between each ball and static circle objects
    for ball in balls:
        for obj in objects:
            handle_ball_container_collision(ball, obj)


balls = [
    Ball(pos=(400, 100), vel=(0, 0), radius=10, color=(0, 150, 255)),
    Ball(pos=(300, 100), vel=(0, 0), radius=10, color=(0, 150, 255)),
    Ball(pos=(500, 101), vel=(0, 0), radius=10, color=(0, 150, 255)),
]
objects = [
    CircleObject(
        pos=(int(width / 2), int(height / 2)), radius=280, color=(155, 155, 155)
    )
]
running = True


while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for ball in balls:
        ball.update(dt)

    check_all_collisions(balls, objects)
    screen.fill(background_color)

    for ball in balls:
        ball.draw(screen)
    for obj in objects:
        obj.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
