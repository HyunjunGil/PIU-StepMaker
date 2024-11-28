from manager.custom_key_logic.base import *

from constants import *
from core import update_validity
from gui import PlayButton, AutoLinePassButton


# Goto the error line
class FindKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        if state.MUSIC_PLAYING:
            return False

        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and event.key == pygame.K_f
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:

        pressed_keys = pygame.key.get_pressed()
        step_data, block_info = state.get_step_info()

        error_cnt = update_validity(step_data, 0, len(step_data))
        if error_cnt == 0:
            state.log("No error line found")
            return

        state.log(f"{error_cnt} error lines found")

        ln, tot_ln = state.coor_cur[1], len(step_data)

        d = (
            -1
            if (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT])
            else 1
        )
        if step_data[ln][STEP_DATA_VD_IDX] != 0:
            ln = 0

        for i in range(1, tot_ln + 1):
            ln = (ln + d + tot_ln) % tot_ln
            if step_data[ln][STEP_DATA_VD_IDX] == 0:
                state.coor_base = (0, ln)
                state.coor_cur = (state.get_cols() - 1, ln)
                state.sync_scr_y()
                return


class MusicKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        return event.type == pygame.KEYDOWN and event.key == pygame.K_F5

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        PlayButton.action(history_manager, state, event, [])


class SelectAllKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        if state.MUSIC_PLAYING or BI_BPM_TEXTBOX <= state.focus_idx < BI_APPLY_BUTTON:
            return False
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and event.key == pygame.K_a
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        step_data, block_info = state.get_step_info()
        x_base, ln_base = state.coor_base
        x_cur, ln_cur = state.coor_cur
        bi_from = step_data[ln_base][STEP_DATA_BI_IDX]
        bi_to = step_data[ln_cur][STEP_DATA_BI_IDX]
        ln_ff, _ = state.get_block_range_by_block_idx(bi_from)
        _, ln_tt = state.get_block_range_by_block_idx(bi_to)
        cols = state.get_cols()
        if state.coor_base == (0, ln_ff) and state.coor_cur == (cols - 1, ln_tt - 1):
            state.coor_base = (0, 0)
            state.coor_cur = (cols - 1, len(step_data) - 1)
        else:
            state.coor_base = (0, ln_ff)
            state.coor_cur = (cols - 1, ln_tt - 1)

        state.sync_scr_y()


class StepSizeKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and event.key
            in [pygame.K_EQUALS, pygame.K_MINUS, pygame.K_COMMA, pygame.K_PERIOD]
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        if event.key == pygame.K_COMMA and state.step_size_idx != 0:
            # Step size down
            state.step_size_idx -= 1
            state.update_x_info()
            state.update_y_info()
            state.update_scr_to_time()
            state.sync_scr_y()
        elif event.key == pygame.K_PERIOD and state.step_size_idx != 2:
            # Step size up
            state.step_size_idx += 1
            if not state.is_valid_step_info(state.step_data, state.block_info)[0]:
                state.log(
                    "(Error) Cannot increase step size. Maximum scrollable height reached"
                )
                state.step_size_idx -= 1
                return
            state.update_x_info()
            state.update_y_info()
            state.update_scr_to_time()
            state.sync_scr_y()
        elif event.key == pygame.K_MINUS and state.step_vertical_mp != 10:
            # Step height down
            state.step_vertical_mp -= 1
            state.update_y_info()
            state.update_scr_to_time()
            state.sync_scr_y()
        elif (
            event.key == pygame.K_EQUALS
            and state.step_vertical_mp != VERTICAL_MULTIPLIER_MAX
        ):
            # Step height up
            state.step_vertical_mp += 1
            if not state.is_valid_step_info(state.step_data, state.block_info)[0]:
                state.log(
                    "(Error) Cannot increase step height. Maximum scrollable height reached"
                )
                state.step_vertical_mp -= 1
                return
            state.update_y_info()
            state.update_scr_to_time()
            state.sync_scr_y()


class AutoPassModeKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        return event.type == pygame.KEYDOWN and event.key == pygame.K_F1

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        return AutoLinePassButton.action(history_manager, state, event, ui_elements)
