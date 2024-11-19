import pygame, copy

from typing import List, Tuple
from state import State
from history_manager import HistoryManager, StepChartChangeDelta
from utils import get_step_diff, update_validity
from constants import *


class KeyBase:

    def __init__(self):
        pass

    def condition(self, state: State, event: pygame.Event) -> bool:
        raise Exception("Condition for KeyBase is Not implemented")

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        raise Exception("Action for KeyBase is not implemented")


# Step Chart
class StepChartKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        key_name = pygame.key.name(event.key)
        return not (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL]) and (
            (state.mode == "Single" and key_name in KEY_SINGLE)
            or (state.mode == "Double" and key_name in KEY_DOUBLE)
        )

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        step_data, block_info = state.get_step_info()
        coor_undo = (state.coor_cur, state.coor_base)
        col = STEP_DATA_OFFSET + KEY_DOUBLE[pygame.key.name(event.key)]
        ln_from, ln_to = (
            min(state.coor_cur[1], state.coor_base[1]),
            max(state.coor_cur[1], state.coor_base[1]) + 1,
        )

        prev_step_data = copy.deepcopy(step_data[ln_from:ln_to])

        if ln_from == ln_to - 1:  # Only one line is selected
            step_data[ln_from][col] = 1 - step_data[ln_from][col]
        else:  # Many lines are selected
            flag = True
            for ln in range(ln_from, ln_to):
                if ln == ln_from:
                    flag = flag and step_data[ln][col] == 2
                elif ln < ln_to - 1:
                    flag = flag and step_data[ln][col] == 3
                else:
                    flag = flag and step_data[ln][col] == 4
                if not flag:
                    break

            if flag:
                # If already there are exact long note in the lane
                for i in range(ln_from, ln_to):
                    step_data[i][col] = 0
            else:
                step_data[ln_from][col] = 2
                step_data[ln_to - 1][col] = 4
                for i in range(ln_from + 1, ln_to - 1):
                    step_data[i][col] = 3
        update_validity(step_data, ln_from - 1, ln_to + 1, col)

        coor_redo = (state.coor_cur, state.coor_base)

        history_manager.append(
            StepChartChangeDelta(
                coor_undo,
                coor_redo,
                get_step_diff(prev_step_data, step_data[ln_from:ln_to], ln_from),
            )
        )


# Up
class UpKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        return event.type == pygame.KEYDOWN and event.key == pygame.K_UP

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
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

            if not (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]):
                state.coor_base = state.coor_cur

            block_idx = step_data[state.coor_cur[1]][STEP_DATA_BI_IDX]
            if block_idx != block_idx_prev:
                state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True
        print(state.coor_cur[1], step_data[state.coor_cur[1]])
        state.sync_scr_y()


# Down
class DownKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        return event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        step_data, block_info = state.get_step_info()

        ln = state.coor_cur[1]
        pressed_keys = pygame.key.get_pressed()
        if ln != len(step_data) - 1:
            block_idx_prev = step_data[ln][STEP_DATA_BI_IDX]
            if pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]:
                line = step_data[ln]
                block = block_info[line[STEP_DATA_BI_IDX]]
                ln -= line[STEP_DATA_BT_IDX] * block[2] + line[STEP_DATA_SP_IDX]
                ln += block[1] * block[2]
                state.coor_cur = (state.coor_cur[0], ln)
            else:
                state.coor_cur = (state.coor_cur[0], ln + 1)

            if not (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]):
                state.coor_base = state.coor_cur

            block_idx = step_data[state.coor_cur[1]][STEP_DATA_BI_IDX]
            if block_idx != block_idx_prev:
                state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True

        print(state.coor_cur[1], step_data[state.coor_cur[1]])
        state.sync_scr_y()


# Left
class LeftKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        return event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:

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

    def condition(self, state: State, event: pygame.Event) -> bool:
        return event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:

        x = state.coor_cur[0]
        cols = state.get_cols()
        pressed_keys = pygame.key.get_pressed()
        if x != cols - 1:
            if pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]:
                x = cols
            else:
                x += 1
            state.coor_cur = (x, state.coor_cur[1])
            if not (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]):
                state.coor_base = state.coor_cur


class TabKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        return (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_TAB
            and state.focus_idx != -1
        )

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        pressed_keys = pygame.key.get_pressed()
        state.focus_idx_prev = state.focus_idx
        if pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
            state.focus_idx_prev = state.focus_idx
            state.focus_idx = (
                state.focus_idx + 18
            ) % 19  # 19 = Total number of UI elements
            if state.focus_idx == 12 and not state.APPLY_ENABLED:
                state.focus_idx -= 1
        else:
            state.focus_idx = (
                state.focus_idx + 1
            ) % 19  # 19 = Total number of UI elements
            if state.focus_idx == 12 and not state.APPLY_ENABLED:
                state.focus_idx += 1


class EscKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        return (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
            and state.focus_idx != -1
        )

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        state.focus_idx_prev = state.focus_idx
        state.focus_idx = -1


# Area Key 1, 2, 3, 4
class AreaKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            pressed_keys[pygame.K_LCTRL]
            and event.type == pygame.KEYDOWN
            and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
        )

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:

        state.focus_idx_prev = state.focus_idx
        if event.key == pygame.K_1:
            # Update focus to Play button
            state.focus_idx = 0
        elif event.key == pygame.K_2:
            # Update focus to BPM textbox in Block Information area
            state.focus_idx = 5
        elif event.key == pygame.K_3:
            # Update focus to "Add ^" button in Block Operation area
            state.focus_idx = 13
        elif event.key == pygame.K_4:
            # Update selection square at top square in current scr_y
            state.coor_base = (0, state.y_to_ln[state.scr_y])
            state.coor_cur = (state.get_cols(), state.y_to_ln[state.scr_y])
            state.sync_scr_y()


class EnterKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        return event.type == pygame.KEYDOWN and event.key in [
            pygame.K_RETURN,
            pygame.K_KP_ENTER,
        ]

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        print("hello")
        state.EMIT_BUTTON_PRESS = True


class BackspaceKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        return (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_BACKSPACE
            and state.focus_idx == -1
        )

    # TODO : Implement action for ctrl + BACKSPACE
    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
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

        prev_step_data = copy.deepcopy(step_data[ln_from:ln_to])

        for ln in range(ln_from, ln_to):
            for col in range(col_from, col_to):
                step_data[ln][col] = 0
        update_validity(step_data, ln_from - 1, ln_to + 1)

        y_undo = y_redo = (state.coor_cur, state.coor_base)
        history_manager.append(
            StepChartChangeDelta(
                y_undo,
                y_redo,
                get_step_diff(prev_step_data, step_data[ln_from:ln_to], ln_from),
            )
        )


class CopyKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and event.key == pygame.K_c
        )

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        print("COPY")
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

    def condition(self, state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and event.key == pygame.K_x
        )

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        print("CUT")
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
                    state.clipboard[ln][col] = -1

        update_validity(step_data, ln_from, ln_to)


class PasteKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and event.key == pygame.K_v
        )

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        print("PASTE")
        if state.clipboard is None:
            print("Nothing in clipboard")
            return

        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()

        clipboard = state.clipboard
        ln_from, ln_to = (
            min(state.coor_cur[1], state.coor_base[1]),
            max(state.coor_cur[1], state.coor_base[1], len(step_data) - 1) + 1,
        )
        col_from, col_to = (
            min(state.coor_cur[0], state.coor_base[0]) + STEP_DATA_OFFSET,
            max(state.coor_cur[0], state.coor_base[0]) + STEP_DATA_OFFSET + 1,
        )
        target_cols = []
        for col in range(STEP_DATA_OFFSET, len(step_data[0])):
            if clipboard[0][col] != -1:
                target_cols.append(col)

        # Remove
        for ln in range(ln_from, ln_to):
            for col in target_cols:
                step_data[ln][col] = 0

        # Paste
        ln_to = min(ln_from + len(clipboard), len(step_data))
        for ln in range(ln_from, ln_to):
            for col in target_cols:
                step_data[ln][col] = clipboard[ln - ln_from][col]

        # Update coor_cur, y_base and coor_cur
        state.coor_cur = (state.coor_cur[0], ln_to)
        state.coor_base = (state.coor_base[0], ln_from)
        state.sync_scr_y()


class UndoKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and not (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT])
            and event.key == pygame.K_z
        )

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        history_manager.undo(state)


class RedoKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT])
            and event.key == pygame.K_z
        )

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        history_manager.redo(state)


# TODO: Implemente below
class FindKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, history_manager: HistoryManager
    ) -> None:
        return super().action(state, event, history_manager)


class KeyboardManager:

    def __init__(self):
        self.keys: List[KeyBase] = [
            # Step Chart Keys
            StepChartKey(),
            # Up & Down
            UpKey(),
            DownKey(),
            RightKey(),
            LeftKey(),
            # Tab
            TabKey(),
            # Esc
            EscKey(),
            # Ctrl + (1, 2, 3, 4) -> Key for Focusing Each Area
            AreaKey(),
            # Backspace
            BackspaceKey(),
            # Enter
            EnterKey(),
            # Copy, Cut, Paste
            CopyKey(),
            CutKey(),
            PasteKey(),
            # Undo, Redo
            UndoKey(),
            RedoKey(),
        ]

    def process_event(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ):
        for key in self.keys:
            if key.condition(state, event):
                key.action(history_manager, state, event)
                break
