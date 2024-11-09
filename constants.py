from typing import List


# Step <-> Code Inverter
STEP_TO_CODE = {".": 0, "X": 1, "M": 2, "H": 3, "W": 4}
CODE_TO_STEP = [".", "X", "M", "H", "W"]

# Keybinding for Step
KEY_TO_COL = {
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

# Size config
CELL_SIZE = 48
MIN_SPLIT_SIZE = 10

# Scroll Speed Config
SCROLL_SPEED = 20

# Line Selection Speed
LINE_AUTO_MOVE_DELAY_MS = 500

# Measure Descriptor Width
MEASURE_DESCRIPTOR_WIDTH = 50

# Scroll Bar
SCROLL_BAR_WIDTH = 20
MIN_SCROLL_BAR_HEIGHT = 200

# Option Width
OPTION_WIDTH = 300

# Step Data Index for block information : block_idx, bpm, beat/measure, split/beat, delay
STEP_DATA_BI_IDX = 0  # index for block index
STEP_DATA_MS_IDX = 1  # index for measure index
STEP_DATA_BT_IDX = 2  # index for beat index
STEP_DATA_SP_IDX = 3  # index for split index
STEP_DATA_OFFSET = 4  # length of total metadata index


# File Buttons Options
FILE_BUTTON_WIDTH = 50
FILE_BUTTON_HEIGHT = 25
FILE_BUTTON_SIZE = (FILE_BUTTON_WIDTH, FILE_BUTTON_HEIGHT)
FILE_BUTTON_GAP = 10
FILE_BUTTON_AREA_Y = 0
FILE_BUTTON_AREA_HEIGHT = FILE_BUTTON_HEIGHT + 2 * FILE_BUTTON_GAP

# Block Info
BLOCK_INFO_AREA_Y = FILE_BUTTON_AREA_Y + FILE_BUTTON_AREA_HEIGHT
BLOCK_INFO_TEXT_WIDTH = 50
BLOCK_INFO_TEXT_HEIGHT = 25
BLOCK_BUTTON_SIZE = (60, 25)

BLOCK_INFO_AREA_HEIGHT = 200
BLOCK_INFO_GAP = 10

Bx0 = BLOCK_INFO_GAP
Bw0 = 60
Bx1 = Bx0 + Bw0 + BLOCK_INFO_GAP // 2
Bw1 = 80
Bx2 = Bx1 + Bw1 + BLOCK_INFO_GAP // 2
Bw2 = 60
Bx3 = Bx2 + Bw2 + BLOCK_INFO_GAP // 2
Bw3 = 40 + BLOCK_INFO_GAP

Bh = 25
By0 = BLOCK_INFO_GAP + 30
By1 = By0 + Bh + BLOCK_INFO_GAP
By2 = By1 + Bh + BLOCK_INFO_GAP
By3 = By2 + Bh + BLOCK_INFO_GAP


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
