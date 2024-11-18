from typing import List, Tuple, Dict
from constants import *


class State:
    def __init__(self):
        # Flag
        self.IS_SCROLL = False
        self.LATTICE_CLICKED = False
        self.SCROLLBAR_CLICKED = False
        self.LINE_SELECTED = False
        self.UPDATE_BLOCK_INFORMATION_TEXTBOX = False
        self.EMIT_BUTTON_PRESS = False
        self.APPLY_ENABLED = False
        self.SCREEN_SIZE_CHANGED = False
        self.MUSIC_PLAYING = False
        self.TYPING = False

        # Save Information
        self.ucs_file_path: str = "sample.ucs"
        self.ucs_save_path: str = "result.ucs"
        self.ucs_cache_path: str = "temp.ucs"

        # 0 : small, 24px
        # 1 : medium, 36px
        # 2 : large, 48px
        self.step_size: int = 48

        # Initial Chart Information
        self.format: int = -1
        self.mode: str = ""
        self.keymap: Dict[str, int] = dict()

        # Offset for Step Area and Scrollbar Area
        self.step_x_start = OPTION_WIDTH
        self.measure_x_start = 0
        self.scrollbar_x_start = 0

        # Step data
        self.step_data: List[List[int]] = []

        # Block information
        self.block_info: List[List[int | float]] = []

        # Screen size
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

        # Information for each y
        self.max_y = -1
        # self.y_info: List[List[int]] = [[0, 0] for _ in range(100000)]
        self.y_to_ln: List[int] = [0 for _ in range(100000)]
        self.ln_to_y: List[int] = [0 for _ in range(100000)]

        # selected line info
        self.y_cur = 0
        self.y_base = 0

        # scroll location info
        self.scr_y = 0

        # scroll bar info
        self.scrollbar_h = 0
        self.scrollbar_y = 0
        self.scrollbar_y_init = 0
        self.scr_mouse_init = -1

        # Element Focus Rectangle
        self.focus_idx_prev = -1
        self.focus_idx = -1

        # Clipboard
        self.clipboard: List[List[int]] | None = None

    def get_screen_size(self):
        return self.screen_width, self.screen_height

    def get_element_focus_info(self):
        return self.focus_x, self.focus_y, self.focus_w, self.focus_h

    def get_step_info(self):
        return self.step_data, self.block_info

    def get_y_info(self):
        return self.y_to_ln, self.ln_to_y

    def update_y_info(self):
        block_idx, measure, bpm, beat, split = -1, 0, 0, 0, 0
        y, ny = 0, 0
        tot_ln = len(self.step_data)
        for ln in range(tot_ln):
            row = self.step_data[ln]
            bi = row[STEP_DATA_BI_IDX]
            if bi != block_idx:
                block_idx = bi
                block = self.block_info[bi]
                bpm, beat, split, delay = block[0], block[1], block[2], block[3]

            line_height = min(max((CELL_SIZE * 2) // split, MIN_SPLIT_SIZE), CELL_SIZE)
            ny = y + line_height
            self.ln_to_y[ln] = y
            for i in range(y, ny):
                self.y_to_ln[i] = ln

            y = ny

        self.max_y = y

    def clear_step(self, ln: int, col: int):
        if self.step_data[ln][col] == 0:
            pass
        elif self.step_data[ln][col] == 1:
            self.step_data[ln][col] = 0
        else:
            s = e = ln
            while self.step_data[s][col] != 2:
                s -= 1
            while self.step_data[e][col] != 4:
                e += 1
            for i in range(s, e + 1):
                self.step_data[i][col] = 0
