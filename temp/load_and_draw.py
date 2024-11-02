import pygame, sys, time, numpy as np

from typing import List


class Line:
    def __init__(self, step: str, bpm: int, delay: int, beat: int, split: int):
        self.step = step
        self.bpm = bpm
        self.delay = delay
        self.beat = beat
        self.split = split

    def __str__(self):
        return self.step


pygame.init()

screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

# color
white = (255, 255, 255)
black = (0, 0, 0)
light_gray = (200, 200, 200)
dark_gray = (169, 169, 169)

cell_size = 76
rows, cols = 0, 0

# scroll
scr_y = 0
scr_speed = 20

# Initial Rectangle Location
square_x = -100
square_y = -100

# Total Grid Height
grid_height = 0

# Square Movement Speed
delay = 500

# Key pressing time
square_keys = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0, pygame.K_UP: 0, pygame.K_DOWN: 0}

# Image Load
short_images = [
    pygame.image.load(f"./images/note{i % 5}.png").convert_alpha() for i in range(10)
]
long_head_images = [
    pygame.image.load(f"./images/start{i % 5}.png").convert_alpha() for i in range(10)
]
long_middle_images = [
    pygame.image.load(f"./images/hold{i % 5}.png").convert_alpha() for i in range(10)
]
long_tail_images = [
    pygame.image.load(f"./images/end{i % 5}.png").convert_alpha() for i in range(10)
]

image_rects = dict()


# lines = []
step_data: List[Line] = []


format = -1
mode = ""

blocks = []
lines = []
y_coors = []

block_idx, y_coor = 0, 0
initial_bpm, bpm, delay, beat, split, lcnt = 0, 0, 0, 0, 0, 0
with open("sample.ucs", "r") as f:
    file_lines = f.readlines()

    ln, tot_ln = 2, len(file_lines)

    try:
        assert file_lines[0].startswith(":Format=") and file_lines[1].startswith(
            ":Mode="
        ), "Invalid UCS Header"

        format = int(file_lines[0].strip().split("=")[1])
        mode = file_lines[1].strip().split("=")[1]

        assert format == 1 and mode in ["Single", "Double"]

        if mode == "Single":
            cols = 5
        else:
            cols = 10

    except Exception as e:
        print(e)
        raise Exception("Failed to parse UCS Header")

    inital_bpm = bpm = round(float(file_lines[ln].strip().split("=")[1]), 4)
    delay = int(file_lines[ln + 1].strip().split("=")[1])
    beat = int(file_lines[ln + 2].strip().split("=")[1])
    split = int(file_lines[ln + 3].strip().split("=")[1])
    lcnt = 0
    ln += 4

    while ln < tot_ln:
        if file_lines[ln].startswith(":"):

            assert lcnt > 0, "Zero Size Block Occured at line {}".format(ln)
            assert (
                file_lines[ln].startswith(":BPM=")
                and file_lines[ln + 1].startswith(":Delay=")
                and file_lines[ln + 2].startswith(":Beat=")
                and file_lines[ln + 3].startswith(":Split=")
            ), "Invalid Block Header"

            bpm = round(float(file_lines[ln].split("=")[1]), 4)
            delay = int(file_lines[ln + 1].split("=")[1])
            beat = int(file_lines[ln + 1].split("=")[1])
            split = int(file_lines[ln + 1].split("=")[1])
            lcnt = 0
            ln += 4

        else:
            step_data.append(
                Line(
                    file_lines[ln].strip(), bpm, delay if lcnt == 0 else 0, beat, split
                )
            )
            lcnt += 1
            ln += 1


rows = len(step_data)
grid_height = rows * cell_size
step_x_offset = cell_size * 2


running = True

while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            is_scroll = True
            if event.button == 4:  # Mouse Wheel Up
                scr_y = max(scr_y - scr_speed, 0)
            elif event.button == 5:  # Mouse Wheel Down
                scr_y = min(scr_y + scr_speed, grid_height - screen_height)
            elif event.button == 1:  # Left Mouse Click
                mouse_x, mouse_y = event.pos
                grid_x = (mouse_x - step_x_offset) // cell_size
                grid_y = (mouse_y + scr_y) // cell_size

                if 0 <= grid_x < cols:
                    square_x = step_x_offset + grid_x * cell_size
                    square_y = grid_y * cell_size
            print(scr_y)

        elif event.type == pygame.KEYDOWN:
            is_scroll = False
            if event.key in square_keys:
                if event.key == pygame.K_LEFT:
                    square_x = max(square_x - cell_size, step_x_offset)
                if event.key == pygame.K_RIGHT:
                    square_x = min(
                        square_x + cell_size, step_x_offset + (cols - 1) * cell_size
                    )
                if event.key == pygame.K_UP:
                    square_y = max(square_y - cell_size, 0)
                if event.key == pygame.K_DOWN:
                    square_y = min(square_y + cell_size, (rows - 1) * cell_size)

            elif event.key == pygame.K_SPACE:
                selected_col = (square_x - step_x_offset) // cell_size
                if 0 <= selected_col < cols:
                    if (square_x, square_y) in image_rects:
                        del image_rects[(square_x, square_y)]
                    else:
                        image_rects[(square_x, square_y)] = short_images[selected_col]
            elif event.key == pygame.K_ESCAPE:
                square_x = (
                    -cell_size
                )  # Vanish selection square by moving it to out of the screen

    screen.fill(white)

    # Draw columns for step
    x_offset = 2 * cell_size
    for row in range(rows):
        y = row * cell_size - scr_y
        # print(scr_y, y)
        if -cell_size >= y or y >= screen_height:
            continue
        # print("hello")
        for col in range(cols):
            x = x_offset + col * cell_size
            pygame.draw.rect(screen, light_gray, (x, y, cell_size, cell_size), 1)

    # Draw columns for Measure

    # Draw columns for Measure Descriptor

    # Draw selected square
    pygame.draw.rect(
        screen, black, (square_x, square_y - scr_y, cell_size, cell_size), 1
    )

    for (x, y), image in image_rects.items():
        if -cell_size < y - scr_y < screen_height:
            screen.blit(image, (x, y - scr_y))

    pygame.display.flip()

    pygame.time.Clock().tick(30)
