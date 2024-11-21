import pygame
from typing import List

# Initial Screen Width, Height
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 500

# Step <-> Code Inverter
STEP_TO_CODE = {".": 0, "X": 1, "M": 2, "H": 3, "W": 4}
CODE_TO_STEP = [".", "X", "M", "H", "W"]

# Keybinding for Step
KEY_SINGLE = {
    "z": 0,
    "q": 1,
    "s": 2,
    "e": 3,
    "c": 4,
}
KEY_DOUBLE = {
    "z": 0,
    "q": 1,
    "s": 2,
    "e": 3,
    "c": 4,
    "v": 5,
    "r": 6,
    "g": 7,
    "y": 8,
    "n": 9,
}

COL_TO_KEY = ["z", "q", "s", "e", "c", "v", "r", "g", "y", "n"]


# INF
INF = 1_000_000

# Used Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (169, 169, 169)
ROYAL_BLUE = (65, 105, 205)
LIGHT_GREEN = (144, 238, 144)
LIGHT_BLUE = (221, 254, 243)
LIGHT_YELLOW = (255, 255, 222)
LIGHT_RED = (255, 99, 103)

# Size config
CELL_SIZE = 48
MIN_SPLIT_SIZE = 10

# Scroll Speed Config
SCROLL_SPEED = 20

# Line Selection Speed
LINE_AUTO_MOVE_DELAY_MS = 500

# Measure Descriptor Width
MEASURE_DESCRIPTOR_WIDTH = 150

# Scroll Bar
SCROLL_BAR_WIDTH = 20
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


# File Buttons Options
BASIC_ACTION_WIDTH = 60
BASIC_ACTION_HEIGHT = 30
BASIC_ACTION_SIZE = (BASIC_ACTION_WIDTH, BASIC_ACTION_HEIGHT)
BASIC_ACTION_AREA_Y = 0
BASIC_ACTION_AREA_HEIGHT = BASIC_ACTION_HEIGHT


# Block Info
BLOCK_INFO_AREA_Y = BASIC_ACTION_AREA_Y + BASIC_ACTION_AREA_HEIGHT
BLOCK_INFO_TEXT_WIDTH = 50
BLOCK_INFO_TEXT_HEIGHT = 25
BLOCK_BUTTON_SIZE = (60, 25)

BLOCK_INFO_AREA_HEIGHT = 200
BLOCK_INFO_GAP = 10

BI_x0 = BLOCK_INFO_GAP
BI_w0 = 60
BI_x1 = BI_x0 + BI_w0 + BLOCK_INFO_GAP // 2
BI_w1 = 80
BI_x2 = BI_x1 + BI_w1 + BLOCK_INFO_GAP // 2
BI_w2 = 60
BI_x3 = BI_x2 + BI_w2 + BLOCK_INFO_GAP // 2
BI_w3 = 40 + BLOCK_INFO_GAP

BI_h = 25
BI_y0 = BLOCK_INFO_GAP + 30
BI_y1 = BI_y0 + BI_h + BLOCK_INFO_GAP
BI_y2 = BI_y1 + BI_h + BLOCK_INFO_GAP
BI_y3 = BI_y2 + BI_h + BLOCK_INFO_GAP


# Constant for TAB operation
BLOCK_INFO_OBJECT_ID_IDX_MAP = {
    "BI_measures": 0,
    "BI_beats": 1,
    "BI_splits": 2,
    "BI_delay": 3,
    "BI_bpm": 4,
    "BI_bm": 5,
    "BI_sb": 6,
}


# Block Operation
BLOCK_OPER_AREA_Y = BLOCK_INFO_AREA_Y + BLOCK_INFO_AREA_HEIGHT
BLOCK_OPER_AREA_HEIGHT = 75
BLOCK_OPER_GAP = 10
BLOCK_OPER_BUTTON_WIDTH = 60
BLOCK_OPER_BUTTON_HEIGHT = 30
BLOCK_OPER_BUTTON_SIZE = (BLOCK_OPER_BUTTON_WIDTH, BLOCK_OPER_BUTTON_HEIGHT)

BO_x0 = 12
BO_x1 = BO_x0 + BLOCK_OPER_BUTTON_WIDTH + 12
BO_x2 = BO_x1 + BLOCK_OPER_BUTTON_WIDTH + 12
BO_x3 = BO_x2 + BLOCK_OPER_BUTTON_WIDTH + 12
BO_y0 = BLOCK_OPER_AREA_Y + 35

SCROLLBAR_BUTTON_WIDTH = SCROLL_BAR_WIDTH
SCROLLBAR_BUTTON_HEIGHT = 30
