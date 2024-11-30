import time, copy

from manager.custom_key_logic.base import *
from constants import *
from core import update_validity, get_step_diff


class CopyKey(KeyBase):
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
            and event.key == pygame.K_c
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
        state.clipboard = copy.deepcopy(step_data[ln_from:ln_to])
        for ln in range(ln_from, ln_to):
            for col in range(STEP_DATA_OFFSET, len(step_data[0])):
                if not (col_from <= col < col_to):
                    # ignore unselected lane
                    state.clipboard[ln - ln_from][col] = -1


class CutKey(KeyBase):

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
            and event.key == pygame.K_x
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
        state.clipboard = copy.deepcopy(step_data[ln_from:ln_to])
        step_diff: List[Tuple[int, int, int, int]] = []
        for ln in range(ln_from, ln_to):
            for col in range(STEP_DATA_OFFSET, len(step_data[0])):
                if col_from <= col < col_to:
                    if step_data[ln][col] != 0:
                        step_diff.append((ln, col, step_data[ln][col], 0))
                        step_data[ln][col] = 0
                else:
                    state.clipboard[ln - ln_from][col] = -1

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


class PasteKey(KeyBase):
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
            and event.key == pygame.K_v
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        if state.clipboard is None:
            state.log("(Paste) Nothing in clipboard")
            return

        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        coor_undo = (state.coor_cur, state.coor_base)

        clipboard = state.clipboard
        ln_from, ln_to_remove = (
            min(state.coor_cur[1], state.coor_base[1]),
            max(state.coor_cur[1], state.coor_base[1]) + 1,
        )
        ln_to_paste = min(ln_from + len(clipboard), len(step_data))

        ln_to = max(ln_to_paste, ln_to_remove)

        prev_step_data = copy.deepcopy(step_data[ln_from:ln_to])

        target_cols = []
        for col in range(STEP_DATA_OFFSET, len(step_data[0])):
            if clipboard[0][col] != -1:
                target_cols.append(col)

        col_from, col_to = (
            min(target_cols) - STEP_DATA_OFFSET,
            max(target_cols) - STEP_DATA_OFFSET,
        )

        # Remove
        for ln in range(ln_from, ln_to):
            for col in target_cols:
                step_data[ln][col] = 0

        # Paste
        for ln in range(ln_from, ln_to_paste):
            for col in target_cols:
                step_data[ln][col] = clipboard[ln - ln_from][col]

        update_validity(step_data, ln_from - 1, ln_to + 1)

        # Update coor_cur, y_base and coor_cur
        if state.AUTO_LINE_PASS:
            ln_next = min(ln_to, len(step_data) - 1)
            state.coor_cur = (col_from, ln_next)
            state.coor_base = (col_to, ln_next)
        else:
            state.coor_cur = (col_from, ln_to - 1)
            state.coor_base = (col_to, ln_from)

        coor_redo = (state.coor_cur, state.coor_base)
        state.sync_scr_y()

        step_diff = get_step_diff(
            prev_step_data, state.step_data[ln_from:ln_to], ln_from
        )
        if len(step_diff):
            history_manager.append(
                StepChartChangeDelta(
                    coor_undo,
                    coor_redo,
                    step_diff,
                )
            )


class UndoKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        if state.MUSIC_PLAYING:
            return
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and event.key == pygame.K_z
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        pressed_keys = pygame.key.get_pressed()
        if state.pressed_timestamp[pygame.K_z] == INFINITY:
            state.pressed_timestamp[pygame.K_z] = int(time.time() * 1000)

        if pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
            history_manager.redo(state)
        else:
            history_manager.undo(state)
