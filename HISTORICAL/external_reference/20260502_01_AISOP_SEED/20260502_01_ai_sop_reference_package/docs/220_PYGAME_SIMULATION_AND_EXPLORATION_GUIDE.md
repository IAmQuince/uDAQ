---
document_id: DOC-220
title: "Pygame Simulation and Exploration Guide"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-220
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# Pygame Simulation and Exploration Guide

220_PYGAME_SIMULATION_AND_EXPLORATION_GUIDE
0. Purpose
This document explains how we use Pygame as a practical simulation and exploration environment.
It is based on the style of projects we have built before, including the “rain game” style simulation where:
* dots of rain fall across the screen;
* a movable block/player interacts with the rain;
* collisions are counted;
* rain speed can be adjusted;
* rain direction can be adjusted;
* density can be changed;
* experiments can be run repeatedly;
* the user can observe patterns visually instead of only reading numbers.
The goal is not just to make games.
The goal is to create small interactive laboratories where the user can explore a simulated situation by changing parameters and watching what happens.
Pygame is well suited for this because it gives direct control over:
* the main loop;
* screen drawing;
* keyboard input;
* mouse input;
* timing;
* sprites/objects;
* collision detection;
* simple physics;
* random particle systems;
* visual feedback;
* score/counter displays.
The official Pygame documentation describes Pygame as a Python package built around multimedia modules, with a typical quick-start pattern of opening a window, handling events, updating the screen, and controlling the main loop. (Pygame) Pygame’s introductory docs also describe it as a Python wrapper around SDL, which provides cross-platform multimedia access for video, input, sound, and related functionality. (Pygame)

1. Core Philosophy
A Pygame simulation should be treated as an interactive experiment.
The user should be able to ask:
What happens if I increase the rain speed?
What happens if I change the direction?
What happens if I increase particle density?
What happens if the player block gets bigger?
What happens if the screen is wider?
What happens if gravity changes?
What happens if particles bounce instead of disappear?
What happens if I run the same scenario for 60 seconds?

The program should make those questions easy to explore.
The best Pygame simulations are:
* visual;
* adjustable;
* responsive;
* measurable;
* restartable;
* instrumented;
* easy to modify;
* not over-architected too early.
The simulation should not only show motion.
It should expose variables, counts, rates, collisions, and conditions so the user can learn from the behavior.

2. When to Use Pygame
Use Pygame when the project needs:
* 2D visual simulation;
* moving objects;
* collisions;
* interactive controls;
* quick experimental feedback;
* keyboard/mouse interaction;
* particle systems;
* games;
* visual teaching tools;
* exploratory physics;
* simple animations;
* cellular/agent simulations;
* toy models of real systems;
* rapid prototyping without a heavy GUI framework.
Good Pygame project examples:
rain collision simulator
particle interaction sandbox
orbiting-particle simulation
falling-object game
wind/rain exposure model
simple fluid-like particle toy
2D robot/agent arena
cellular automaton viewer
sorting/pathfinding visualizer
touchscreen visual toy
reaction-diffusion style prototype
electric/magnetic field toy model

Do not use Pygame as the first choice when the project mainly needs:
* complex forms;
* many dockable panels;
* tables;
* professional data entry;
* database administration;
* many menus/settings dialogs;
* long-term engineering DAQ interface;
* native desktop widgets.
For those, use PyQt/Tkinter/Kivy/other GUI frameworks.
Pygame is best when the main thing is the animated simulation canvas.

3. Installation
Modern Python:
python -m pip install pygame

Linux/Raspberry Pi:
python3 -m pip install pygame

Check install:
python -m pygame.examples.aliens

or:
import pygame
print(pygame.version.ver)

Important compatibility notes:
* Modern Pygame no longer supports Python 2; the Pygame getting-started page notes that Pygame has dropped Python 2 support. (Pygame)
* For old Windows XP / Python 2.7 work, do not assume current Pygame installs. Use old known-good installers or already-installed legacy versions.
* For Android/Pydroid, Pygame may work in some cases, but touch/display behavior must be tested directly on the device.
* For Raspberry Pi, performance depends on Pi model, display, resolution, and graphics stack.

4. Basic Pygame Concepts
4.1 Display Surface
The display surface is the main window/canvas.
screen = pygame.display.set_mode((width, height))

You draw onto this surface each frame.
4.2 Game Loop / Simulation Loop
The loop usually does this:
handle input
update simulation state
detect collisions
record measurements
draw everything
update display
limit frame rate

Pygame gives the programmer direct control over the loop. That is powerful, but it also means timing, events, and redraws must be handled deliberately. (Pygame)
4.3 Events
Events include:
window close
key press
key release
mouse movement
mouse click
custom timer events

Example:
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        running = False

4.4 Clock / FPS
Use a clock to control frame rate:
clock = pygame.time.Clock()
dt = clock.tick(60) / 1000.0

dt is elapsed time in seconds since the last frame.
Use dt so movement is time-based rather than frame-based.
Bad:
y += 5

Better:
y += speed_pixels_per_second * dt

4.5 Rects
Pygame Rect objects are rectangular position/size objects used for:
* drawing;
* collision detection;
* movement;
* boundaries.
Example:
player_rect = pygame.Rect(100, 100, 80, 40)
rain_rect = pygame.Rect(200, 0, 4, 12)

if player_rect.colliderect(rain_rect):
    hit_count += 1

The Pygame guide notes that rectangular collision detection is usually much faster and often good enough for practical games/simulations compared with more expensive exact masks. (Scuba)

5. Standard Simulation Structure
Use this structure for most Pygame simulations:
project_name/
├── README_START_HERE.md
├── RUN_INSTRUCTIONS.md
├── main.py
├── config/
│   └── default_settings.json
├── data/
│   └── experiment_results.csv
├── screenshots/
├── logs/
└── docs/
    └── SIMULATION_NOTES.md

For a one-file prototype:
rain_simulation.py

Inside the file, use sections:
1. Imports
2. Constants
3. Utility functions
4. Data classes / object models
5. Simulation state
6. Input handling
7. Physics/update logic
8. Collision logic
9. Drawing/rendering
10. Metrics/logging
11. Main loop

Even in a monolithic prototype, keep the structure visible.

6. Minimal Pygame Skeleton
import sys
import pygame

def main():
    pygame.init()

    screen_width = 1000
    screen_height = 700

    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Pygame Simulation Skeleton")

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((10, 10, 20))

        pygame.display.flip()

    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())

This creates a window, handles close events, limits frame rate, and redraws the screen.

7. Rain Simulation Concept
The rain simulator has these objects:
Player/block:
    x, y, width, height, speed

Raindrop:
    x, y, vx, vy, width, height, active/alive

Simulation:
    list of raindrops
    spawn rate
    rain speed
    rain angle
    hit count
    elapsed time
    controls/settings

The core update loop:
spawn new drops
read player input
move player
move rain
check rain/player collisions
count hits
remove or recycle drops
draw frame
display metrics

8. Complete Rain Simulation Example
This is a complete starting point.
It includes:
* movable player block;
* falling rain particles;
* adjustable rain speed;
* adjustable wind/direction;
* adjustable spawn rate;
* hit counter;
* reset key;
* pause key;
* resizable window;
* simple on-screen help;
* CSV logging at the end.
import csv
import math
import os
import random
import sys
import time

import pygame

# =============================================================================
# 1. CONSTANTS
# =============================================================================

APP_NAME = "Rain Exposure Simulation"
APP_VERSION = "20260502_00_pygame_rain_sim"

DEFAULT_WIDTH = 1100
DEFAULT_HEIGHT = 720
FPS = 60

BACKGROUND = (10, 12, 20)
PLAYER_COLOR = (80, 180, 255)
RAIN_COLOR = (120, 170, 255)
TEXT_COLOR = (230, 235, 245)
HIT_COLOR = (255, 100, 80)

DATA_DIR = "data"
RESULTS_CSV = os.path.join(DATA_DIR, "rain_sim_results.csv")

# =============================================================================
# 2. HELPERS
# =============================================================================

def safe_makedirs(path):
    if path and not os.path.isdir(path):
        os.makedirs(path)

def clamp(value, low, high):
    return max(low, min(high, value))

def now_string():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def draw_text(surface, font, text, x, y, color=TEXT_COLOR):
    img = font.render(text, True, color)
    surface.blit(img, (x, y))

# =============================================================================
# 3. DATA OBJECTS
# =============================================================================

class Player(object):
    def __init__(self, x, y, width=90, height=45):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = 420.0

    def update(self, dt, keys, bounds_rect):
        dx = 0.0
        dy = 0.0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed * dt

        self.rect.x += int(dx)
        self.rect.y += int(dy)

        self.rect.clamp_ip(bounds_rect)

    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect, border_radius=6)

class Raindrop(object):
    def __init__(self, x, y, vx, vy, width=4, height=14):
        self.rect = pygame.Rect(int(x), int(y), width, height)
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.alive = True
        self.hit = False

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, surface):
        color = HIT_COLOR if self.hit else RAIN_COLOR
        pygame.draw.rect(surface, color, self.rect)

class SimulationState(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.player = Player(width // 2 - 45, height - 100)
        self.raindrops = []

        self.spawn_rate_per_second = 80.0
        self.rain_speed = 360.0
        self.wind_speed = 0.0
        self.drop_width = 4
        self.drop_height = 14

        self.hit_count = 0
        self.spawned_count = 0
        self.elapsed_time = 0.0
        self.paused = False

        self.spawn_accumulator = 0.0
        self.experiment_started_at = now_string()

    def reset(self):
        width = self.width
        height = self.height
        self.__init__(width, height)

    def resize(self, width, height):
        self.width = width
        self.height = height
        bounds = pygame.Rect(0, 0, width, height)
        self.player.rect.clamp_ip(bounds)

# =============================================================================
# 4. SIMULATION LOGIC
# =============================================================================

def spawn_raindrop(state):
    x = random.randint(-50, state.width + 50)
    y = -20

    vx = state.wind_speed
    vy = state.rain_speed

    drop = Raindrop(
        x=x,
        y=y,
        vx=vx,
        vy=vy,
        width=state.drop_width,
        height=state.drop_height,
    )

    state.raindrops.append(drop)
    state.spawned_count += 1

def update_spawning(state, dt):
    state.spawn_accumulator += state.spawn_rate_per_second * dt

    while state.spawn_accumulator >= 1.0:
        spawn_raindrop(state)
        state.spawn_accumulator -= 1.0

def update_raindrops(state, dt):
    for drop in state.raindrops:
        drop.update(dt)

    margin = 100
    state.raindrops = [
        d for d in state.raindrops
        if d.rect.y < state.height + margin
        and d.rect.x > -margin
        and d.rect.x < state.width + margin
        and not d.hit
    ]

def handle_collisions(state):
    for drop in state.raindrops:
        if not drop.hit and state.player.rect.colliderect(drop.rect):
            drop.hit = True
            state.hit_count += 1

def update_simulation(state, dt):
    if state.paused:
        return

    state.elapsed_time += dt

    keys = pygame.key.get_pressed()
    bounds = pygame.Rect(0, 0, state.width, state.height)

    state.player.update(dt, keys, bounds)
    update_spawning(state, dt)
    update_raindrops(state, dt)
    handle_collisions(state)

# =============================================================================
# 5. INPUT HANDLING
# =============================================================================

def handle_keydown(event, state):
    if event.key == pygame.K_SPACE:
        state.paused = not state.paused

    elif event.key == pygame.K_r:
        state.reset()

    elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
        state.rain_speed += 40.0

    elif event.key == pygame.K_MINUS:
        state.rain_speed = max(40.0, state.rain_speed - 40.0)

    elif event.key == pygame.K_RIGHTBRACKET:
        state.spawn_rate_per_second += 10.0

    elif event.key == pygame.K_LEFTBRACKET:
        state.spawn_rate_per_second = max(1.0, state.spawn_rate_per_second - 10.0)

    elif event.key == pygame.K_PERIOD:
        state.wind_speed += 40.0

    elif event.key == pygame.K_COMMA:
        state.wind_speed -= 40.0

    elif event.key == pygame.K_0:
        state.wind_speed = 0.0

# =============================================================================
# 6. DRAWING
# =============================================================================

def draw_hud(screen, font, state, fps):
    lines = [
        "%s  |  %s" % (APP_NAME, APP_VERSION),
        "Time: %.1f s   FPS: %.1f   Paused: %s" % (state.elapsed_time, fps, state.paused),
        "Hits: %d   Spawned: %d   Active drops: %d" % (
            state.hit_count,
            state.spawned_count,
            len(state.raindrops),
        ),
        "Rain speed: %.0f px/s   Wind: %.0f px/s   Spawn rate: %.0f drops/s" % (
            state.rain_speed,
            state.wind_speed,
            state.spawn_rate_per_second,
        ),
        "Move: WASD/arrows | Space pause | R reset | +/- speed | [/ ] density | ,/. wind | 0 no wind",
    ]

    y = 10
    for line in lines:
        draw_text(screen, font, line, 12, y)
        y += 22

def draw_simulation(screen, font, state, fps):
    screen.fill(BACKGROUND)

    for drop in state.raindrops:
        drop.draw(screen)

    state.player.draw(screen)

    draw_hud(screen, font, state, fps)

    if state.paused:
        large_font = pygame.font.SysFont("arial", 48)
        text = large_font.render("PAUSED", True, TEXT_COLOR)
        rect = text.get_rect(center=(state.width // 2, state.height // 2))
        screen.blit(text, rect)

# =============================================================================
# 7. RESULTS LOGGING
# =============================================================================

def save_experiment_result(state):
    safe_makedirs(DATA_DIR)

    file_exists = os.path.isfile(RESULTS_CSV)

    with open(RESULTS_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "saved_at",
            "experiment_started_at",
            "elapsed_time_s",
            "hit_count",
            "spawned_count",
            "rain_speed_px_s",
            "wind_speed_px_s",
            "spawn_rate_per_s",
            "window_width",
            "window_height",
        ])

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "saved_at": now_string(),
            "experiment_started_at": state.experiment_started_at,
            "elapsed_time_s": "%.3f" % state.elapsed_time,
            "hit_count": state.hit_count,
            "spawned_count": state.spawned_count,
            "rain_speed_px_s": "%.3f" % state.rain_speed,
            "wind_speed_px_s": "%.3f" % state.wind_speed,
            "spawn_rate_per_s": "%.3f" % state.spawn_rate_per_second,
            "window_width": state.width,
            "window_height": state.height,
        })

# =============================================================================
# 8. MAIN LOOP
# =============================================================================

def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (DEFAULT_WIDTH, DEFAULT_HEIGHT),
        pygame.RESIZABLE
    )

    pygame.display.set_caption(APP_NAME)

    font = pygame.font.SysFont("consolas", 18)
    clock = pygame.time.Clock()

    state = SimulationState(DEFAULT_WIDTH, DEFAULT_HEIGHT)

    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        fps = clock.get_fps()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                width, height = event.size
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                state.resize(width, height)

            elif event.type == pygame.KEYDOWN:
                handle_keydown(event, state)

        update_simulation(state, dt)
        draw_simulation(screen, font, state, fps)

        pygame.display.flip()

    save_experiment_result(state)
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())

9. How to Think About the Rain Game Scientifically
The rain game can be treated as a simple exposure model.
The block represents:
a person
a vehicle
a collector
a target surface
a sensor
an object moving through an environment

The raindrops represent:
rain
particles
debris
radiation events
falling hazards
random impacts
projectiles
sampling events

Variables:
block size
block speed
rain density
rain speed
rain direction
wind speed
screen size
spawn distribution
collision rule

Measurements:
hit count
hit rate
hits per second
hits per distance moved
exposure per unit area
average drop lifetime
active particle count
miss rate

Experiments:
Run 1:
    rain speed = 300
    wind = 0
    spawn rate = 80

Run 2:
    rain speed = 600
    wind = 0
    spawn rate = 80

Run 3:
    rain speed = 300
    wind = 200
    spawn rate = 80

Then compare:
Does wind increase hits?
Does faster rain increase hit rate?
Does moving sideways help?
Does a wider block collect proportionally more drops?

This is the basic philosophy: use Pygame as an interactive experimental system.

10. Common Simulation Parameters
Every simulation should define adjustable parameters clearly.
params = {
    "particle_count": 500,
    "spawn_rate": 80,
    "gravity": 300,
    "wind": 0,
    "drag": 0.0,
    "bounce": False,
    "collision_enabled": True,
    "player_speed": 420,
}

Better for larger projects:
class SimulationParams(object):
    def __init__(self):
        self.spawn_rate = 80.0
        self.rain_speed = 360.0
        self.wind_speed = 0.0
        self.player_speed = 420.0
        self.drop_width = 4
        self.drop_height = 14
        self.gravity = 0.0
        self.collision_enabled = True

The user should be able to modify parameters through:
* keyboard shortcuts;
* sliders;
* config file;
* GUI overlay;
* command-line flags;
* saved scenario files.

11. Adding Sliders or On-Screen Controls
Pygame does not provide native GUI widgets like PyQt, but simple sliders can be built.
class Slider(object):
    def __init__(self, x, y, width, label, min_value, max_value, value):
        self.rect = pygame.Rect(x, y, width, 20)
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.set_from_mouse(event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.set_from_mouse(event.pos[0])

    def set_from_mouse(self, mouse_x):
        t = (mouse_x - self.rect.x) / float(self.rect.width)
        t = max(0.0, min(1.0, t))
        self.value = self.min_value + t * (self.max_value - self.min_value)

    def draw(self, surface, font):
        pygame.draw.rect(surface, (80, 80, 100), self.rect)
        t = (self.value - self.min_value) / float(self.max_value - self.min_value)
        knob_x = self.rect.x + int(t * self.rect.width)
        pygame.draw.circle(surface, (220, 220, 255), (knob_x, self.rect.centery), 8)

        label = "%s: %.1f" % (self.label, self.value)
        img = font.render(label, True, (230, 235, 245))
        surface.blit(img, (self.rect.x, self.rect.y - 22))

Use sliders when the simulation is meant for exploratory tuning.

12. Collision Detection Patterns
12.1 Rect collision
Fast and simple:
if player.rect.colliderect(drop.rect):
    hit_count += 1

Use for:
* boxes;
* simple games;
* many particles;
* approximate collision.
12.2 Circle collision
For circular particles:
def circles_collide(x1, y1, r1, x2, y2, r2):
    dx = x2 - x1
    dy = y2 - y1
    return dx * dx + dy * dy <= (r1 + r2) * (r1 + r2)

Avoid square roots for speed.
12.3 Spatial partitioning
If particle count gets large, checking every particle against every other particle becomes slow.
Naive pair check:
O(n²)

Better options:
grid buckets
quadtree
only check nearby objects

For many rain drops against one player block, naive collision is fine.
For many particles interacting with many particles, use spatial partitioning.

13. Particle System Pattern
A particle system usually has:
spawn
update
collide
draw
remove/recycle
measure

Generic particle:
class Particle(object):
    def __init__(self, x, y, vx, vy, radius=3):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.radius = radius
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            (180, 220, 255),
            (int(self.x), int(self.y)),
            self.radius
        )

Useful for:
* rain;
* sparks;
* stars;
* molecules;
* dust;
* Brownian motion;
* particle fields;
* simple orbit simulations.

14. Physics Update Pattern
Use force/acceleration if needed:
class Body(object):
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.ax = 0.0
        self.ay = 0.0

    def update(self, dt):
        self.vx += self.ax * dt
        self.vy += self.ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

Gravity:
body.ay = 500.0

Drag:
body.vx *= 0.99
body.vy *= 0.99

Bounce from walls:
if body.x < 0 or body.x > width:
    body.vx *= -1

Use simple physics unless the simulation specifically needs a real physics engine.

15. Data Logging
Every exploratory simulation should be able to record results.
Minimum experiment row:
timestamp
app_version
elapsed_time
parameter values
counts
rates
notes

Example CSV writer:
def append_result_csv(path, row):
    folder = os.path.dirname(os.path.abspath(path))
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)

    file_exists = os.path.isfile(path)

    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(row.keys()))

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)

Use data logging when the simulation is meant to compare scenarios.

16. Screenshots
Add screenshot capture:
def save_screenshot(screen, folder="screenshots"):
    if not os.path.isdir(folder):
        os.makedirs(folder)

    filename = time.strftime("screenshot_%Y%m%d_%H%M%S.png")
    path = os.path.join(folder, filename)
    pygame.image.save(screen, path)
    return path

Handle key:
elif event.key == pygame.K_F12:
    path = save_screenshot(screen)
    print("Saved screenshot:", path)

Screenshots are useful for:
* documenting experiments;
* debugging layouts;
* sharing visual results;
* comparing simulation states.

17. Scenario Files
For repeatable experiments, save/load scenario JSON.
{
  "name": "high_wind_high_density",
  "rain_speed": 420.0,
  "wind_speed": 180.0,
  "spawn_rate_per_second": 120.0,
  "player_width": 90,
  "player_height": 45
}

Load:
import json

def load_scenario(path):
    with open(path, "r") as f:
        return json.load(f)

def apply_scenario(state, scenario):
    state.rain_speed = float(scenario.get("rain_speed", state.rain_speed))
    state.wind_speed = float(scenario.get("wind_speed", state.wind_speed))
    state.spawn_rate_per_second = float(
        scenario.get("spawn_rate_per_second", state.spawn_rate_per_second)
    )

This is how a game-like toy becomes a repeatable simulation tool.

18. Time Control
Useful simulation time controls:
pause
single-step
slow motion
fast forward
reset
fixed random seed

Fixed seed:
random.seed(12345)

Single-step idea:
if paused and step_requested:
    update_simulation(state, fixed_dt)

Use this when debugging collisions or teaching cause/effect.

19. Randomness and Reproducibility
Randomness makes simulations interesting but can make experiments hard to compare.
Use a seed:
random.seed(42)

Record the seed in results:
seed = 42

Then another user can reproduce the same rain pattern or particle layout.
For exploratory mode, use random seeds.
For comparison mode, fix the seed.

20. Performance Rules
Common performance problems:
too many particles
drawing too much text every frame
loading images inside the loop
checking every particle against every other particle
using per-pixel collision when rect collision is enough
printing every frame
not limiting FPS

Rules:
Load images once.
Create fonts once.
Use clock.tick(FPS).
Use dt-based motion.
Use Rect collision first.
Limit active particles.
Use spatial partitioning if needed.
Avoid console spam during live loop.

FPS display:
fps = clock.get_fps()

21. Pygame on Raspberry Pi
Use Pygame on Raspberry Pi when:
* the visual simulation is simple;
* the display is local;
* touchscreen or keyboard interaction is needed;
* performance requirements are modest.
Be careful with:
* high resolution;
* thousands of particles;
* alpha blending;
* image scaling every frame;
* heavy logging;
* expensive collision checks.
Start with:
800x480 for small touchscreens
30 or 60 FPS depending on Pi model
simple shapes before images

22. Pygame on Android / Pydroid
Pydroid/Pygame work should be treated as target-specific.
Do not assume:
* keyboard exists;
* mouse behavior matches desktop;
* screen orientation stays fixed;
* file paths match desktop;
* performance matches PC;
* window resizing behaves normally.
For mobile, prefer:
touch controls
large buttons
simple drawing
lower particle count
clear exit button
diagnostic log output

23. Windows XP / Legacy Pygame
Modern Pygame does not target Python 2, so XP/Python 2.7 projects require old installers or old known-good environments.
Rules:
Do not use current pip install pygame on XP/Python 2.7.
Do not use Python 3-only syntax.
Avoid pathlib, dataclasses, f-strings, type annotations.
Use old Pygame docs/installers if working in that environment.
Test with the actual XP machine.

For XP, keep simulations simple:
one file
no modern dependencies
small resolution
basic shapes
simple CSV logging
batch launcher

24. UI Design for Pygame Simulations
Pygame UIs should not try to imitate full desktop apps.
Good Pygame UI:
large simulation canvas
small HUD overlay
keyboard shortcuts
simple clickable controls
pause/reset buttons
parameter sliders if needed
help overlay
screenshot key
results logging

Avoid:
complex menus
large forms
spreadsheet-like tables
many nested panels
tiny controls
heavy text input

For large configuration screens, use JSON config files or a separate GUI tool.

25. Standard Controls
Suggested default controls:
Esc / window close:
    quit safely

Space:
    pause/resume

R:
    reset simulation

S:
    save screenshot or save state

F12:
    screenshot

Arrow keys / WASD:
    move player/camera/object

+ / -:
    increase/decrease primary speed

[ / ]:
    decrease/increase density/count

, / .:
    decrease/increase wind/direction

0:
    reset wind/parameter

H:
    toggle help overlay

D:
    toggle debug overlay

L:
    toggle logging

Document controls on screen.

26. Diagnostics for Pygame Projects
Add a diagnostic mode for serious Pygame simulations.
Report:
Python version
Pygame version
OS/platform
screen size
display driver if known
current FPS
particle count
target FPS
data path
screenshot path
log path
last exception

Example:
def write_diagnostic_report(path, state, fps):
    lines = []
    lines.append("PYGAME SIMULATION DIAGNOSTIC")
    lines.append("=" * 72)
    lines.append("timestamp: %s" % now_string())
    lines.append("app: %s" % APP_NAME)
    lines.append("version: %s" % APP_VERSION)
    lines.append("python: %s" % sys.version)
    lines.append("pygame: %s" % pygame.version.ver)
    lines.append("fps: %.2f" % fps)
    lines.append("window: %sx%s" % (state.width, state.height))
    lines.append("active_raindrops: %s" % len(state.raindrops))
    lines.append("hit_count: %s" % state.hit_count)

    folder = os.path.dirname(os.path.abspath(path))
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)

    with open(path, "w") as f:
        f.write("\n".join(lines))

27. Project Progression
A Pygame simulation often evolves through these phases.
Phase 0 — Toy prototype
Draw shapes.
Move one object.
Spawn particles.
Count collisions.

Phase 1 — Experiment controls
Add keyboard controls.
Add parameters.
Add reset.
Add pause.
Add HUD.

Phase 2 — Measurement
Log results.
Show rates.
Save screenshots.
Save scenario configs.

Phase 3 — More realistic model
Add acceleration.
Add wind.
Add drag.
Add bouncing.
Add object interactions.
Add distributions.

Phase 4 — Analysis
Batch runs.
Repeat with fixed seeds.
Compare CSV results.
Plot hit rate vs parameter.

Phase 5 — Formal package
Split into modules.
Add docs.
Add test scripts.
Add diagnostics.
Add examples.

Do not jump to Phase 5 before the behavior is understood.

28. Suggested Module Structure for Formal Pygame Simulation
pygame_sim_project/
├── README_START_HERE.md
├── RUN_INSTRUCTIONS.md
├── main.py
├── requirements.txt
├── config/
│   └── default_scenario.json
├── data/
├── screenshots/
├── docs/
│   ├── SIMULATION_MODEL.md
│   ├── CONTROLS.md
│   └── EXPERIMENT_PLAN.md
└── sim/
    ├── __init__.py
    ├── constants.py
    ├── state.py
    ├── objects.py
    ├── physics.py
    ├── collisions.py
    ├── input.py
    ├── rendering.py
    ├── logging_utils.py
    └── diagnostics.py

Module responsibilities:
state.py:
    SimulationState and parameters.

objects.py:
    Player, particle, obstacle, target classes.

physics.py:
    Movement, forces, integration.

collisions.py:
    Collision tests and responses.

input.py:
    Keyboard/mouse/touch handling.

rendering.py:
    Drawing and HUD.

logging_utils.py:
    CSV results, screenshots, scenario save/load.

diagnostics.py:
    Pygame/environment reports.

29. Acceptance Tests for Pygame Simulations
Even playful simulations need basic acceptance checks.
ACCEPT-PYGAME-001
Test:
Launch the simulation.

Expected:
Window opens, no immediate crash, close button works.

ACCEPT-PYGAME-002
Test:
Move the player with keyboard.

Expected:
Player moves and stays inside screen bounds.

ACCEPT-PYGAME-003
Test:
Rain spawns and moves.

Expected:
Particles appear, move, and are removed/recycled.

ACCEPT-PYGAME-004
Test:
Collision count increments.

Expected:
When raindrop intersects block, hit count increases once.

ACCEPT-PYGAME-005
Test:
Parameter controls work.

Expected:
Speed, density, wind, or chosen parameters visibly change behavior.

ACCEPT-PYGAME-006
Test:
Pause/reset work.

Expected:
Pause freezes simulation update. Reset clears counts and particles.

ACCEPT-PYGAME-007
Test:
CSV logging works.

Expected:
Result row is written at exit or on save.

ACCEPT-PYGAME-008
Test:
Resizable window works.

Expected:
Simulation remains usable after resize.

ACCEPT-PYGAME-009
Test:
Diagnostic report works.

Expected:
Report includes Python/Pygame version, screen size, FPS, particle count.

ACCEPT-PYGAME-010
Test:
Performance remains acceptable.

Expected:
FPS stays above target threshold at expected particle count.

30. Common Problems and Fixes
30.1 Window opens and immediately closes
Cause:
No persistent main loop.
Script reaches end immediately.

Fix:
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

30.2 Window stops responding
Cause:
Events are not being processed.
Long blocking operation inside main loop.

Fix:
Call pygame.event.get() every frame.
Move slow file/network operations outside frame loop or make them incremental.

30.3 Movement speed changes with FPS
Cause:
Frame-based movement instead of time-based movement.

Fix:
dt = clock.tick(FPS) / 1000.0
x += speed * dt

30.4 Too slow with many particles
Cause:
Too many objects, too much drawing, or too many collision checks.

Fix:
Limit particle count.
Use rect collisions.
Avoid per-pixel operations.
Use spatial partitioning.
Draw simple shapes.
Reduce resolution.

30.5 Collisions count too many times
Cause:
Same particle collides across multiple frames.

Fix:
if not drop.hit and player.rect.colliderect(drop.rect):
    drop.hit = True
    hit_count += 1

30.6 Flickering
Cause:
Not clearing screen consistently or drawing in odd order.

Fix:
Clear background.
Draw simulation objects.
Draw UI/HUD.
Flip display once.

30.7 Fonts slow things down
Cause:
Creating fonts every frame.

Fix:
Create fonts once before the loop.
Render only necessary text.

31. Pygame Simulation Design Checklist
Before coding:
[ ] What is being simulated?
[ ] What does each object represent?
[ ] What variables should the user control?
[ ] What should be measured?
[ ] What counts as a collision/event?
[ ] What should be logged?
[ ] What controls are needed?
[ ] What screen size is expected?
[ ] What performance target is needed?
[ ] Is randomness fixed or variable?

Before packaging:
[ ] Run instructions exist.
[ ] Controls are documented.
[ ] Simulation variables are documented.
[ ] CSV/logging behavior is documented.
[ ] Screenshots folder works.
[ ] Diagnostics work.
[ ] Known limitations are listed.
[ ] Pygame version is recorded.

32. Core Rules
RULE-PYGAME-001
Use Pygame when the simulation canvas is the main interface.

RULE-PYGAME-002
Every simulation should have a clear loop:
input → update → collide → measure → draw.

RULE-PYGAME-003
Use dt-based movement, not frame-based movement.

RULE-PYGAME-004
Treat adjustable parameters as first-class design elements.

RULE-PYGAME-005
Separate raw simulation state from rendered pixels.

RULE-PYGAME-006
Do not let playful visuals prevent measurement and logging.

RULE-PYGAME-007
Use simple collision first.

RULE-PYGAME-008
Use fixed seeds when comparing scenarios.

RULE-PYGAME-009
Add pause, reset, screenshot, and diagnostics early.

RULE-PYGAME-010
A good Pygame simulation is an interactive experiment, not just animation.

33. Closing Principle
Pygame is valuable because it lets us turn an idea into something we can see, touch, tune, and measure quickly.
For our style of work, Pygame is best used as:
a visual thought experiment
a toy physics lab
a teaching tool
a rapid simulation canvas
a way to discover behavior before formalizing architecture

The rain game is the basic pattern:
objects move
rules govern interaction
the user changes parameters
the program counts what happens
the visual result teaches intuition
the saved data supports comparison

That is the model to reuse.

LabJackPython
