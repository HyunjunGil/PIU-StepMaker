import pygame, pygame_gui, sys, time, numpy as np

from typing import List, Tuple
from constants import *
from file_manager import load_ucs_file, save_ucs_file
from pygame import Surface

pygame.init()

font = pygame.font.SysFont("Verdana", 18)
header_font = pygame.font.SysFont("Verdana", 24)

screen_width, screen_height = 800, 500
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

# scroll
scr_y = 0

# Mouse Position Variable

# Selected Line Locations Variable
line_selected = False
sline_y_init = -100
sline_y = -100

# Hover Rectangle Location Variable
hline_y = -100

# Total Grid Height
grid_height = 0
max_y = 0

# Scroll Bar Variable
scrollbar_height = 0
scrollbar_mouse_y = 0
scrollbar_y_init = 0
scrollbar_y = 0

# Mouse & Key Flag
is_scroll = False
lattice_clicked = False
scrollbar_clicked = False
block_info_idx = -1
line_selected = False
save_pressed = False
copy_pressed = False
paste_pressed = False
playing = False
typing = False

# Key Combination Status
key_combination_status = {
    (pygame.K_LCTRL, pygame.K_c): False,
    (pygame.K_LCTRL, pygame.K_v): False,
    (pygame.K_LCTRL, pygame.K_s): False,
    (pygame.K_LCTRL, pygame.K_z): False,
    (pygame.K_LCTRL, pygame.K_a): False,
}


# Key pressing time
square_keys = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0, pygame.K_UP: 0, pygame.K_DOWN: 0}

# Image Load
short_images = [
    pygame.image.load(f"./images/note{i % 5}_48.png").convert_alpha() for i in range(10)
]
long_head_images = [
    pygame.image.load(f"./images/start{i % 5}_48.png").convert_alpha()
    for i in range(10)
]
long_middle_images = [
    pygame.image.load(f"./images/hold{i % 5}_48.png").convert_alpha() for i in range(10)
]
long_tail_images = [
    pygame.image.load(f"./images/end{i % 5}_48.png").convert_alpha() for i in range(10)
]

total_images = [
    [None for _ in range(10)],
    short_images,
    long_head_images,
    long_middle_images,
    long_tail_images,
]


# lines = []
block_info: List[List[int | float]] = []
step_data: List[List[int]] = []
y_selection_map: List[List[int]] = [[0, 0] for i in range(100_000)]


format = -1
mode = ""

y_coors = []

block_idx, y_coor = 0, 0
initial_bpm, bpm, delay, beat, split, lcnt = 0, 0, 0, 0, 0, 0


def empty_if_none(a: any):
    if a is None:
        return ""
    else:
        return str(a)


def update_y_selection_map():
    global step_data, y_selection_map, max_y
    block_idx, measure, bpm, beat, split = -1, 0, 0, 0, 0
    y, ny = 0, 0
    tot_ln = len(step_data)
    for ln in range(tot_ln):
        row = step_data[ln]
        bi = row[STEP_DATA_BI_IDX]
        if bi != block_idx:
            block = block_info[bi]
            bpm, beat, split, delay = block[0], block[1], block[2], block[3]

        line_height = max((CELL_SIZE * 2) // split, MIN_SPLIT_SIZE)
        ny = y + line_height
        # print(ln, ny)
        for i in range(y, ny):
            y_selection_map[i][0] = ln
            y_selection_map[i][1] = y

        y = ny

    max_y = y
    # print(max_y)


def clear_step(ln: int, col: int):
    global step_data
    col += STEP_DATA_OFFSET
    if step_data[ln][col] == 0:
        pass
    elif step_data[ln][col] == 1:
        step_data[ln][col] = 0
    else:
        s = e = ln
        while step_data[s][col] != 2:
            s -= 1
        while step_data[e][col] != 4:
            e += 1
        for i in range(s, e + 1):
            step_data[i][col] = 0


def add_text(
    screen: Surface,
    text: str,
    x: int,
    y: int,
    font_size: int,
    loc: int = 0,
    color: Tuple[int, int] = BLACK,
    bg_color: Tuple[int, int] | None = None,
):
    # loc
    # 0 : topleft
    # 1 : topright
    # 2 : bottomright
    # 3 : bottomleft
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color, bg_color)
    rect = text_surface.get_rect()
    if loc == 0:
        rect.topleft = (x, y)
    elif loc == 1:
        rect.topright = (x, y)
    elif loc == 2:
        rect.bottomright = (x, y)
    elif loc == 3:
        rect.bottomleft = (x, y)

    screen.blit(text_surface, rect)


def add_rectangle_with_text(
    text: str,
    font_size: int,
    rect_info: Tuple[int, int, int, int],
    rect_color: Tuple[int, int, int] = WHITE,
    text_color: Tuple[int, int, int] = BLACK,
):
    global screen
    rect = pygame.Rect(rect_info)
    text_surface = pygame.font.SysFont("Verdana", font_size).render(
        text, True, text_color
    )
    text_rect = text_surface.get_rect(center=rect.center)
    pygame.draw.rect(screen, rect_color, rect)
    screen.blit(text_surface, text_rect)
    pass


def draw_block_info_area():
    global screen
    offset = BLOCK_INFO_GAP
    x0 = option_x_start + BLOCK_INFO_GAP
    x1 = x0 + 120
    y0 = BLOCK_INFO_AREA_Y
    st, sw, sh = 12, 60, 20
    add_text(
        screen,
        "Block Information",
        option_x_start + BLOCK_INFO_GAP,
        BLOCK_INFO_AREA_Y + BLOCK_INFO_GAP,
        30,
        0,
        BLACK,
    )
    offset += 30
    add_rectangle_with_text(
        "BPM",
        st,
        (option_x_start + Bx0, BLOCK_INFO_AREA_Y + By0, sw, sh),
        LIGHT_GRAY,
    )
    add_rectangle_with_text(
        "Measures",
        st,
        (option_x_start + Bx2, BLOCK_INFO_AREA_Y + By0, sw, sh),
        LIGHT_GRAY,
    )
    offset += sh + BLOCK_INFO_GAP
    add_rectangle_with_text(
        "B/M",
        st,
        (option_x_start + Bx0, BLOCK_INFO_AREA_Y + By1, sw, sh),
        LIGHT_GRAY,
    )
    add_rectangle_with_text(
        "Beats",
        st,
        (option_x_start + Bx2, BLOCK_INFO_AREA_Y + By1, sw, sh),
        LIGHT_GRAY,
    )
    offset += sh + BLOCK_INFO_GAP
    add_rectangle_with_text(
        "S/B",
        st,
        (option_x_start + Bx0, BLOCK_INFO_AREA_Y + By2, sw, sh),
        LIGHT_GRAY,
    )
    add_rectangle_with_text(
        "Splits",
        st,
        (option_x_start + Bx2, BLOCK_INFO_AREA_Y + By2, sw, sh),
        LIGHT_GRAY,
    )
    offset += sh + BLOCK_INFO_GAP
    add_rectangle_with_text(
        "Delay",
        st,
        (option_x_start + Bx0, BLOCK_INFO_AREA_Y + By3, sw, sh),
        LIGHT_GRAY,
    )
    add_rectangle_with_text(
        "m/s",
        st,
        (option_x_start + Bx2, BLOCK_INFO_AREA_Y + By3, sw, sh),
        WHITE,
    )
    # pass


# pygame Manager
manager = pygame_gui.UIManager((screen_width, screen_height))


format, mode, block_info, step_data = load_ucs_file("sample.ucs")

rows, cols = len(step_data), len(step_data[0]) - STEP_DATA_OFFSET
SELECTION_WIDTH = CELL_SIZE * cols
step_x_start = MEASURE_DESCRIPTOR_WIDTH
step_x_end = MEASURE_DESCRIPTOR_WIDTH + CELL_SIZE * cols
scrollbar_x = step_x_end
option_x_start = scrollbar_x + SCROLL_BAR_WIDTH
option_x_end = option_x_start + OPTION_WIDTH

running = True

update_y_selection_map()

### File Buttons
# Play/Stop Button
play_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(
        (option_x_start + FILE_BUTTON_GAP, FILE_BUTTON_GAP), FILE_BUTTON_SIZE
    ),
    text="Play",
    manager=manager,
)
save_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(
        (option_x_start + FILE_BUTTON_GAP * 2 + FILE_BUTTON_WIDTH, FILE_BUTTON_GAP),
        FILE_BUTTON_SIZE,
    ),
    text="Save",
    manager=manager,
)
load_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(
        (
            option_x_start + FILE_BUTTON_GAP * 3 + FILE_BUTTON_WIDTH * 2,
            FILE_BUTTON_GAP,
        ),
        FILE_BUTTON_SIZE,
    ),
    text="Load",
    manager=manager,
)

### Block Info Buttons
# Adjust Block Size
block_apply_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(
        (
            option_x_end - BLOCK_BUTTON_SIZE[0] - BLOCK_INFO_GAP,
            BLOCK_INFO_AREA_Y
            + BLOCK_INFO_AREA_HEIGHT
            - BLOCK_BUTTON_SIZE[1]
            - BLOCK_INFO_GAP,
        ),
        BLOCK_BUTTON_SIZE,
    ),
    text="Apply",
    manager=manager,
)

bpm_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(option_x_start + Bx1, BLOCK_INFO_AREA_Y + By0, Bw1, Bh),
    manager=manager,
    object_id="BI_bpm",
)
bm_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(option_x_start + Bx1, BLOCK_INFO_AREA_Y + By1, Bw1, Bh),
    manager=manager,
    object_id="BI_bm",
)
sb_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(option_x_start + Bx1, BLOCK_INFO_AREA_Y + By2, Bw1, Bh),
    manager=manager,
    object_id="BI_sb",
)
delay_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(option_x_start + Bx1, BLOCK_INFO_AREA_Y + By3, Bw1, Bh),
    manager=manager,
    object_id="BI_delay",
)
measures_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(option_x_start + Bx3, BLOCK_INFO_AREA_Y + By0, Bw3, Bh),
    manager=manager,
    object_id="BI_measures",
)
beats_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(option_x_start + Bx3, BLOCK_INFO_AREA_Y + By1, Bw3, Bh),
    manager=manager,
    object_id="BI_beats",
)
splits_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(option_x_start + Bx3, BLOCK_INFO_AREA_Y + By2, Bw3, Bh),
    manager=manager,
    object_id="BI_splits",
)


bpm_textbox.set_allowed_characters([f"{i}" for i in range(10)] + ["."])
bm_textbox.set_allowed_characters("numbers")
sb_textbox.set_allowed_characters("numbers")
delay_textbox.set_allowed_characters("numbers")
measures_textbox.set_allowed_characters("numbers")
beats_textbox.set_allowed_characters("numbers")
splits_textbox.set_allowed_characters("numbers")

block_information_text_boxes = [
    bpm_textbox,
    bm_textbox,
    sb_textbox,
    delay_textbox,
    measures_textbox,
    beats_textbox,
    splits_textbox,
]


clock = pygame.time.Clock()

while running:

    time_delta = clock.tick(60) / 1000.0
    current_time = pygame.time.get_ticks()

    pressed_keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.VIDEORESIZE:
            screen_width, screen_height = event.size
            screen = pygame.display.set_mode(
                (screen_width, screen_height), pygame.RESIZABLE
            )

        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            print(event.ui_object_id, " unfocused")
            block_info_idx = -1

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 4:  # Mouse Wheel Up
                is_scroll = True
                scr_y = max(scr_y - SCROLL_SPEED, 0)
            elif event.button == 5:  # Mouse Wheel Down
                is_scroll = True
                scr_y = min(scr_y + SCROLL_SPEED, max_y)
            elif event.button == 1:  # Left Mouse Click

                lattice_clicked = scrollbar_clicked = False
                block_info_idx = -1

                mouse_x, mouse_y = event.pos

                # Select Line
                if step_x_start <= mouse_x < step_x_end:
                    lattice_clicked = True
                    line_selected = True
                    # sline_y_init = sline_y = y_selection_map[mouse_y + scr_y][1]
                    sline_y = y_selection_map[mouse_y + scr_y][1]
                    if not pressed_keys[pygame.K_LSHIFT]:
                        sline_y_init = sline_y

                # Select Scrollbar
                elif (
                    scrollbar_x <= mouse_x < option_x_start
                    and scrollbar_y <= mouse_y < scrollbar_y + scrollbar_height
                    and not scrollbar_clicked
                ):
                    scrollbar_clicked = True
                    scrollbar_mouse_y = mouse_y
                    scrollbar_y_init = scrollbar_y
                    print("scrollbar", scrollbar_y_init, scrollbar_mouse_y)
                else:

                    # Select Block Information Text Box
                    for i, textbox in enumerate(block_information_text_boxes):
                        if textbox.get_abs_rect().collidepoint(event.pos):
                            block_info_idx = i
                            break

            print(scr_y)

        elif event.type == pygame.MOUSEBUTTONUP:
            lattice_clicked = False
            scrollbar_clicked = False

        elif event.type == pygame.KEYDOWN:
            is_scroll = False
            if event.key in square_keys and line_selected:
                if event.key == pygame.K_LEFT:
                    square_x = max(square_x - CELL_SIZE, step_x_start)
                elif event.key == pygame.K_RIGHT:
                    square_x = min(
                        square_x + CELL_SIZE, step_x_start + (cols - 1) * CELL_SIZE
                    )
                elif event.key == pygame.K_UP:
                    ln = y_selection_map[sline_y][0]
                    if ln != 0:
                        sb = block_info[step_data[ln - 1][STEP_DATA_BI_IDX]][2]
                        dy = max((CELL_SIZE * 2) // sb, MIN_SPLIT_SIZE)
                        sline_y -= dy
                        if not pressed_keys[pygame.K_LSHIFT]:
                            sline_y_init = sline_y

                elif event.key == pygame.K_DOWN:
                    ln = y_selection_map[sline_y][0]
                    if ln != len(step_data) - 1:
                        sb = block_info[step_data[ln][STEP_DATA_BI_IDX]][2]
                        dy = max((CELL_SIZE * 2) // sb, MIN_SPLIT_SIZE)
                        sline_y += dy
                        if not pressed_keys[pygame.K_LSHIFT]:
                            sline_y_init = sline_y

            elif (
                pygame.key.name(event.key) in KEY_TO_COL
                and line_selected
                and not pressed_keys[pygame.K_LCTRL]
            ):
                col = STEP_DATA_OFFSET + KEY_TO_COL[pygame.key.name(event.key)]
                ln_start = y_selection_map[min(sline_y_init, sline_y)][0]
                ln_end = y_selection_map[max(sline_y_init, sline_y)][0]

                if ln_start == ln_end:  # Only one line is selected
                    step = step_data[ln_start][col]
                    if step == 1:
                        step_data[ln_start][col] = 0
                    else:
                        if step != 0:
                            clear_step(ln_start, col)
                        step_data[ln_start][col] = 1
                else:  # Many lines are selected
                    flag = (step_data[ln_start][col] == 2) and (
                        step_data[ln_end][col] == 4
                    )
                    for ln in range(ln_start + 1, ln_end):
                        if not flag:
                            break
                        flag = flag and (step_data[ln][col] == 3)

                    if flag:
                        for i in range(ln_start, ln_end + 1):
                            step_data[i][col] = 0
                    else:
                        clear_step(ln_start, col)
                        clear_step(ln_end, col)
                        step_data[ln_start][col] = 2
                        step_data[ln_end][col] = 4
                        for i in range(ln_start + 1, ln_end):
                            step_data[i][col] = 3

            elif event.key == pygame.K_BACKSPACE:  # Clear selected lines
                ln_start = y_selection_map[min(sline_y_init, sline_y)][0]
                ln_end = y_selection_map[max(sline_y_init, sline_y)][0]
                for i in range(cols):
                    clear_step(ln_start, i)
                    clear_step(ln_end, i)
                for i in range(ln_start, ln_end + 1):
                    for j in range(STEP_DATA_OFFSET, STEP_DATA_OFFSET + cols):
                        step_data[i][j] = 0

            elif event.key == pygame.K_ESCAPE and line_selected:
                line_selected = False
                # Vanish selection square by moving it to out of the screen
                sline_y_init = sline_y = -100

        manager.process_events(event)

    manager.update(time_delta)

    if lattice_clicked:
        _, mouse_y = pygame.mouse.get_pos()
        sline_y = y_selection_map[mouse_y + scr_y][1]

    # Move Scrollbar
    scrollbar_height = max(
        MIN_SCROLL_BAR_HEIGHT,
        min(screen_height, (screen_height * screen_height) // max_y),
    )
    if scrollbar_clicked:
        _, mouse_y = pygame.mouse.get_pos()
        scrollbar_y = min(
            max(scrollbar_y_init + (mouse_y - scrollbar_mouse_y), 0),
            screen_height - scrollbar_height,
        )
        scr_y = (scrollbar_y * max_y) // (screen_height - scrollbar_height)
        print("adjusted :", mouse_y, scrollbar_y, scr_y)
    else:
        scrollbar_y = ((screen_height - scrollbar_height) * scr_y) // max_y

    ### Save step_data.
    if pressed_keys[pygame.K_LCTRL] and pressed_keys[pygame.K_s]:
        if not key_combination_status[(pygame.K_LCTRL, pygame.K_s)]:
            save_ucs_file("result.ucs", format, mode, step_data, block_info)
            key_combination_status[(pygame.K_LCTRL, pygame.K_s)] = True
    else:
        key_combination_status[(pygame.K_LCTRL, pygame.K_s)] = False

    ### Keep curent selected line on screen while not scrolling
    if line_selected and not is_scroll:
        scr_y = min(max(scr_y, sline_y + CELL_SIZE - screen_height), sline_y)

    ### Hover Sqaure
    mouse_x, mouse_y = pygame.mouse.get_pos()
    grid_x = (mouse_x - step_x_start) // CELL_SIZE

    if step_x_start <= mouse_x < step_x_end:
        hline_y = y_selection_map[mouse_y + scr_y][1]
    else:
        hline_y = -100

    screen.fill(WHITE)

    # Draw hovered square
    pygame.draw.rect(
        screen, LIGHT_GRAY, (step_x_start, hline_y - scr_y, SELECTION_WIDTH, CELL_SIZE)
    )

    # Draw lattice
    pygame.draw.line(screen, LIGHT_GRAY, (0, 0), (0, screen_height), 2)
    pygame.draw.line(
        screen, LIGHT_GRAY, (step_x_start, 0), (step_x_start, screen_height), 2
    )
    pygame.draw.line(
        screen,
        LIGHT_GRAY,
        (step_x_end, 0),
        (step_x_end, screen_height),
        2,
    )

    ln, y = y_selection_map[scr_y][0], y_selection_map[scr_y][1]
    tot_ln = len(step_data)
    screen_bottom = scr_y + screen_height
    block_idx, bpm, beat, split, delay, dy = -1, 0, 0, 0, 0, 0
    image_rects: List[Tuple[int, int, int, int]] = []  # List of (z, y, col, code)
    while ln < tot_ln and y < screen_bottom:
        row = step_data[ln]
        bi, mi, bti, si = (
            row[STEP_DATA_BI_IDX],
            row[STEP_DATA_MS_IDX],
            row[STEP_DATA_BT_IDX],
            row[STEP_DATA_SP_IDX],
        )

        if block_idx != bi:
            info = block_info[bi]
            block_idx, bpm, beat, split, delay = bi, info[0], info[1], info[2], info[3]
            dy = max((CELL_SIZE * 2) // split, MIN_SPLIT_SIZE)
        # print(mi, bti, si)
        if mi == 0 and bti == 0 and si == 0:  # Start of Blcok
            # print("block start")
            pygame.draw.line(
                screen, RED, (0, y - scr_y), (option_x_start, y - scr_y), 3
            )
            text = font.render("{}:{}".format(bi + 1, mi + 1), True, BLACK)
            text_rect = text.get_rect()
            text_rect.topright = (step_x_start, y - scr_y)

            # block_text = font.render("{:.4f}BPM\n1/{}".format(bpm, split), True, BLACK)
            # block_text_rect = block_text.get_rect()
            # block_text_rect.topleft = (step_x_end, y - scr_y)

            screen.blit(text, text_rect)
            # screen.blit(block_text, block_text_rect)

        elif bti == 0 and si == 0:  # Start of Measure
            # print("adf")
            pygame.draw.line(
                screen, ROYAL_BLUE, (0, y - scr_y), (step_x_end, y - scr_y), 2
            )
            text = font.render("{}:{}".format(bi + 1, mi + 1), True, BLACK)
            text_rect = text.get_rect()
            text_rect.topright = (step_x_start, y - scr_y)

            screen.blit(text, text_rect)

        elif si == 0:  # Start of Beat
            pygame.draw.line(
                screen,
                ROYAL_BLUE,
                (step_x_start, y - scr_y),
                (step_x_end, y - scr_y),
                1,
            )

        elif (split == 6 and si % 2 == 0) or (split % 2 == 0 and si * 2 == split):
            # Split line
            pygame.draw.line(
                screen,
                LIGHT_GREEN,
                (step_x_start, y - scr_y),
                (step_x_end, y - scr_y),
                1,
            )

        # Draw step if exists
        for col in range(cols):
            idx = col + STEP_DATA_OFFSET
            image = None
            if row[idx] == 0:
                continue
            elif row[idx] == 2:
                image = short_images[col % 5]
                image_rects.append((ln + INF, y, col, 2))
            else:
                image_rects.append((ln, y, col, row[idx]))

        y += dy
        ln += 1

    # Draw Images
    image_rects = sorted(image_rects, key=lambda x: x[0])
    for rect in image_rects:
        z, y, col, code = rect
        screen.blit(
            total_images[code][col], (step_x_start + col * CELL_SIZE, y - scr_y)
        )

    # Draw selected square
    pygame.draw.rect(
        screen,
        BLACK,
        (
            step_x_start,
            min(sline_y_init, sline_y) - scr_y,
            SELECTION_WIDTH,
            abs(sline_y_init - sline_y) + CELL_SIZE,
        ),
        3,
    )

    # Draw Scroll Bar
    pygame.draw.rect(
        screen,
        DARK_GRAY,
        (
            scrollbar_x,
            scrollbar_y,
            SCROLL_BAR_WIDTH,
            scrollbar_height,
        ),
    )

    # Draw Line Descriptor
    if line_selected:
        ln = y_selection_map[sline_y][0]
        ln_init = y_selection_map[sline_y_init][0]
        if ln == ln_init:
            txt = "Ln{}".format(ln + 1)
        else:
            ln_max, ln_min = max(ln, ln_init), min(ln, ln_init)
            txt = "Ln{}~{} ({} selected)".format(
                ln_min + 1, ln_max + 1, ln_max - ln_min + 1
            )
        line_text = pygame.font.SysFont("Verdana", 12).render(
            txt, True, BLACK, LIGHT_GRAY
        )
        line_text_rect = line_text.get_rect()
        line_text_rect.bottomright = (scrollbar_x, screen_height)
        screen.blit(line_text, line_text_rect)

    # Draw Option Area
    pygame.draw.rect(screen, BLACK, (option_x_start, 0, OPTION_WIDTH, screen_height), 3)
    pygame.draw.line(
        screen,
        BLACK,
        (option_x_start, FILE_BUTTON_AREA_HEIGHT),
        (option_x_end, FILE_BUTTON_AREA_HEIGHT),
        2,
    )

    pygame.draw.line(
        screen,
        BLACK,
        (option_x_start, BLOCK_INFO_AREA_Y + BLOCK_INFO_AREA_HEIGHT),
        (option_x_end, BLOCK_INFO_AREA_Y + BLOCK_INFO_AREA_HEIGHT),
    )

    draw_block_info_area()

    # line_text = font.render(txt, True, BLACK, LIGHT_GRAY)
    # line_text_rect = line_text.get_rect()
    # line_text_rect.bottomright = (scrollbar_x, screen_height)

    # block_info_header

    # Fill Block Information
    if line_selected and block_info_idx == -1:
        print("Update Block Info")

        mouse_x, mouse_y = pygame.mouse.get_pos()

        if line_selected:
            ln = y_selection_map[sline_y][0]
            info = block_info[step_data[ln][STEP_DATA_BI_IDX]]

        elif step_x_start <= mouse_x < step_x_end:
            ln = y_selection_map[mouse_y + scr_y][0]
            info = block_info[step_data[ln][STEP_DATA_BI_IDX]]

        for textbox, value in zip(block_information_text_boxes, info):
            textbox.set_text(empty_if_none(value))

    if line_selected:
        for textbox in block_information_text_boxes:
            textbox.enable()
    else:
        for textbox in block_information_text_boxes:
            textbox.set_text("")
            textbox.disable()

    manager.draw_ui(screen)

    pygame.display.flip()
