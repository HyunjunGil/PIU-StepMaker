from pydub import AudioSegment
from typing import List, Tuple, Dict
from utils import get_block_size
from constants import *
from enum import Enum


class State:
    def __init__(self):
        self.initialize()

    def get_step_size(self):
        return STEP_SIZE_MAP[self.step_size_idx]

    def get_cols(self) -> int:
        if self.mode == "Single":
            return 5
        elif self.mode == "Double":
            return 10
        else:
            raise Exception("Invalid mode : {}".format(self.mode))

    def get_measure_range_by_y(self, y: int) -> Tuple[int, int]:
        step_data, block_info = self.get_step_info()
        y_to_ln = self.y_to_ln
        ln = y_to_ln[y]
        block = block_info[step_data[ln][STEP_DATA_BI_IDX]]
        line = step_data[ln]
        ln_from = ln - (line[STEP_DATA_BT_IDX] * block[2] + line[STEP_DATA_SP_IDX])
        ln_to = ln_from + (
            block[BLOCK_BT_IDX] * block[BLOCK_SP_IDX]
            if block[BLOCK_MS_IDX] == line[STEP_DATA_MS_IDX]
            else block[BLOCK_BM_IDX] * block[BLOCK_SB_IDX]
        )
        return ln_from, ln_to

    def get_block_range_by_y(self, y: int):
        step_data, block_info = self.get_step_info()
        y_to_ln = self.y_to_ln
        ln = y_to_ln[y]
        block = block_info[step_data[ln][STEP_DATA_BI_IDX]]
        line = step_data[ln]
        ln_from = ln - (
            (line[STEP_DATA_MS_IDX] * block[1] + line[STEP_DATA_BT_IDX]) * block[2]
            + line[STEP_DATA_SP_IDX]
        )
        ln_to = ln_from + ((block[4] * block[1] + block[5]) * block[2] + block[6])
        return ln_from, ln_to

    def get_block_range_by_block_idx(self, block_idx: int):
        ln_from, idx = 0, 0
        while idx < block_idx:
            block = self.block_info[idx]
            ln_from += get_block_size(block)  # number of lines in the block
            idx += 1
        block = self.block_info[block_idx]
        ln_to = ln_from + get_block_size(block)
        return ln_from, ln_to

    def sync_scr_y(self):

        if self.FIX_LINE:
            self.scr_y = self.ln_to_y[self.coor_cur[1]] - self.receptor_y
        else:
            y_cur = self.ln_to_y[self.coor_cur[1]]
            self.scr_y = max(
                min(self.scr_y, y_cur),
                y_cur + self.get_step_size() - self.screen_height,
            )

    def get_screen_size(self):
        return self.screen_width, self.screen_height

    def get_element_focus_info(self):
        return self.focus_x, self.focus_y, self.focus_w, self.focus_h

    def get_step_info(self):
        return self.step_data, self.block_info

    def get_y_info(self):
        return self.y_to_ln, self.ln_to_y

    def log(self, s: str, quite=True):
        if not quite:
            print(s)
        self.logs.append(s)

    def update_x_info(self):
        step_size, cols = self.get_step_size(), self.get_cols()
        self.measure_x_start = self.step_x_start + step_size * cols
        self.scrollbar_x_start = self.measure_x_start + MEASURE_DESCRIPTOR_WIDTH

    def update_y_info(self):

        step_data, block_info = self.get_step_info()
        block_idx, measure, bpm, beat, split = -1, 0, 0, 0, 0
        y, ny = 0, 0
        step_size = self.get_step_size()
        tot_ln = len(step_data)
        line_height = 0
        for ln in range(tot_ln):
            row = step_data[ln]
            bi = row[STEP_DATA_BI_IDX]
            if bi != block_idx:
                block_idx = bi
                block = block_info[bi]
                bpm, beat, split, delay = block[0], block[1], block[2], block[3]

                line_height = min(
                    max((step_size * 2) // split, MIN_SPLIT_SIZE), step_size
                )
            ny = y + line_height
            self.ln_to_y[ln] = y
            for i in range(y, ny):
                self.y_to_ln[i] = ln

            y = ny
        self.ln_to_y[tot_ln] = self.ln_to_y[tot_ln - 1] + step_size

        self.max_y = y

        screen_height, max_y = (
            self.screen_height - 2 * SCROLLBAR_BUTTON_HEIGHT,
            self.max_y,
        )
        self.scrollbar_h = max(
            MIN_SCROLL_BAR_HEIGHT,
            min(screen_height, (screen_height * screen_height) // max_y),
        )

    def update_scr_to_time(self):
        step_data, block_info = self.get_step_info()
        step_size = self.get_step_size()
        t, ms_per_pixel = 0.0, 0.0
        block_idx, measure, bpm, beat, split = -1, 0, 0, 0, 0

        scr_to_time = self.scr_to_time
        for y in range(0, self.max_y):
            scr_to_time[y] = int(t)
            ln = self.y_to_ln[y]
            row = step_data[ln]
            bi = row[STEP_DATA_BI_IDX]
            if bi != block_idx:
                block_idx = bi
                block = block_info[bi]
                bpm, beat, split, delay = block[0], block[1], block[2], block[3]
                t += delay

                line_height = min(
                    max((step_size * 2) // split, MIN_SPLIT_SIZE), step_size
                )
                beat_height = line_height * split
                ms_per_pixel = 60_000.0 / bpm / beat_height
            t += ms_per_pixel

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

    def initialize(self):
        # Flag
        self.IS_SCROLL = False
        self.LATTICE_CLICKED = False
        self.SCROLLBAR_CLICKED = False
        self.LINE_SELECTED = False
        self.MOUSE_CLICKED = False
        self.UPDATE_BLOCK_INFORMATION_TEXTBOX = True
        self.EMIT_BUTTON_PRESS = False
        self.APPLY_ENABLED = False
        self.SCREEN_SIZE_CHANGED = False
        self.MUSIC_PLAYING = False
        self.AUTO_LINE_PASS = False
        self.FIX_LINE = False

        # Save Information
        self.ucs_file_path: str = ""
        self.ucs_save_path: str = ""
        self.ucs_cache_path: str = ""

        # 0 : small, 24px
        # 1 : medium, 36px
        # 2 : large, 48px
        self.step_size_idx = 2

        # Initial Chart Information
        self.format: int = 1
        self.mode: str = "Single"

        # Offset for Step Area and Scrollbar Area
        self.step_x_start = OPTION_WIDTH
        self.measure_x_start = self.step_x_start + STEP_SIZE_MAP[self.step_size_idx] * 5
        self.scrollbar_x_start = self.measure_x_start + MEASURE_DESCRIPTOR_WIDTH

        # Block information
        self.block_info: List[List[int | float]] = [
            [160.0, 4, 2, 0, 1, 0, 0]
        ]  # initial block information

        # Delay unit
        self.delay_unit = DelayUnit.ms

        # Step data
        self.step_data: List[List[int]] = [
            [0, 0, i // 2, i % 2, 1, 0, 0, 0, 0, 0] for i in range(8)
        ]  # initial step data

        # Screen size
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

        # Information for each y
        self.max_y = -1
        # self.y_info: List[List[int]] = [[0, 0] for _ in range(100000)]
        self.y_to_ln: List[int] = [0 for _ in range(100000)]
        self.ln_to_y: List[int] = [0 for _ in range(100000)]

        # selected line info
        self.coor_cur = (0, 0)
        self.coor_base = (0, 0)

        # scroll location info
        self.scr_y = 0

        # scroll bar info
        self.scrollbar_h = SCREEN_HEIGHT - 2 * SCROLLBAR_BUTTON_HEIGHT
        self.scrollbar_y = 0
        self.scrollbar_y_init = 0
        self.scr_mouse_init = -1

        # Element Focus Rectangle
        self.focus_idx_prev = -1
        self.focus_idx = -1

        # Clipboard
        self.clipboard: List[List[int]] | None = None

        # Last Mouse Position
        self.mouse_pos: Tuple[int, int] = (0, 0)

        # Music
        self.scr_to_time: List[int] = [0 for _ in range(100000)]
        self.music: any = None
        self.music_len: int = 0  # in ms
        self.music_speed_idx: int = 3
        self.music_start_time: int = 0  # in ms
        self.music_start_offset: int = 0  # in ms

        # Log
        self.logs: List[str] = []

        # Mode 2 Receptor y location
        self.receptor_y = 0

        self.update_y_info()
        self.update_scr_to_time()
