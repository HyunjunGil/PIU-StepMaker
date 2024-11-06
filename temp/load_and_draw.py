import pygame, sys, time, numpy as np

from typing import List

step_to_code = {".": 0, "X": 1, "M": 2, "H": 3, "W": 4}
code_to_step = [".", "X", "M", "H", "W"]


pygame.init()

font = pygame.font.Font(None, 24)


screen_width, screen_height = 800, 1000
screen = pygame.display.set_mode((screen_width, screen_height))

# color
red = (255, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)
light_gray = (200, 200, 200)
dark_gray = (169, 169, 169)
royal_blue = (65, 105, 205)
light_green = (144, 238, 144)

cell_size = 76
min_split_size = 10
rows, cols = 0, 0

# scroll
scr_y = 0
scr_speed = 20

# Initial Selection Rectangle Location
square_selected = False
square_x = -100
square_y = -100

# Initial Hover Rectangle Location
hover_x = -100
hover_y = -100

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


# lines = []
block_info: List[int | float] = []
step_data: List[List[int]] = []
y_selection_map: List[List[int]] = [[0, 0] for i in range(100_000)]


format = -1
mode = ""

y_coors = []

block_idx, y_coor = 0, 0
initial_bpm, bpm, delay, beat, split, lcnt = 0, 0, 0, 0, 0, 0


def update_y_selection_map():
    global step_data, y_selection_map
    block_idx, measure, bpm, beat, split = -1, 0, 0, 0, 0
    y, ny = 0, 0
    tot_ln = len(step_data)
    for ln in range(tot_ln):
        row = step_data[ln]
        bi = row[5]
        if bi != block_idx:
            block = block_info[bi]
            bpm, beat, split, delay = block[0], block[1], block[2], block[3]

        line_height = max((cell_size * 2) // split, min_split_size)
        ny = y + line_height
        # print(ln, ny)
        for i in range(y, ny):
            y_selection_map[i][0] = ln
            y_selection_map[i][1] = y

        y = ny


def save_step():
    with open("result.ucs", "w") as f:
        f.write(":Format=1")
        f.write("Mode=" + "Single" if mode == "Single" else "Double")

        block_idx = -1
        for ln in range(len(step_data)):
            row = step_data[ln]
            bi = row[cols]
            if block_idx != bi:
                f.writelines(
                    [
                        f":BPM={row[cols + 1]}",
                        f":Delay={row[cols + 4]}",
                        f":Beat={row[cols + 2]}",
                        f":Split={row[cols + 3]}",
                    ]
                )
                block_idx = bi

            f.write(row["".join([code_to_step[c] for c in row[:cols]])])


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
    block_idx = 0
    lcnt = 0
    ln += 4
    block_info.append([bpm, beat, split, delay])

    while ln < tot_ln:
        if file_lines[ln].startswith(":"):

            assert lcnt > 0, "Zero Size Block Occured at line {}".format(ln)
            assert (
                file_lines[ln].startswith(":BPM=")
                and file_lines[ln + 1].startswith(":Delay=")
                and file_lines[ln + 2].startswith(":Beat=")
                and file_lines[ln + 3].startswith(":Split=")
            ), "Invalid Block Header"

            bpm = round(float(file_lines[ln].strip().split("=")[1]), 4)
            delay = int(file_lines[ln + 1].strip().split("=")[1])
            beat = int(file_lines[ln + 2].strip().split("=")[1])
            split = int(file_lines[ln + 3].strip().split("=")[1])
            block_info.append([bpm, beat, split, delay])
            block_idx += 1
            lcnt = 0
            ln += 4
            print(delay, beat, split)
        else:
            parsed_line = [step_to_code[c] for c in file_lines[ln].strip()] + [
                block_idx,  # block index
                lcnt // (beat * split),  # measure index
                lcnt // split,  # beat index
                lcnt % split,  # split index
            ]
            parsed_line.append(block_idx)
            step_data.append(parsed_line)
            lcnt += 1
            ln += 1

grid_height = len(step_data) * cell_size
step_x_start = cell_size * 2
step_x_end = cell_size * (2 + cols)
x_end = step_x_end + 2 * cell_size

# for i in range(20):
# print(step_data[i])

running = True

update_y_selection_map()

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
                grid_x = (mouse_x - step_x_start) // cell_size

                if 0 <= grid_x < cols:
                    square_selected = True
                    square_x = step_x_start + grid_x * cell_size
                    square_y = y_selection_map[mouse_y + scr_y][1]
            print(scr_y)

        elif event.type == pygame.KEYDOWN:
            is_scroll = False
            if event.key in square_keys and square_selected:
                if event.key == pygame.K_LEFT:
                    square_x = max(square_x - cell_size, step_x_start)
                elif event.key == pygame.K_RIGHT:
                    square_x = min(
                        square_x + cell_size, step_x_start + (cols - 1) * cell_size
                    )
                elif event.key == pygame.K_UP:
                    ln = y_selection_map[square_y][0]
                    if ln != 0:
                        split = block_info[step_data[ln - 1][5]][2]
                        dy = max((cell_size * 2) // split, min_split_size)
                        square_y -= dy
                elif event.key == pygame.K_DOWN:
                    ln = y_selection_map[square_y][0]
                    if ln != len(step_data) - 1:
                        split = block_info[step_data[ln][5]][2]
                        dy = max((cell_size * 2) // split, min_split_size)
                        square_y += dy

            # elif event.key == pygame.K_SPACE:
            #     selected_col = (square_x - step_x_start) // cell_size
            #     if 0 <= selected_col < cols:
            #         if (square_x, square_y) in image_rects:
            #             del image_rects[(square_x, square_y)]
            #         else:
            #             image_rects[(square_x, square_y)] = short_images[selected_col]

            #     grid_x = (square_x - step_x_start) // cell_size
            #     if 0 <= grid_x < cols:
            #         ln = y_selection_map[square_y + scr_y][0]
            #         step_data[ln][grid_x] = 1
            elif event.key == pygame.K_ESCAPE and square_selected:
                square_selected = False
                square_x = (
                    -cell_size
                )  # Vanish selection square by moving it to out of the screen

    if square_selected and not is_scroll:
        scr_y = min(max(scr_y, square_y + cell_size - screen_height), square_y)

    # Hover Sqaure
    mouse_x, mouse_y = pygame.mouse.get_pos()
    # mouse_x, mouse_y = event.pos
    grid_x = (mouse_x - step_x_start) // cell_size

    if 0 <= grid_x < cols:
        hover_x = step_x_start + grid_x * cell_size
        hover_y = y_selection_map[mouse_y + scr_y][1]
    else:
        hover_x = -100
        hover_y = -100

    screen.fill(white)

    # Draw lattice
    pygame.draw.line(screen, red, (0, 0), (0, screen_height), 2)
    pygame.draw.line(screen, red, (step_x_start, 0), (step_x_start, screen_height), 2)
    pygame.draw.line(
        screen,
        red,
        (step_x_end, 0),
        (step_x_end, screen_height),
        2,
    )

    ln, y = y_selection_map[scr_y][0], y_selection_map[scr_y][1]
    tot_ln = len(step_data)
    max_y = scr_y + screen_height
    block_idx, bpm, beat, split, delay, dy = -1, 0, 0, 0, 0, 0
    while ln < tot_ln and y < max_y:
        row = step_data[ln]
        bi, mi, bti, si = row[5], row[6], row[7], row[8]
        if block_idx != bi:
            info = block_info[bi]
            block_idx, bpm, beat, split, delay = bi, info[0], info[1], info[2], info[3]
            dy = max((cell_size * 2) // split, min_split_size)

        if mi == 0 and bti == 0 and si == 0:  # Start of Blcok
            pygame.draw.line(screen, red, (0, y - scr_y), (x_end, y - scr_y), 1)
            measure_text = font.render("{}:{}".format(bi + 1, mi + 1), True, black)
            measure_text_rect = measure_text.get_rect()
            measure_text_rect.topright = (step_x_start, y - scr_y)

            block_text = font.render("{:.4f}BPM, 1/{}".format(bpm, split), True, black)
            block_text_rect = block_text.get_rect()
            block_text_rect.topleft = (step_x_end, y - scr_y)

            screen.blit(measure_text, measure_text_rect)
            screen.blit(block_text, block_text_rect)

        elif bti == 0 and si == 0:  # Start of Measure
            pygame.draw.line(
                screen, royal_blue, (0, y - scr_y), (step_x_end, y - scr_y), 1
            )
            text = font.render("{}:{}".format(bi + 1, mi + 1), True, black)
            text_rect = text.get_rect()
            text_rect.topright = (step_x_start, y - scr_y)

            screen.blit(text, text_rect)

        elif si == 0:  # Start of Beat
            pygame.draw.line(
                screen,
                royal_blue,
                (step_x_start, y - scr_y),
                (step_x_end, y - scr_y),
                1,
            )

        elif (split == 6 and si % 2 == 0) or (split % 2 == 0 and si * 2 == split):
            # Split line
            pygame.draw.line(
                screen,
                light_green,
                (step_x_start, y - scr_y),
                (step_x_end, y - scr_y),
                1,
            )

        # Draw step if exists
        for i in range(cols):
            image = None
            if row[i] == 0:
                continue
            if row[i] == 1:
                image = short_images[i % 5]
            elif row[i] == 2:
                image = long_head_images[i % 5]
            elif row[i] == 3:
                image = long_middle_images[i % 5]
            elif row[i] == 4:
                image = long_tail_images[i % 5]

            screen.blit(image, (step_x_start + i * cell_size, y - scr_y))

        y += dy
        ln += 1

    # Draw hovered square
    pygame.draw.rect(
        screen, dark_gray, (hover_x, hover_y - scr_y, cell_size, cell_size)
    )

    # Draw selected square
    pygame.draw.rect(
        screen, black, (square_x, square_y - scr_y, cell_size, cell_size), 1
    )

    pygame.display.flip()

    pygame.time.Clock().tick(30)
