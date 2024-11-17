import pygame, pygame_gui

from constants import *
from state import State


class MouseManager:
    def __init__(self):
        pass

    def _process_mouse_wheel_up(state: State, event: pygame.Event):
        state.IS_SCROLL = True
        state.scr_y = max(state.scr_y - SCROLL_SPEED, 0)

    def _process_mouse_wheel_down(state: State, event: pygame.Event):
        state.IS_SCROLL = True
        state.scr_y = min(state.scr_y + SCROLL_SPEED, state.max_y)

    def _process_mouse_click(state: State, event: pygame.Event):
        state.LATTICE_CLICKED = state.SCROLLBAR_CLICKED = False
        state.focus_idx = -1

        mouse_x, mouse_y = event.pos

        pressed_keys = pygame.key.get_pressed()

        if state.step_x_start <= mouse_x < state.measure_x_start:
            state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True
            state.LATTICE_CLICKED, state.SCROLLBAR_CLICKED = True, False
            state.focus_idx = -1

            state.y_cur = state.y_info[mouse_y + state.scr_y][1]

            if not pressed_keys[pygame.K_LSHIFT]:
                state.y_base = state.y_cur

        elif state.measure_x_start <= mouse_x < state.scrollbar_x_start:
            state.LATTICE_CLICKED, state.SCROLLBAR_CLICKED = False, False
            state.focus_idx = -1

            step_data, block_info, y_info = state.get_step_info()

            ln, y = (
                y_info[mouse_y + state.scr_y][0],
                y_info[mouse_y + state.scr_y][1],
            )

            line_info = step_data[ln]
            block = block_info[line_info[STEP_DATA_BI_IDX]]
            # line at start of measure
            ln_base = ln - line_info[STEP_DATA_BT_IDX] * line_info[STEP_DATA_SP_IDX]
            ln_cur = ln_base + block[1] * block[2]
            state_y_cur = state_y_base = mouse_y + state.scr_y
            while y_info[state.y_base][0] >= ln_base and y > 0:
                state.y_base -= 1
            while y_info[state.y_cur][0] < ln_cur and y < state.max_y - 1:
                state.y_cur += 1

        elif (
            state.scrollbar_x_start
            <= mouse_x
            < state.scrollbar_x_start + SCROLL_BAR_WIDTH
        ) and (state.scrollbar_y <= mouse_y < state.scrollbar_y + state.scrollbar_h):
            state.LATTICE_CLICKED, state.SCROLLBAR_CLICKED = False, True
            state.focus_idx = -1

            state.scr_mouse_init = mouse_y
            state.scrollbar_y_init = state.scrollbar_y

    def _process_mouse_up(state: State, event: pygame.Event):
        state.IS_SCROLL, state.LATTICE_CLICKED, state.SCROLLBAR_CLICKED = (
            False,
            False,
            False,
        )

    @staticmethod
    def process_event(state: State, event: pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
            MouseManager._process_mouse_wheel_up(state, event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
            MouseManager._process_mouse_wheel_down(state, event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            MouseManager._process_mouse_click(state, event)
        elif event.type == pygame.MOUSEBUTTONUP:
            MouseManager._process_mouse_up(state, event)
        else:
            raise Exception(
                "Unrecognized event for MouseManager: {}".format(str(event))
            )
