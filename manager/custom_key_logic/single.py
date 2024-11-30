import time, copy

from manager.custom_key_logic.base import *
from constants import *
from core import clear_step, update_validity, get_note_range


class TabKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        return (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_TAB
            and state.focus_idx != -1
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        pressed_keys = pygame.key.get_pressed()
        fi = state.focus_idx_prev = state.focus_idx
        sub_panel = ui_elements[FILE_LOAD_BUTTON].e.ui_container
        if pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
            d = TOTAL_UI_ELEMENTS - 1
        else:
            d = 1
        while True:
            fi = (fi + d) % TOTAL_UI_ELEMENTS
            element = ui_elements[fi].e
            if element.visible and element.is_enabled:
                break
        state.focus_idx = fi


class EscKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        return (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
            and state.focus_idx != -1
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        state.focus_idx_prev = state.focus_idx
        state.focus_idx = -1


# Area Key 1, 2, 3, 4
class AreaKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and pressed_keys[pygame.K_LCTRL]
            and event.key
            in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        state.focus_idx_prev = state.focus_idx
        if event.key == pygame.K_1:
            # Update focus to Play button
            state.focus_idx = FILE_BUTTON
        elif event.key == pygame.K_2:
            # Update focus to BPM textbox in Block Information area
            state.focus_idx = BI_BPM_TEXTBOX
        elif event.key == pygame.K_3:
            # Update focus to "Add ^" button in Block Operation area
            state.focus_idx = BO_BLOCK_ADD_A_BUTTON
        elif event.key == pygame.K_4:
            # Update focus to "Add ^" button in Block Operation area
            state.focus_idx = AUTO_LINE_PASS_BUTTON
        elif event.key == pygame.K_5:
            # Update focus to "Add ^" button in Block Operation area
            state.focus_idx = LOG_CLEAR_BUTTON


class EnterKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        return event.type == pygame.KEYDOWN and event.key in [
            pygame.K_RETURN,
            pygame.K_KP_ENTER,
        ]

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        state.EMIT_BUTTON_PRESS = True


class BackspaceKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        if state.MUSIC_PLAYING:
            return False
        return (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_BACKSPACE
            and not (BI_BPM_TEXTBOX <= state.focus_idx < BI_APPLY_BUTTON)
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        step_data, block_info = state.get_step_info()
        ln_from, ln_to = (
            min(state.coor_cur[1], state.coor_base[1]),
            max(state.coor_cur[1], state.coor_base[1]) + 1,
        )
        col_from, col_to = (
            min(state.coor_cur[0], state.coor_base[0]) + STEP_DATA_OFFSET,
            max(state.coor_cur[0], state.coor_base[0]) + STEP_DATA_OFFSET + 1,
        )
        cols = state.get_cols()

        step_diff: List[Tuple[int, int, int, int]] = []

        for col in range(col_from, col_to):
            step_diff = step_diff + clear_step(step_data, ln_from, ln_to, col)
            for ln in range(ln_from, ln_to):
                if step_data[ln][col] != 0:
                    step_diff.append((ln, col, step_data[ln][col], 0))
                    step_data[ln][col] = 0

        update_validity(step_data, ln_from - 1, ln_to + 1)

        coor_undo = coor_redo = (state.coor_cur, state.coor_base)

        if len(step_diff):
            history_manager.append(
                StepChartChangeDelta(
                    coor_undo,
                    coor_redo,
                    step_diff,
                )
            )
