import pygame, pygame_gui, numpy as np, time, pandas as pd

from tkinter import Tk
from typing import List, Tuple, Dict
from constants import *
from state import State
from scroll_manager import ScrollManager
from ui_element_manager import UIElementManager, ElementBase
from mouse_manager import MouseManager
from keyboard_manager import KeyboardManager
from history_manager import HistoryManager

from utils import binary_search


class StepMaker:
    def __init__(self, screen: pygame.Surface):

        self.screen = screen
        manager = pygame_gui.UIManager(screen.size)
        self.ui_manager = UIElementManager(manager)
        self.keyboard_manager = KeyboardManager()
        self.state = State()
        self.history_manager = HistoryManager()
        self.history_manager.initialize(self.state)
        self.ui_manager.relocate_scroll_button(self.state)

        # Images
        # Image Load
        self.TOTAL_IMAGES = []
        for suffix in ["s", "m", "l"]:
            SHORT_IMAGES = [
                pygame.image.load(f"./images/note{i % 5}_{suffix}.png").convert_alpha()
                for i in range(10)
            ]
            LONG_HEAD_IMAGES = [
                pygame.image.load(f"./images/start{i % 5}_{suffix}.png").convert_alpha()
                for i in range(10)
            ]
            LONG_MIDDLE_IMAGES = [
                pygame.image.load(f"./images/hold{i % 5}_{suffix}.png").convert_alpha()
                for i in range(10)
            ]
            LONG_TAIL_IMAGES = [
                pygame.image.load(f"./images/end{i % 5}_{suffix}.png").convert_alpha()
                for i in range(10)
            ]

            self.TOTAL_IMAGES.append(
                [
                    [None for _ in range(10)],
                    SHORT_IMAGES,
                    LONG_HEAD_IMAGES,
                    LONG_MIDDLE_IMAGES,
                    LONG_TAIL_IMAGES,
                ]
            )

    def _get_focused_ui_element(self, idx: int) -> ElementBase:
        ui_elements = self.ui_manager.get_ui_elements()
        assert idx != -1, "Focus idx shoud not be -1"
        focus_idx_str = str(idx)
        focus_idx_str = "0" * (3 - len(focus_idx_str)) + focus_idx_str
        for k, element in ui_elements.items():
            if k.startswith(focus_idx_str):
                return element

    def resize_screen(self, event: pygame.Event):
        w, h = event.size
        self.state.screen_width = w
        self.state.screen_height = h
        self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self.ui_manager.manager.set_window_resolution((w, h))
        self.ui_manager.relocate_scroll_button(self.state)
        ScrollManager.update_scrollbar_info(self.state)

    def update_ui_elements(self):
        state = self.state

        if state.UPDATE_BLOCK_INFORMATION_TEXTBOX:
            self.ui_manager.update_block_information_textbox(state)
            self.ui_manager.ui_elements["013_BI_Apply"].disable()
            state.APPLY_ENABLED = False
            state.UPDATE_BLOCK_INFORMATION_TEXTBOX = False

        if state.EMIT_BUTTON_PRESS:
            element = self._get_focused_ui_element(state.focus_idx)
            pygame.event.post(
                pygame.event.Event(
                    pygame_gui.UI_BUTTON_PRESSED,
                    {
                        "user_type": pygame_gui.UI_BUTTON_PRESSED,
                        "ui_element": element.e,
                        # "ui_object_id": button.most_specific_combined_id,
                    },
                )
            )
            state.EMIT_BUTTON_PRESS = False

        if state.focus_idx != state.focus_idx_prev:
            if state.focus_idx_prev != -1:
                element = self._get_focused_ui_element(state.focus_idx_prev)
                element.unfocus()
            state.focus_idx_prev = state.focus_idx

            if state.focus_idx != -1:
                element = self._get_focused_ui_element(state.focus_idx)
                element.focus()

        self.ui_manager.relocate_scroll_button(self.state)

        play_button = self.ui_manager.ui_elements["000_Play"].e
        if state.MUSIC_PLAYING and play_button.text != "Stop":
            play_button.set_text("Stop")
        elif not state.MUSIC_PLAYING and play_button.text != "Play":
            play_button.set_text("Play")

    def process_mouse_event(self, event: pygame.Event):
        MouseManager.process_event(self.state, event)
        self.ui_manager.check_textbox_clicked(self.state, event)
        self.update_ui_elements()

    def process_keyboard_event(self, event: pygame.Event):
        self.keyboard_manager.process_event(self.history_manager, self.state, event)
        self.update_ui_elements()

    def process_ui_element_event(self, event: pygame.Event):
        self.ui_manager.process_event(self.history_manager, self.state, event)
        self.update_ui_elements()

    def process_ui_manager_event(self, event: pygame.Event):
        self.ui_manager.manager.process_events(event)

    def update_scr_y(self):
        state = self.state
        step_size = state.get_step_size()
        if (
            not state.MUSIC_PLAYING
            and state.MOUSE_CLICKED
            and state.step_x_start <= state.mouse_pos[0] < state.measure_x_start
        ):
            mouse_y = state.mouse_pos[1]
            if mouse_y < 0:
                speed = max(-mouse_y, 100) // 20
                state.scr_y = max(0, state.scr_y - speed)
            elif state.mouse_pos[1] > state.screen_height:
                speed = max(mouse_y - state.screen_height, 100) // 20
                state.scr_y = min(
                    state.max_y - state.screen_height + step_size,
                    state.scr_y + speed,
                )

    def adjust_scr_y_to_music(self):
        state = self.state
        t = int(time.time() * 1000)
        if state.music_start_offset + t - state.music_start_time > state.music_len:
            state.MUSIC_PLAYING = False
            self.ui_manager.ui_elements["000_Play"].e.set_text("Play")
            return
        state.scr_y = binary_search(
            state.scr_to_time[: state.max_y],
            state.music_start_offset + int(time.time() * 1000) - state.music_start_time,
        )
        pass

    def draw(self):
        # print(
        #     pd.Timestamp(time.time(), tz="utc", unit="s").strftime(
        #         "%Y-%m-%d %H:%M:%S.%f"
        #     )
        # )

        # If music is playing, adjust scr.y
        if self.state.MUSIC_PLAYING:
            self.adjust_scr_y_to_music()

        # ORDERING IS IMPORTANT
        self.screen.fill(WHITE)

        self.draw_background()

        self.draw_frame()

        self.draw_scrollbar()

        self.draw_hovered_area()

        self.draw_step_chart()

        self.draw_selected_area()

        self.draw_line_descriptor()

        self.draw_focus_rect()

        self.ui_manager.draw(self.state, self.screen)

        pygame.display.flip()

    def draw_background(self):
        state = self.state
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        cols = state.get_cols()
        ln = y_to_ln[state.scr_y]
        y = ln_to_y[ln]
        step_size = state.get_step_size()
        screen_bottom = state.scr_y + state.screen_height

        while ln < len(step_data) and y < screen_bottom:
            block_idx = step_data[ln][STEP_DATA_BI_IDX]
            ln_from, ln_to = state.get_block_range_by_block_idx(block_idx)
            pygame.draw.rect(
                self.screen,
                LIGHT_BLUE if block_idx % 2 == 0 else LIGHT_YELLOW,
                (
                    state.step_x_start,
                    ln_to_y[ln_from] - state.scr_y,
                    step_size * cols,
                    ln_to_y[ln_to] - ln_to_y[ln_from],
                ),
            )
            ln, y = ln_to, ln_to_y[ln_to]

    def _add_text(
        self,
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

        self.screen.blit(text_surface, rect)

    def _add_rectangle_with_text(
        self,
        text: str,
        font_size: int,
        rect_info: Tuple[int, int, int, int],
        rect_color: Tuple[int, int, int] = WHITE,
        text_color: Tuple[int, int, int] = BLACK,
    ):
        rect = pygame.Rect(rect_info)
        text_surface = pygame.font.SysFont("Verdana", font_size).render(
            text, True, text_color
        )
        text_rect = text_surface.get_rect(center=rect.center)
        pygame.draw.rect(self.screen, rect_color, rect)
        self.screen.blit(text_surface, text_rect)

    def draw_frame(self):
        # Draw lattice
        state = self.state

        # Control Area
        pygame.draw.rect(
            self.screen, BLACK, (0, 0, OPTION_WIDTH, state.screen_height), 3
        )
        pygame.draw.rect(
            self.screen,
            BLACK,
            (0, BASIC_ACTION_AREA_HEIGHT, OPTION_WIDTH, BLOCK_INFO_AREA_HEIGHT),
            3,
        )
        pygame.draw.rect(
            self.screen,
            BLACK,
            (
                (
                    0,
                    BLOCK_OPER_AREA_Y - 3,
                    OPTION_WIDTH,
                    BLOCK_OPER_AREA_HEIGHT,
                ),
            ),
            3,
        )
        # Draw "Block Information" Section
        offset = BLOCK_INFO_GAP
        x0 = BLOCK_INFO_GAP
        x1 = x0 + 120
        y0 = BLOCK_INFO_AREA_Y
        st, sw, sh = 12, 60, 20
        self._add_text(
            "Block Information",
            BLOCK_INFO_GAP,
            BLOCK_INFO_AREA_Y + BLOCK_INFO_GAP,
            30,
            0,
            BLACK,
        )
        offset += 30
        self._add_rectangle_with_text(
            "BPM",
            st,
            (BI_x0, BLOCK_INFO_AREA_Y + BI_y0, sw, sh),
            LIGHT_GRAY,
        )
        self._add_rectangle_with_text(
            "Measures",
            st,
            (BI_x2, BLOCK_INFO_AREA_Y + BI_y0, sw, sh),
            LIGHT_GRAY,
        )
        offset += sh + BLOCK_INFO_GAP
        self._add_rectangle_with_text(
            "B/M",
            st,
            (BI_x0, BLOCK_INFO_AREA_Y + BI_y1, sw, sh),
            LIGHT_GRAY,
        )
        self._add_rectangle_with_text(
            "Beats",
            st,
            (BI_x2, BLOCK_INFO_AREA_Y + BI_y1, sw, sh),
            LIGHT_GRAY,
        )
        offset += sh + BLOCK_INFO_GAP
        self._add_rectangle_with_text(
            "S/B",
            st,
            (BI_x0, BLOCK_INFO_AREA_Y + BI_y2, sw, sh),
            LIGHT_GRAY,
        )
        self._add_rectangle_with_text(
            "Splits",
            st,
            (BI_x2, BLOCK_INFO_AREA_Y + BI_y2, sw, sh),
            LIGHT_GRAY,
        )
        offset += sh + BLOCK_INFO_GAP
        self._add_rectangle_with_text(
            "Delay",
            st,
            (BI_x0, BLOCK_INFO_AREA_Y + BI_y3, sw, sh),
            LIGHT_GRAY,
        )

        # Draw "Block Operation" Section
        self._add_text(
            "Block Operation",
            10,
            BLOCK_OPER_AREA_Y + 10,
            30,
            0,
            BLACK,
        )

        # Measure Descriptor Area
        pygame.draw.line(
            self.screen,
            LIGHT_GRAY,
            (state.measure_x_start, 0),
            (state.measure_x_start, state.screen_height),
            2,
        )

        # Scrollbar Area
        pygame.draw.rect(
            self.screen,
            LIGHT_GRAY,
            (state.scrollbar_x_start, 0, SCROLL_BAR_WIDTH, state.screen_height),
            3,
        )

    def draw_step_chart(self):
        state = self.state
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        cols = state.get_cols()
        ln = y_to_ln[state.scr_y]
        y = ln_to_y[ln]
        font = pygame.font.SysFont("Verdana", 18)
        step_size = state.get_step_size()
        tot_ln = len(step_data)
        screen_bottom = state.scr_y + state.screen_height
        block_idx, bpm, beat, split, delay, dy = -1, 0, 0, 0, 0, 0
        even_split, triple_split = False, False
        if split % 3 == 0:
            even_split, triple_split = False, True
        elif split % 2 == 0:
            even_split, triple_split = True, False
        else:
            even_split, triple_split = False, False
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
                block_idx, bpm, beat, split, delay = (
                    bi,
                    info[0],
                    info[1],
                    info[2],
                    info[3],
                )
                if split % 3 == 0:
                    even_split, triple_split = False, True
                elif split % 2 == 0:
                    even_split, triple_split = True, False
                else:
                    even_split, triple_split = False, False
                dy = min(max((step_size * 2) // split, MIN_SPLIT_SIZE), step_size)

            # Fill background
            bg_color = None
            if row[STEP_DATA_VD_IDX] == 0:
                pygame.draw.rect(
                    self.screen,
                    LIGHT_RED,
                    (
                        state.step_x_start,
                        y - state.scr_y,
                        step_size * cols + 10,
                        step_size,
                    ),
                )

            if mi == 0 and bti == 0 and si == 0:  # Start of Blcok
                pygame.draw.line(
                    self.screen,
                    RED,
                    (state.step_x_start, y - state.scr_y),
                    (state.scrollbar_x_start, y - state.scr_y),
                    3,
                )
                text = font.render("{}:{}".format(bi + 1, mi + 1), True, BLACK)
                text_rect = text.get_rect()
                text_rect.topright = (state.measure_x_start, y - state.scr_y)

                self.screen.blit(text, text_rect)

            elif bti == 0 and si == 0:  # Start of Measure
                pygame.draw.line(
                    self.screen,
                    ROYAL_BLUE,
                    (state.step_x_start, y - state.scr_y),
                    (state.scrollbar_x_start, y - state.scr_y),
                    2,
                )
                text = font.render("{}:{}".format(bi + 1, mi + 1), True, BLACK)
                text_rect = text.get_rect()
                text_rect.topright = (state.measure_x_start, y - state.scr_y)

                self.screen.blit(text, text_rect)

            elif si == 0:  # Start of Beat
                pygame.draw.line(
                    self.screen,
                    ROYAL_BLUE,
                    (state.step_x_start, y - state.scr_y),
                    (state.measure_x_start, y - state.scr_y),
                    1,
                )

            elif triple_split:
                if si % (split // 3) == 0:
                    pygame.draw.line(
                        self.screen,
                        LIGHT_GREEN,
                        (state.step_x_start, y - state.scr_y),
                        (state.measure_x_start, y - state.scr_y),
                        1,
                    )
            elif even_split:
                if si % (split // 2) == 0:
                    pygame.draw.line(
                        self.screen,
                        LIGHT_GREEN,
                        (state.step_x_start, y - state.scr_y),
                        (state.measure_x_start, y - state.scr_y),
                        1,
                    )

            # Draw step if exists
            cols = 5 if state.mode == "Single" else 10
            for col in range(cols):
                idx = col + STEP_DATA_OFFSET
                image = None
                if row[idx] == 0:
                    continue
                elif row[idx] == 2:
                    image = self.TOTAL_IMAGES[0][col % 5]
                    image_rects.append((ln + INF, y, col, 2))
                else:
                    image_rects.append((ln, y, col, row[idx]))

            y += dy
            ln += 1

        # Draw Images
        image_rects = sorted(image_rects, key=lambda x: x[0])
        for rect in image_rects:
            z, y, col, code = rect
            self.screen.blit(
                self.TOTAL_IMAGES[state.step_size_idx][code][col],
                (state.step_x_start + col * step_size, y - state.scr_y),
            )

    def draw_scrollbar(self):
        state, screen = self.state, self.screen
        if state.SCROLLBAR_CLICKED:
            _, mouse_y = pygame.mouse.get_pos()
            state.scrollbar_y = min(
                max(
                    state.scrollbar_y_init + (mouse_y - state.scr_mouse_init),
                    SCROLLBAR_BUTTON_HEIGHT,
                ),
                (state.screen_height - SCROLLBAR_BUTTON_HEIGHT) - state.scrollbar_h,
            )
            state.scr_y = (
                (state.scrollbar_y - SCROLLBAR_BUTTON_HEIGHT) * state.max_y
            ) // (
                (state.screen_height - 2 * SCROLLBAR_BUTTON_HEIGHT) - state.scrollbar_h
            )
        else:
            state.scrollbar_y = (
                SCROLLBAR_BUTTON_HEIGHT
                + (
                    (
                        (state.screen_height - 2 * SCROLLBAR_BUTTON_HEIGHT)
                        - state.scrollbar_h
                    )
                    * state.scr_y
                )
                // state.max_y
            )

        pygame.draw.rect(
            screen,
            DARK_GRAY,
            (
                state.scrollbar_x_start,
                state.scrollbar_y,
                SCROLL_BAR_WIDTH,
                state.scrollbar_h,
            ),
        )

    def draw_hovered_area(self):
        state, screen = self.state, self.screen
        step_size = state.get_step_size()
        cols = 5 if state.mode == "Single" else 10

        y_cur, y_base = (
            state.ln_to_y[state.coor_cur[1]],
            state.ln_to_y[state.coor_base[1]],
        )
        x_cur, x_base = (
            state.step_x_start + state.coor_cur[0] * step_size,
            state.step_x_start + state.coor_base[0] * step_size,
        )

        # Draw hovered square
        pygame.draw.rect(
            screen,
            LIGHT_GRAY,
            (
                state.step_x_start,
                y_cur - state.scr_y,
                cols * step_size,
                step_size,
            ),
        )
        pass

    def draw_selected_area(self):

        state, screen = self.state, self.screen
        step_size = state.get_step_size()
        cols = 5 if state.mode == "Single" else 10

        y_cur, y_base = (
            state.ln_to_y[state.coor_cur[1]],
            state.ln_to_y[state.coor_base[1]],
        )
        x_cur, x_base = (
            state.step_x_start + state.coor_cur[0] * step_size,
            state.step_x_start + state.coor_base[0] * step_size,
        )

        # Draw selection square
        pygame.draw.rect(
            screen,
            BLACK,
            (
                min(x_base, x_cur),
                min(y_base, y_cur) - state.scr_y,
                abs(x_base - x_cur) + step_size,
                abs(y_base - y_cur) + step_size,
            ),
            3,
        )

    def draw_focus_rect(self):
        state, screen = self.state, self.screen
        focus_idx = state.focus_idx
        if focus_idx == -1:
            return
        element = self._get_focused_ui_element(state.focus_idx)
        x, y = element.e.get_abs_rect().topleft
        w, h = element.e.get_abs_rect().size
        pygame.draw.rect(screen, DARK_GRAY, (x, y, w, h), 3)

    def draw_line_descriptor(self):
        state, screen = self.state, self.screen
        step_data, block_info = state.get_step_info()
        y_to_ln = state.y_to_ln
        y_cur, y_base = (
            state.ln_to_y[state.coor_cur[1]],
            state.ln_to_y[state.coor_base[1]],
        )
        ln_from, ln_to = (
            y_to_ln[min(y_cur, y_base)],
            y_to_ln[max(y_cur, y_base)],
        )

        if ln_from == ln_to:
            txt = "Ln{}".format(ln_from + 1)
        else:
            txt = "Ln{}~{} ({} selected)".format(
                ln_from + 1, ln_to + 1, ln_to - ln_from + 1
            )

        line_text = pygame.font.SysFont("Verdana", 12).render(
            txt, True, BLACK, LIGHT_GRAY
        )
        line_text_rect = line_text.get_rect()
        line_text_rect.bottomleft = (state.step_x_start, state.screen_height)
        screen.blit(line_text, line_text_rect)
