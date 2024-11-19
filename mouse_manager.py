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

            state.coor_cur = (
                (mouse_x - state.step_x_start) // state.step_size,
                state.y_to_ln[mouse_y + state.scr_y],
            )

            if not pressed_keys[pygame.K_LSHIFT]:
                state.coor_base = state.coor_cur
            state.sync_scr_y()

        elif state.measure_x_start <= mouse_x < state.scrollbar_x_start:
            state.LATTICE_CLICKED, state.SCROLLBAR_CLICKED = False, False
            state.focus_idx = -1

            y_to_ln, ln_to_y = state.get_y_info()

            ln_from, ln_to = state.get_measure_range_by_y(mouse_y + state.scr_y)
            state.coor_base = (0, ln_from)
            state.coor_cur = (state.get_cols() - 1, ln_to - 1)
            state.sync_scr_y()

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
