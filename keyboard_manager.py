import pygame, copy, time

from ui_elements import (
    PlayButton,
    SaveButton,
    SaveAsButton,
    LoadButton,
    LoadMP3Button,
    AutoLinePassButton,
    ElementBase,
    BlockAddAboveButton,
    BlockAddBelowButton,
    BlockSplitButton,
    BlockDeleteButton,
)
from typing import List, Tuple
from state import State
from history_manager import HistoryManager, StepChartChangeDelta
from file_manager import save_ucs_file
from utils import get_step_diff, update_validity, clear_step, binary_search
from constants import *


class KeyBase:

    def __init__(self):
        pass

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        raise Exception("Condition for KeyBase is Not implemented")

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        raise Exception("Action for KeyBase is not implemented")


# Step Chart
class StepChartKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and not (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and (
                (state.mode == "Single" and event.key in KEY_SINGLE)
                or (state.mode == "Double" and event.key in KEY_DOUBLE)
            )
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        step_data, block_info = state.get_step_info()
        coor_undo = (state.coor_cur, state.coor_base)
        col = STEP_DATA_OFFSET + KEY_DOUBLE[event.key]
        ln_from, ln_to = (
            min(state.coor_cur[1], state.coor_base[1]),
            max(state.coor_cur[1], state.coor_base[1]) + 1,
        )

        step_diff: List[Tuple[int, int, int, int]] = []

        if ln_from == ln_to - 1:  # Only one line is selected
            if step_data[ln_from][col] == 1:
                return
            if step_data[ln_from][col] == 0:
                step_data[ln_from][col] = 1
            else:
                v = step_data[ln_from][col]
                step_diff = list(
                    filter(
                        lambda x: x[0] != ln_from,
                        clear_step(step_data, ln_from, ln_to, col),
                    )
                ) + [(ln_from, col, v, 1)]

                step_data[ln_from][col] = 1

        else:  # Many lines are selected
            done = True
            for ln in range(ln_from, ln_to):
                v = step_data[ln][col]
                if ln == ln_from and v != 2:
                    done = False
                    step_diff.append((ln, col, v, 2))
                elif ln < ln_to - 1 and v != 3:
                    done = False
                    step_diff.append((ln, col, v, 3))
                elif ln == ln_to - 1 and v != 4:
                    done = False
                    step_diff.append((ln, col, v, 4))
            if done:
                return
            if not done:
                step_diff = step_diff + list(
                    filter(
                        lambda x: not (ln_from <= x[0] < ln_to),
                        clear_step(step_data, ln_from, ln_to, col),
                    )
                )
                for ln in range(ln_from, ln_to):
                    if ln == ln_from:
                        step_data[ln][col] = 2
                    elif ln < ln_to - 1:
                        step_data[ln][col] = 3
                    else:
                        step_data[ln][col] = 4

        update_validity(step_data, ln_from - 1, ln_to + 1)

        coor_redo = (state.coor_cur, state.coor_base)

        history_manager.append(StepChartChangeDelta(coor_undo, coor_redo, step_diff))


# Up
class UpKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        return event.type == pygame.KEYDOWN and event.key == pygame.K_UP

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:

        if state.pressed_timestamp[pygame.K_UP] == INFINITY:
            state.pressed_timestamp[pygame.K_UP] = int(time.time() * 1000)

        step_data, block_info = state.get_step_info()
        ln = state.coor_cur[1]
        pressed_keys = pygame.key.get_pressed()
        if ln != 0:
            ln -= 1
            block_idx_prev = step_data[ln][STEP_DATA_BI_IDX]
            if pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]:
                line = step_data[ln]
                block = block_info[line[STEP_DATA_BI_IDX]]
                ln -= line[STEP_DATA_BT_IDX] * block[2] + line[STEP_DATA_SP_IDX]
                state.coor_cur = (state.coor_cur[0], ln)
            else:
                state.coor_cur = (state.coor_cur[0], ln)

            block_idx = step_data[state.coor_cur[1]][STEP_DATA_BI_IDX]
            if block_idx != block_idx_prev:
                state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True

        if state.AUTO_LINE_PASS:
            state.coor_base = (state.coor_base[0], state.coor_cur[1])
        elif not (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]):
            state.coor_base = state.coor_cur
        state.sync_scr_y()

        # # Useful Debug
        # ln = state.coor_cur[1]
        # print(ln, step_data[ln])


# Down
class DownKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        return event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:

        if state.pressed_timestamp[pygame.K_DOWN] == INFINITY:
            state.pressed_timestamp[pygame.K_DOWN] = int(time.time() * 1000)

        step_data, block_info = state.get_step_info()
        block_idx_prev = None
        ln = state.coor_cur[1]
        pressed_keys = pygame.key.get_pressed()
        if ln != len(step_data) - 1:
            block_idx_prev = step_data[ln][STEP_DATA_BI_IDX]
            if pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]:
                line = step_data[ln]
                block = block_info[line[STEP_DATA_BI_IDX]]
                ln -= line[STEP_DATA_BT_IDX] * block[2] + line[STEP_DATA_SP_IDX]

                ln += block[1] * block[2]
                ln = min(ln, len(step_data) - 1)
                state.coor_cur = (state.coor_cur[0], ln)
            else:
                state.coor_cur = (state.coor_cur[0], ln + 1)

            block_idx = step_data[state.coor_cur[1]][STEP_DATA_BI_IDX]
            if block_idx != block_idx_prev:
                state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True

        if state.AUTO_LINE_PASS:
            state.coor_base = (state.coor_base[0], state.coor_cur[1])
        elif not (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]):
            state.coor_base = state.coor_cur

        state.sync_scr_y()

        # # Useful Debug
        # ln = state.coor_cur[1]
        # print(ln, step_data[ln])


# Left
class LeftKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        return (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_LEFT
            and not (BI_BPM_TEXTBOX <= state.focus_idx <= BI_SP_TEXTBOX)
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        if state.AUTO_LINE_PASS:
            return
        x = state.coor_cur[0]
        pressed_keys = pygame.key.get_pressed()
        if x != 0:
            if pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]:
                x = 0
            else:
                x -= 1
            state.coor_cur = (x, state.coor_cur[1])
            if not (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]):
                state.coor_base = state.coor_cur


# Right
class RightKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        return (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_RIGHT
            and not (BI_BPM_TEXTBOX <= state.focus_idx <= BI_SP_TEXTBOX)
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        if state.AUTO_LINE_PASS:
            return
        x = state.coor_cur[0]
        cols = state.get_cols()
        pressed_keys = pygame.key.get_pressed()
        if x != cols - 1:
            if pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]:
                x = cols - 1
            else:
                x += 1
            state.coor_cur = (x, state.coor_cur[1])
            if not (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]):
                state.coor_base = state.coor_cur


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

        y_undo = y_redo = (state.coor_cur, state.coor_base)
        history_manager.append(StepChartChangeDelta(y_undo, y_redo, step_diff))


class CopyKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
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
        if state.MUSIC_PLAYING:
            state.log("(Error) Cannot copy while music playing")
            return
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
        if state.MUSIC_PLAYING:
            state.log("(Error) Cannot cut while music playing")
            return
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
                if col_from <= col < col_to:
                    step_data[ln][col] = 0
                else:
                    state.clipboard[ln - ln_from][col] = -1

        update_validity(step_data, ln_from - 1, ln_to + 1)


class PasteKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
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
        if state.MUSIC_PLAYING:
            state.log("(Error) Cannot copy while music playing")
            return
        elif state.clipboard is None:
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
        for ln in range(ln_from, ln_to):
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
        if state.MUSIC_PLAYING:
            state.log("(Error) Cannot undo/redo while music playing")
            return
        pressed_keys = pygame.key.get_pressed()
        if state.pressed_timestamp[pygame.K_z] == INFINITY:
            state.pressed_timestamp[pygame.K_z] = int(time.time() * 1000)

        if pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
            history_manager.redo(state)
        else:
            history_manager.undo(state)


# Goto the error line
class FindKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
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
        if state.MUSIC_PLAYING:
            state.log("(Error) Cannot find error while music playing")
            return
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


class SaveKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and event.key == pygame.K_s
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
            SaveAsButton.action(history_manager, state, event, ui_elements)
        else:
            SaveButton.action(history_manager, state, event, ui_elements)


class LoadKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and event.key == pygame.K_l
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
            LoadMP3Button.action(history_manager, state, event, ui_elements)
        else:
            LoadButton.action(history_manager, state, event, ui_elements)


class SelectAllKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
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
        if state.MUSIC_PLAYING:
            return
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


class StepKeyUp(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        if not (event.type == pygame.KEYUP and state.AUTO_LINE_PASS):
            return False

        target_keys = list(
            (KEY_SINGLE if state.mode == "Single" else KEY_DOUBLE).keys()
        )
        if not event.key in target_keys:
            return False

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL]:
            return False
        all_step_key_released = (
            sum(list(map(lambda x: pressed_keys[x], target_keys))) == 0
        )
        return all_step_key_released

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        if state.AUTO_LINE_PASS:
            ln = state.coor_cur[1]
            ln_next = min(ln + 1, len(state.step_data) - 1)
            state.coor_base = (0, ln_next)
            state.coor_cur = (state.get_cols() - 1, ln_next)
            state.sync_scr_y()


class BlockOperationKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and event.key in [pygame.K_u, pygame.K_i, pygame.K_o, pygame.K_p]
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        if state.MUSIC_PLAYING:
            state.log("(Error) Cannot operate while music playing")
            return
        if event.key == pygame.K_u:
            BlockAddAboveButton.action(history_manager, state, event, ui_elements)
        elif event.key == pygame.K_i:
            BlockAddBelowButton.action(history_manager, state, event, ui_elements)
        elif event.key == pygame.K_o:
            BlockSplitButton.action(history_manager, state, event, ui_elements)
        elif event.key == pygame.K_p:
            BlockDeleteButton.action(history_manager, state, event, ui_elements)


class HoldKeyUp(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYUP and event.key in state.pressed_timestamp.keys()
        )

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ) -> None:
        if event.key == pygame.K_z:
            state.pressed_timestamp[pygame.K_z] = INFINITY
        elif event.key == pygame.K_UP:
            state.pressed_timestamp[pygame.K_UP] = INFINITY
        elif event.key == pygame.K_DOWN:
            state.pressed_timestamp[pygame.K_DOWN] = INFINITY


class KeyboardManager:

    def __init__(self):
        self.keys: List[KeyBase] = [
            # Step Chart Keys
            StepChartKey,
            # Up & Down
            UpKey,
            DownKey,
            RightKey,
            LeftKey,
            # Tab
            TabKey,
            # Esc
            EscKey,
            # Ctrl + (1, 2, 3, 4) -> Key for Focusing Each Area
            AreaKey,
            # Backspace
            BackspaceKey,
            # Enter
            EnterKey,
            # Copy, Cut, Paste
            CopyKey,
            CutKey,
            PasteKey,
            # Undo, Redo
            UndoKey,
            # Select All
            SelectAllKey,
            # Find Error
            FindKey,
            # Music Play/Stop
            MusicKey,
            # Save, Load
            SaveKey,
            LoadKey,
            # Step Size Adjust
            StepSizeKey,
            # Step Key Up
            StepKeyUp,
            # Mode Shortcut
            AutoPassModeKey,
            # Block Operation Shortcut
            BlockOperationKey,
            # Hold Key Up Dection
            HoldKeyUp,
        ]

    def process_event(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        for key in self.keys:
            if key.condition(state, event):
                key.action(history_manager, state, event, ui_elements)
                break
