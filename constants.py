import pygame
from typing import List
from enum import Enum


class DelayUnit(Enum):
    beats = 1
    ms = 2


# Key Hold Delay
KEY_HOLD_DELAY_MS = 500
KEY_HOLD_INTERVAL_MS = 50

# HARD MAX Y
HARD_MAX_Y = 100_000  # maximum scrollable height
HARD_MAX_LINES = 2_000  # maximum number of lines

# Pygame.mixer sample_rate
PYGAME_SAMPLE_RATE = 44100

# Initial Screen Width, Height
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 700
MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT = 600, 600

# Step Chart Size
STEP_SIZE_MAP = [24, 36, 48]
MUSIC_SPEED_MAP = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
VERTICAL_MULTIPLIER_MAX = 50

# Step <-> Code Inverter
STEP_TO_CODE = {".": 0, "X": 1, "M": 2, "H": 3, "W": 4}
CODE_TO_STEP = [".", "X", "M", "H", "W"]

# Keybinding for Step
KEY_SINGLE = {
    pygame.K_z: 0,
    pygame.K_q: 1,
    pygame.K_s: 2,
    pygame.K_e: 3,
    pygame.K_c: 4,
}
KEY_DOUBLE = {
    pygame.K_z: 0,
    pygame.K_q: 1,
    pygame.K_s: 2,
    pygame.K_e: 3,
    pygame.K_c: 4,
    pygame.K_v: 5,
    pygame.K_r: 6,
    pygame.K_g: 7,
    pygame.K_y: 8,
    pygame.K_n: 9,
}

COL_TO_KEY = ["z", "q", "s", "e", "c", "v", "r", "g", "y", "n"]

# UI Element Index
FILE_BUTTON = 0
FILE_LOAD_BUTTON = 1
FILE_LOAD_MP3_BUTTON = 2
FILE_SAVE_BUTTON = 3
FILE_SAVE_AS_BUTTON = 4
FILE_PLAYSPEED_BUTTON = 5
FILE_PLAY_BUTTON = 6
FILE_PLAYTIME_TEXT = 7

BI_BPM_TEXTBOX = FILE_PLAYTIME_TEXT + 1
BI_BM_TEXTBOX = FILE_PLAYTIME_TEXT + 2
BI_BS_TEXTBOX = FILE_PLAYTIME_TEXT + 3
BI_DL_TEXBOX = FILE_PLAYTIME_TEXT + 4
BI_DL_UNIT_BUTTON = FILE_PLAYTIME_TEXT + 5
BI_MS_TEXTBOX = FILE_PLAYTIME_TEXT + 6
BI_BT_TEXTBOX = FILE_PLAYTIME_TEXT + 7
BI_SP_TEXTBOX = FILE_PLAYTIME_TEXT + 8
BI_APPLY_BUTTON = FILE_PLAYTIME_TEXT + 9

BO_BLOCK_ADD_A_BUTTON = BI_APPLY_BUTTON + 1
BO_BLOCK_ADD_B_BUTTON = BI_APPLY_BUTTON + 2
BO_BLOCK_SPLIT_BUTTON = BI_APPLY_BUTTON + 3
BO_BLOCK_DELETE_BUTTON = BI_APPLY_BUTTON + 4

AUTO_LINE_PASS_BUTTON = BO_BLOCK_DELETE_BUTTON + 1

LOG_TEXTBOX = AUTO_LINE_PASS_BUTTON + 1
LOG_CLEAR_BUTTON = AUTO_LINE_PASS_BUTTON + 2

SCROLLBAR_UP_BUTTON = LOG_CLEAR_BUTTON + 1
SCROLLBAR_DOWN_BUTTON = LOG_CLEAR_BUTTON + 2

TOTAL_UI_ELEMENTS = SCROLLBAR_DOWN_BUTTON + 1

PANEL_1 = SCROLLBAR_DOWN_BUTTON + 1
PANEL_2 = SCROLLBAR_DOWN_BUTTON + 2
PANEL_3 = SCROLLBAR_DOWN_BUTTON + 3
PANEL_4 = SCROLLBAR_DOWN_BUTTON + 4
PANEL_5 = SCROLLBAR_DOWN_BUTTON + 5


# INF
INFINITY = 1_000_000_000_000_000

# Used Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
MIDDLE_GRAY = (170, 170, 170)
DARK_GRAY = (169, 169, 169)
SEMI_BLACK = (32, 32, 32)
ROYAL_BLUE = (65, 105, 205)
LIGHT_GREEN = (144, 238, 144)
LIGHT_BLUE = (221, 254, 243)
LIGHT_YELLOW = (255, 255, 222)
LIGHT_RED = (255, 150, 150)
BUTTON_OFF_COLOR = (76, 80, 82)
BUTTON_HOVER_COLOR = (200, 238, 200)
BUTTON_ON_COLOR = LIGHT_GREEN
BPM_MIN_COLOR = (255, 255, 255)
BPM_MAX_COLOR = (255, 126, 126)

# Size config
CELL_SIZE = 48
MIN_SPLIT_SIZE = 10

# Scroll Speed Config
SCROLL_SPEED = 20

# Line Selection Speed
LINE_AUTO_MOVE_DELAY_MS = 500

# Measure Descriptor Width
MEASURE_DESCRIPTOR_WIDTH = 60

# Scroll Bar
MIN_SCROLL_BAR_HEIGHT = 100

# Option Width
OPTION_WIDTH = 300

# block information index in state.step_data  : block_idx, bpm, beat/measure, split/beat, delay
STEP_DATA_BI_IDX = 0  # index for block index
STEP_DATA_MS_IDX = 1  # index for measure index
STEP_DATA_BT_IDX = 2  # index for beat index
STEP_DATA_SP_IDX = 3  # index for split index
STEP_DATA_VD_IDX = 4  # index for validity index
STEP_DATA_OFFSET = 5  # length of total metadata index

# block information index in state.block_info
BLOCK_BPM_IDX = 0
BLOCK_BM_IDX = 1
BLOCK_SB_IDX = 2
BLOCK_DL_IDX = 3
BLOCK_MS_IDX = 4
BLOCK_BT_IDX = 5
BLOCK_SP_IDX = 6

SCROLLBAR_BUTTON_HEIGHT = 30
SCROLLBAR_BUTTON_WIDTH = 20
