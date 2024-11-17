import pygame, pygame_gui, numpy as np

from typing import List, Tuple, Dict
from enum import Enum
from constants import *
from state import State
from scroll_manager import ScrollManager
from ui_element_manager import UIElementManager
from mouse_manager import MouseManager
from keyboard_manager import KeyboardManager
from file_manager import *


def focus_idx_to_str(idx: int):
    assert idx != -1, "Focus idx shoud not be -1"
    res = str(idx)
    return "0" * (3 - len(res)) + res


class StepMaker:
    def __init__(self, screen: pygame.Surface):

        self.screen = screen
        manager = pygame_gui.UIManager(screen.size)
        self.ui_manger = UIElementManager(manager)
        self.keyboard_manager = KeyboardManager()
        self.state = State()

        # Images
        # Image Load
        SHORT_IMAGES = [
            pygame.image.load(f"./images/note{i % 5}_48.png").convert_alpha()
            for i in range(10)
        ]
        LONG_HEAD_IMAGES = [
            pygame.image.load(f"./images/start{i % 5}_48.png").convert_alpha()
            for i in range(10)
        ]
        LONG_MIDDLE_IMAGES = [
            pygame.image.load(f"./images/hold{i % 5}_48.png").convert_alpha()
            for i in range(10)
        ]
        LONG_TAIL_IMAGES = [
            pygame.image.load(f"./images/end{i % 5}_48.png").convert_alpha()
            for i in range(10)
        ]

        self.TOTAL_IMAGES = [
            [None for _ in range(10)],
            SHORT_IMAGES,
            LONG_HEAD_IMAGES,
            LONG_MIDDLE_IMAGES,
            LONG_TAIL_IMAGES,
        ]

    def load_initial_ucs_file(self, path: str):
        load_ucs_file(path, self.state)
        ScrollManager.update_scrollbar_info(self.state)
        self.ui_manger.update_block_information_textbox(self.state)
        self.ui_manger.ui_elements["012_BI_Apply"].e.disable()

    def draw(self):
        self.screen.fill(WHITE)

        self.draw_frame()

        self.draw_scrollbar()

        self.draw_selected_lines()

        self.draw_line_descriptor()

        self.draw_step_chart()

        self.draw_focus_rect()

        self.ui_manger.draw(self.state, self.screen)

        pygame.display.flip()

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
        self._add_rectangle_with_text(
            "m/s",
            st,
            (BI_x2, BLOCK_INFO_AREA_Y + BI_y3, sw, sh),
            WHITE,
        )
        # pass

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
        step_data, block_info, y_info = state.get_step_info()
        ln, y = y_info[state.scr_y][0], y_info[state.scr_y][1]
        font = pygame.font.SysFont("Verdana", 18)
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
                dy = min(
                    max((state.step_size * 2) // split, MIN_SPLIT_SIZE), state.step_size
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
                text_rect.topleft = (state.measure_x_start, y - state.scr_y)

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
                text_rect.topleft = (state.measure_x_start, y - state.scr_y)

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
                self.TOTAL_IMAGES[code][col],
                (state.step_x_start + col * state.step_size, y - state.scr_y),
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
        # print(state.scrollbar_x_start, state.scrollbar_y, state.scrollbar_h)

    def draw_selected_lines(self):

        state, screen = self.state, self.screen
        cols = 5 if state.mode == "Single" else 10

        # Draw hovered square
        pygame.draw.rect(
            screen,
            LIGHT_GRAY,
            (
                state.step_x_start,
                state.y_cur - state.scr_y,
                cols * state.step_size,
                state.step_size,
            ),
        )

        # Draw selection square
        pygame.draw.rect(
            screen,
            BLACK,
            (
                state.step_x_start,
                min(state.y_base, state.y_cur) - state.scr_y,
                state.step_size * cols,
                abs(state.y_base - state.y_cur) + state.step_size,
            ),
            3,
        )

    def draw_focus_rect(self):
        state, screen = self.state, self.screen

        focus_idx = state.focus_idx
        if focus_idx == -1:
            return
        focus_idx_str = focus_idx_to_str(state.focus_idx)
        ui_elements = self.ui_manger.get_ui_elements()
        for k, element in ui_elements.items():
            if k.startswith(focus_idx_str):
                x, y = element.e.get_abs_rect().topleft
                w, h = element.e.get_abs_rect().size
                pygame.draw.rect(screen, DARK_GRAY, (x, y, w, h), 3)
                break

    def draw_line_descriptor(self):
        state, screen = self.state, self.screen
        step_data, block_info, y_info = state.get_step_info()
        ln_from, ln_to = (
            y_info[min(state.y_cur, state.y_base)][0],
            y_info[max(state.y_cur, state.y_base)][0],
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

    def resize_screen(self, event: pygame.Event):
        w, h = event.size
        self.state.screen_width = w
        self.state.screen_height = h
        self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self.ui_manger.manager.set_window_resolution((w, h))
        ScrollManager.update_scrollbar_info(self.state)

    def update_block_information_textbox(self):
        if self.state.UPDATE_BLOCK_INFORMATION_TEXTBOX:
            self.ui_manger.update_block_information_textbox(self.state)
            self.state.UPDATE_BLOCK_INFORMATION_TEXTBOX = False
        elif self.state.focus_idx == -1 and self.state.focus_idx_prev != -1:
            focus_idx_str = focus_idx_to_str(self.state.focus_idx_prev)
            for k, element in self.ui_manger.get_ui_elements().items():
                if k.startswith(focus_idx_str):
                    element.unfocus()
                    break
            self.state.focus_idx_prev = -1
        elif 5 <= self.state.focus_idx < 12:
            if self.state.focus_idx_prev != -1:
                focus_idx_str = focus_idx_to_str(self.state.focus_idx_prev)
                for k, element in self.ui_manger.get_ui_elements().items():
                    if k.startswith(focus_idx_str):
                        element.unfocus()
                        break
                self.state.focus_idx_prev = -1
            focus_idx_str = focus_idx_to_str(self.state.focus_idx)
            for k, element in self.ui_manger.get_ui_elements().items():
                if k.startswith(focus_idx_str):
                    element.focus()
                    break

    def process_mouse_event(self, event: pygame.Event):
        MouseManager.process_event(self.state, event)
        self.ui_manger.check_textbox_clicked(self.state, event)
        self.update_block_information_textbox()

    def process_keyboard_event(self, event: pygame.Event):
        self.keyboard_manager.process_event(self.state, event)
        self.update_block_information_textbox()

    def process_ui_element_event(self, event: pygame.Event):
        self.ui_manger.process_event(self.state, event)
        self.update_block_information_textbox()

    def process_ui_manager_event(self, event: pygame.Event):
        self.ui_manger.manager.process_events(event)
