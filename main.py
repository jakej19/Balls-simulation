from os import access
import numpy as np
import pygame
import sys
import math
import pymunk
import random
import pygame.midi
from utils.music import NOTES
import numpy as np


# Constants
g = 80
restitution = 1.001
physics_steps_per_frame = 10

FPS = 60
BALL_SIZE = 20
BALL_COLLISION_TYPE = 1
STATIC_COLLISION_TYPE = 2


# Song setup
song_file = "songs/fireflies.txt"
with open(song_file, "r") as f:
    song = f.read().split(",")
note_state = {"note_no": 0}

# Game setup
pygame.init()
pygame.midi.init()
midi_out = pygame.midi.Output(0)
midi_out.set_instrument(9)


clock = pygame.time.Clock()

background_color = (30, 30, 30)
space = pymunk.Space()
space.gravity = (0, g)
space.iterations = 30

# Screen properties
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bouncy balls")


def get_midi(note):
    return NOTES[note]


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

        self.shape.ball = self

        self.shape.collision_type = BALL_COLLISION_TYPE
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
        segment.collision_type = STATIC_COLLISION_TYPE
        space.add(segment)

    return segments


def on_ball_static_collision(arbiter, space, data):
    note = get_next_note()
    velocity = 127
    midi_out.note_on(note, velocity)
    return True


def on_ball_ball_collision(arbiter, space, data):
    global balls
    ball1 = arbiter.shapes[0].ball
    ball2 = arbiter.shapes[1].ball
    if all(ball1.color == ball2.color):
        # Remove both balls from the simulation.
        space.remove(ball1.body, ball1.shape)
        space.remove(ball2.body, ball2.shape)
        if ball1 in balls:
            balls.remove(ball1)
        if ball2 in balls:
            balls.remove(ball2)
    else:

        cp_set = arbiter.contact_point_set
        contact_point = cp_set.points[0].point_a

        normal = cp_set.normal
        offset = normal * ball1.radius * 3
        new_position = contact_point + offset

        new_velocity = offset * 10
        new_ball = Ball(space, new_position, new_velocity, ball1.radius, ball1.color)
        balls.append(new_ball)
    return True


container_centre = pymunk.Vec2d(width / 2, height / 2)
container_radius = 280
container_segments = create_container(space, container_centre, container_radius)


ball_static_handler = space.add_collision_handler(
    BALL_COLLISION_TYPE, STATIC_COLLISION_TYPE
)
ball_static_handler.begin = on_ball_static_collision

ball_ball_handler = space.add_collision_handler(
    BALL_COLLISION_TYPE, BALL_COLLISION_TYPE
)
ball_ball_handler.begin = on_ball_ball_collision

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


def get_rand_color(colors, variation=0):
    if not colors:
        colors = possible_colors.copy()

    color = random.choice(colors)
    colors.remove(color)
    color = np.array(color)
    if variation:
        color += np.random.randint(-variation, variation, 3)
        color = color.clip(0, 255)

    return color


def get_next_note():
    note = get_midi(song[note_state["note_no"]])
    note_state["note_no"] += 1
    return note


balls = [
    Ball(
        space,
        pos=(400, 80),
        vel=(0, 0),
        radius=BALL_SIZE,
        color=get_rand_color(possible_colors),
    ),
    Ball(
        space,
        pos=(300, 120),
        vel=(0, 0),
        radius=BALL_SIZE,
        color=get_rand_color(possible_colors),
    ),
    Ball(
        space,
        pos=(500, 106),
        vel=(0, 0),
        radius=BALL_SIZE,
        color=get_rand_color(possible_colors),
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

del midi_out
pygame.midi.quit()
pygame.quit()
sys.exit()
