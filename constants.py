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
CELL_SIZE = 76
MIN_SPLIT_SIZE = 10

# Scroll Speed Config
SCROLL_SPEED = 20

# Line Selection Speed
LINE_AUTO_MOVE_DELAY_MS = 500
