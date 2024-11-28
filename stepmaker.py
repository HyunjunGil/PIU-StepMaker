import pygame, pygame_gui, numpy as np, time

from tkinter import Tk
from typing import List, Tuple, Dict
from constants import *
from state import State
from scroll_manager import ScrollManager
from ui_element_manager import UIElementManager, ElementBase
from ui_elements import PlayButton
from mouse_manager import MouseManager
from keyboard_manager import KeyboardManager, UndoKey, UpKey, DownKey
from history_manager import HistoryManager, StepChartChangeDelta

from utils import (
    binary_search,
    ms_to_str,
    update_validity,
    num_to_str,
    get_bpm_color,
    ms_to_beats,
    clear_step,
    reduce_diff,
)


class StepMaker:
    def __init__(self, screen: pygame.Surface):

        self.screen = screen
        self.ui_manager = UIElementManager()
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
            LONG_MIDDLE_HALF_IMAGES = [
                pygame.image.load(
                    f"./images/hold_half{i % 5}_{suffix}.png"
                ).convert_alpha()
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
                    LONG_MIDDLE_HALF_IMAGES,
                ]
            )
        self.RECEPTOR_IMAGES = dict()
        for i, suffix in enumerate(["s", "m", "l"]):
            for mode in ["Single", "Double"]:
                self.RECEPTOR_IMAGES[f"{mode}_{i}"] = pygame.image.load(
                    f"./images/receptor_{mode.lower()}_{suffix}.png"
                ).convert_alpha()

    def resize_screen(self, size: Tuple[int, int]):
        state = self.state
        w, h = size
        w = max(
            state.get_step_width() * state.get_cols()
            + OPTION_WIDTH
            + state.get_measure_width()
            + SCROLLBAR_BUTTON_WIDTH,
            w,
        )
        h = max(MIN_SCREEN_HEIGHT, h)
        self.state.screen_width = w
        self.state.screen_height = h
        self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self.ui_manager.manager.set_window_resolution((w, h))
        ScrollManager.update_scrollbar_info(self.state)

    def emit_event(self):
        state = self.state
        if state.EMIT_BUTTON_PRESS:
            element = self.ui_manager.get_ui_element_by_idx(state.focus_idx)
            pygame.event.post(
                pygame.event.Event(
                    pygame_gui.UI_BUTTON_PRESSED,
                    {
                        "user_type": pygame_gui.UI_BUTTON_PRESSED,
                        "ui_element": element.e,
                    },
                )
            )
            state.EMIT_BUTTON_PRESS = False

    def update_ui_elements(self):
        state = self.state

        # Resize screen if screen width
        if state.screen_width < state.scrollbar_x_start + SCROLLBAR_BUTTON_WIDTH:
            self.resize_screen(
                (state.scrollbar_x_start + SCROLLBAR_BUTTON_WIDTH, state.screen_height)
            )

        self.ui_manager.relocate_elements(self.state)

        # Update Block Information Textboxes
        if state.UPDATE_BLOCK_INFORMATION_TEXTBOX:
            self.ui_manager.update_block_information_textbox(state)
            self.ui_manager.ui_elements[BI_APPLY_BUTTON].disable()
            state.APPLY_ENABLED = False
            state.UPDATE_BLOCK_INFORMATION_TEXTBOX = False

        # Update Focused Rectangle Location
        if state.focus_idx != state.focus_idx_prev:
            if state.focus_idx_prev != -1:
                element = self.ui_manager.get_ui_element_by_idx(state.focus_idx_prev)
                element.unfocus()
            state.focus_idx_prev = state.focus_idx

            if state.focus_idx != -1:
                element = self.ui_manager.get_ui_element_by_idx(state.focus_idx)
                element.focus()

        sub_panel = self.ui_manager.get_ui_element_by_idx(
            FILE_LOAD_BUTTON
        ).e.ui_container
        if (
            not (FILE_BUTTON <= state.focus_idx <= FILE_SAVE_AS_BUTTON)
            and sub_panel.visible
        ):
            sub_panel.hide()

        # Update Scrollbar Button Location
        self.ui_manager.relocate_scroll_button(self.state)

        # Update Logger
        if state.logs:
            t = time.strftime("%H:%M:%S")
            logger = self.ui_manager.ui_elements[LOG_TEXTBOX].e
            new_text = logger.html_text + f"\n[{t}] " + "\n".join(state.logs)
            logger.set_text(new_text)
            state.logs.clear()
            if logger.scroll_bar:
                logger.scroll_bar.set_scroll_from_start_percentage(1.0)

        play_button = self.ui_manager.ui_elements[FILE_PLAY_BUTTON].e

        # Update time text
        self.ui_manager.ui_elements[FILE_PLAYTIME_TEXT].e.set_text(
            ms_to_str(state.scr_to_time[state.scr_y + state.receptor_y])
        )

        if state.MUSIC_PLAYING and play_button.text != "Stop":
            play_button.set_text("Stop")
        elif not state.MUSIC_PLAYING and play_button.text != "Play":
            play_button.set_text("Play")

    def process_hold_key(self):
        state = self.state
        pressed_timestamp = state.pressed_timestamp
        current_timestmap = int(time.time() * 1000)
        key, first_timestamp = sorted(pressed_timestamp.items(), key=lambda x: x[1])[0]
        if (
            first_timestamp != INFINITY
            and current_timestmap > first_timestamp + KEY_HOLD_DELAY_MS
        ):
            pressed_timestamp[key] = (
                current_timestmap - KEY_HOLD_DELAY_MS + KEY_HOLD_INTERVAL_MS
            )
            if key == pygame.K_z:
                UndoKey.action(self.history_manager, self.state, None, [])
            elif key == pygame.K_UP:
                UpKey.action(self.history_manager, self.state, None, [])
            elif key == pygame.K_DOWN:
                DownKey.action(self.history_manager, self.state, None, [])

    def process_stepkey(self):
        state = self.state
        if not state.MUSIC_PLAYING:
            return

        y = min(
            max(state.scr_y + state.receptor_y + MUSIC_INPUT_DELAY_IN_PIXEL, 0),
            state.max_y - 1,
        )
        ln = state.y_to_ln[y]

        target_keys = KEY_SINGLE if state.mode == "Single" else KEY_DOUBLE
        pressed_keys = pygame.key.get_pressed()
        stepkey_info, step_data = state.stepkey_info, state.step_data
        for k in target_keys.keys():
            i = target_keys[k]
            col = i + STEP_DATA_OFFSET
            info = stepkey_info[k]
            if not pressed_keys[k] and info.ln_from != -1:
                if ALLOW_LONG_NOTE:
                    if info.ln_from != info.ln_to:
                        info.step_diff.append((info.ln_to, col, 3, 4))
                        step_data[info.ln_to][col] = 4
                    self.history_manager.append(
                        StepChartChangeDelta(
                            ((i, info.ln_to), (i, info.ln_from)),
                            ((i, info.ln_to), (i, info.ln_from)),
                            info.step_diff,
                        )
                    )
                else:
                    self.history_manager.append(
                        StepChartChangeDelta(
                            ((i, info.ln_to), (i, info.ln_from)),
                            ((i, info.ln_to), (i, info.ln_from)),
                            info.step_diff,
                        )
                    )
                info.initialize()

            elif pressed_keys[k]:
                if ALLOW_LONG_NOTE:
                    if info.ln_from == -1:
                        info.ln_from = info.ln_to = ln
                        info.step_diff = info.step_diff + clear_step(
                            step_data, ln, ln + 1, col
                        )
                        info.step_diff.append((ln, col, 0, 1))
                        step_data[ln][col] = 1
                    elif info.ln_to != ln:
                        info.ln_to = ln
                        if ln == info.ln_from + 1:
                            info.step_diff.append((ln - 1, col, 1, 2))
                            step_data[ln - 1][col] = 2
                        info.step_diff.extend(clear_step(step_data, ln, ln + 1, col))
                        info.step_diff.append((ln, col, 0, 3))
                        step_data[ln][col] = 3
                else:
                    if info.ln_from == -1:
                        info.ln_from = info.ln_to = ln
                        info.step_diff.extend(clear_step(step_data, ln, ln + 1, col))
                        info.step_diff.append((ln, col, 0, 1))
                        step_data[ln][col] = 1

    def process_mouse_event(self, event: pygame.Event):
        MouseManager.process_event(self.state, event)
        self.ui_manager.check_ui_element_clicked(self.state, event)

    def process_keyboard_event(self, event: pygame.Event):
        self.keyboard_manager.process_event(
            self.history_manager,
            self.state,
            event,
            self.ui_manager.get_ui_elements(),
        )
        self.emit_event()

    def process_ui_element_event(self, event: pygame.Event):
        self.ui_manager.process_event(self.history_manager, self.state, event)
        self.emit_event()

    def process_ui_manager_event(self, event: pygame.Event):
        self.ui_manager.manager.process_events(event)

    def update_scr_y(self):
        state = self.state
        step_height = state.get_step_height()
        if (
            not state.MUSIC_PLAYING
            and state.MOUSE_CLICKED
            and state.step_x_start <= state.mouse_pos[0] < state.measure_x_start
        ):
            mouse_y = state.mouse_pos[1]
            if mouse_y < 0:
                speed = max(-mouse_y, 100) // 20
                state.scr_y = max(-state.receptor_y, state.scr_y - speed)
            elif state.mouse_pos[1] > state.screen_height:
                speed = max(mouse_y - state.screen_height, 100) // 20
                state.scr_y = min(
                    state.scr_y + speed,
                    max(state.max_y - state.screen_height, 0)
                    - state.receptor_y
                    + step_height,
                )

    def adjust_scr_y_to_music(self):
        state = self.state
        t = int(time.time() * 1000)
        music_speed = MUSIC_SPEED_MAP[state.music_speed_idx]
        if (
            state.music_len != 0
            and state.music_start_offset + (t - state.music_start_time) * music_speed
            > state.music_len
            or state.scr_y
            >= state.max_y - state.receptor_y - state.get_step_height() - 1
        ):
            PlayButton.action(self.history_manager, self.state, None, [])
            self.ui_manager.ui_elements[FILE_PLAY_BUTTON].e.set_text("Play")
            update_validity(state.step_data, 0, len(state.step_data) - 1)
            return

        state.scr_y = (
            binary_search(
                state.scr_to_time[: state.max_y],
                state.music_start_offset
                + music_speed * (int(time.time() * 1000) - state.music_start_time),
            )
            - state.receptor_y
        )

    def draw(self):

        # If music is playing, adjust scr.y
        if self.state.MUSIC_PLAYING:
            self.adjust_scr_y_to_music()

        # ORDERING IS IMPORTANT
        self.screen.fill(WHITE)

        self.draw_background()

        self.draw_scrollbar()

        self.draw_hovered_area()

        self.draw_step_chart()

        self.draw_selected_area()

        self.draw_line_descriptor()

        self.ui_manager.draw(self.state, self.screen)

        self.draw_focus_rect()

        pygame.display.flip()

    def draw_background(self):
        state = self.state
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        cols = state.get_cols()
        ln = y_to_ln[state.scr_y]
        y = ln_to_y[ln]
        step_size = state.get_step_width()
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

    def draw_step_chart(self):
        state, screen = self.state, self.screen
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        cols = state.get_cols()
        ln = y_to_ln[max(state.scr_y, 0)]
        y = ln_to_y[ln]
        font = pygame.font.SysFont("Verdana", state.get_font_size())
        step_size, step_height = state.get_step_width(), state.get_step_height()
        tot_ln = len(step_data)
        screen_bottom = state.scr_y + state.screen_height
        bpm_list = [block[BLOCK_BPM_IDX] for block in block_info]
        bpm_min, bpm_max = min(bpm_list), max(bpm_list)
        block_idx, bpm, beat, split, delay, dy = -1, 0, 0, 0, 0, 0

        pygame.draw.rect(
            screen,
            SEMI_BLACK,
            (
                OPTION_WIDTH,
                state.max_y - state.scr_y,
                step_size * cols,
                state.screen_height,
            ),
        )

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
                dy = min(max((step_height * 2) // split, MIN_SPLIT_SIZE), step_height)

            if row[STEP_DATA_VD_IDX] == 0:
                pygame.draw.rect(
                    screen,
                    LIGHT_RED,
                    (
                        state.step_x_start,
                        y - state.scr_y,
                        step_size * cols,
                        step_size,
                    ),
                )

            if mi == 0 and bti == 0 and si == 0:  # Start of Blcok
                ln_from, ln_to = state.get_block_range_by_y(y)
                measure_height = ln_to_y[ln_to] - ln_to_y[ln_from]
                pygame.draw.rect(
                    screen,
                    get_bpm_color(bpm_min, bpm_max, bpm),
                    (
                        state.measure_x_start,
                        y - state.scr_y,
                        state.get_measure_width(),
                        measure_height,
                    ),
                )
                pygame.draw.line(
                    screen,
                    RED,
                    (state.step_x_start, y - state.scr_y),
                    (state.scrollbar_x_start, y - state.scr_y),
                    3,
                )
                text = font.render("{}:{}".format(bi + 1, mi + 1), True, BLACK)
                text_rect = text.get_rect()
                text_rect.topright = (state.scrollbar_x_start, y - state.scr_y)

                screen.blit(text, text_rect)

                # Draw current measure description at the top right
                block = block_info[step_data[ln][STEP_DATA_BI_IDX]]
                bpm, delay = block[BLOCK_BPM_IDX], block[BLOCK_DL_IDX]
                delay_beat = ms_to_beats(bpm, delay)
                text = font.render(
                    "{}bpm\n{}".format(
                        num_to_str(bpm),
                        (
                            f"{delay_beat}beats"
                            if isinstance(delay_beat, int) and delay_beat != 0
                            else f"{num_to_str(delay)}ms"
                        ),
                    ),
                    True,
                    BLACK,
                )
                text_rect = text.get_rect()
                text_rect.topleft = (state.measure_x_start, y - state.scr_y)
                screen.blit(text, text_rect)

            elif bti == 0 and si == 0:  # Start of Measure
                # Fill background
                pygame.draw.line(
                    screen,
                    ROYAL_BLUE,
                    (state.step_x_start, y - state.scr_y),
                    (state.scrollbar_x_start, y - state.scr_y),
                    2,
                )
                text = font.render("{}:{}".format(bi + 1, mi + 1), True, BLACK)
                text_rect = text.get_rect()
                text_rect.topright = (state.scrollbar_x_start, y - state.scr_y)

                screen.blit(text, text_rect)

            elif si == 0:  # Start of Beat
                pygame.draw.line(
                    screen,
                    ROYAL_BLUE,
                    (state.step_x_start, y - state.scr_y),
                    (state.measure_x_start, y - state.scr_y),
                    1,
                )

            elif triple_split:
                if si % (split // 3) == 0:
                    pygame.draw.line(
                        screen,
                        LIGHT_GREEN,
                        (state.step_x_start, y - state.scr_y),
                        (state.measure_x_start, y - state.scr_y),
                        1,
                    )
            elif even_split:
                if si % (split // 2) == 0:
                    pygame.draw.line(
                        screen,
                        LIGHT_GREEN,
                        (state.step_x_start, y - state.scr_y),
                        (state.measure_x_start, y - state.scr_y),
                        1,
                    )

            # Draw step if exists
            cols = 5 if state.mode == "Single" else 10
            for idx in range(cols):
                col = idx + STEP_DATA_OFFSET
                image = None
                if row[col] == 0:
                    continue
                elif row[col] in [2, 3]:
                    image_rects.append(
                        (ln + (INFINITY if row[col] == 2 else 0), y, idx, row[col])
                    )

                    if step_height > step_size:
                        h = step_size
                        half_size = step_size // 2
                        while h < dy:
                            dh = dy - h
                            if dh <= half_size:
                                image_rects.append((ln, y + dy - half_size, idx, 5))
                                break
                            elif dh <= step_size:
                                image_rects.append((ln, y + dy - step_size, idx, 3))
                                break
                            else:
                                image_rects.append((ln, y + h, idx, 3))
                                h += step_size

                else:
                    image_rects.append((ln, y, idx, row[col]))

            y += dy
            ln += 1

        # Draw Receptor Image
        screen.blit(
            self.RECEPTOR_IMAGES[f"{state.mode}_{state.step_size_idx}"],
            (state.step_x_start, state.receptor_y),
        )

        # Draw Images
        image_rects = sorted(image_rects, key=lambda x: x[0])
        for rect in image_rects:
            z, y, col, code = rect
            screen.blit(
                self.TOTAL_IMAGES[state.step_size_idx][code][col],
                (state.step_x_start + col * step_size, y - state.scr_y),
            )

    def draw_scrollbar(self):
        state, screen = self.state, self.screen
        denom = (state.screen_height - 2 * SCROLLBAR_BUTTON_HEIGHT) - state.scrollbar_h

        max_y = state.max_y - state.get_step_height()
        if state.SCROLLBAR_CLICKED:
            _, mouse_y = pygame.mouse.get_pos()
            new_scrollbar_y = min(
                max(
                    state.scrollbar_y_init + (mouse_y - state.scr_mouse_init),
                    SCROLLBAR_BUTTON_HEIGHT,
                ),
                (state.screen_height - SCROLLBAR_BUTTON_HEIGHT) - state.scrollbar_h,
            )
            if denom != 0:
                new_scr_y = (
                    (new_scrollbar_y - SCROLLBAR_BUTTON_HEIGHT) * max_y
                ) // denom - state.receptor_y
                state.scrollbar_y = new_scrollbar_y
                state.scr_y = new_scr_y
        else:
            state.scrollbar_y = ((state.scr_y + state.receptor_y) * denom) // (
                max_y
            ) + SCROLLBAR_BUTTON_HEIGHT

        pygame.draw.rect(
            screen,
            DARK_GRAY,
            (
                state.scrollbar_x_start,
                state.scrollbar_y,
                SCROLLBAR_BUTTON_WIDTH,
                state.scrollbar_h,
            ),
        )

    def draw_hovered_area(self):
        state, screen = self.state, self.screen
        step_size = state.get_step_width()
        step_height = state.get_step_height()
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
                step_height,
            ),
        )

        # Draw middle line if double mode
        if state.mode == "Double":
            pygame.draw.line(
                self.screen,
                MIDDLE_GRAY,
                (state.step_x_start + 5 * step_size, -state.scr_y),
                (state.step_x_start + 5 * step_size, state.max_y - state.scr_y),
                1,
            )

    def draw_selected_area(self):

        state, screen = self.state, self.screen
        step_size = state.get_step_width()
        step_height = state.get_step_height()
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
                abs(y_base - y_cur) + step_height,
            ),
            3,
        )

    def draw_focus_rect(self):
        state, screen = self.state, self.screen
        focus_idx = state.focus_idx
        if focus_idx == -1:
            return
        element = self.ui_manager.get_ui_element_by_idx(state.focus_idx)
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

        line_text = pygame.font.SysFont("Verdana", state.get_font_size()).render(
            txt, True, BLACK, LIGHT_GRAY
        )
        line_text_rect = line_text.get_rect()
        line_text_rect.bottomleft = (state.step_x_start, state.screen_height)
        screen.blit(line_text, line_text_rect)
