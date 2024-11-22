import pygame, copy, time

from typing import List, Tuple
from state import State
from history_manager import HistoryManager, StepChartChangeDelta
from file_manager import save_ucs_file
from utils import get_step_diff, update_validity, clear_step, binary_search
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

        step_diff: List[Tuple[int, int, int, int]] = []

        if ln_from == ln_to - 1:  # Only one line is selected
            if step_data[ln_from][col] == 0:
                step_data[ln_from][col] = 1
                step_diff.append((ln_from, col, 0, 1))
            else:
                step_diff = step_diff + clear_step(step_data, ln_from, ln_to, col)
        else:  # Many lines are selected
            clear = True
            for ln in range(ln_from, ln_to):
                clear &= step_data[ln][col] == 0
                if not clear:
                    break
            if clear:
                # If there are no notes in the column, fill it
                for ln in range(ln_from, ln_to):
                    if ln == ln_from:
                        step_data[ln][col] = 2
                        step_diff.append((ln, col, 0, 2))
                    elif ln < ln_to - 1:
                        step_data[ln][col] = 3
                        step_diff.append((ln, col, 0, 3))
                    else:
                        step_data[ln][col] = 4
                        step_diff.append((ln, col, 0, 4))
            else:
                step_diff = clear_step(step_data, ln_from, ln_to, col)
                for ln in range(ln_from, ln_to):
                    if step_data[ln][col] != 0:
                        step_diff.append((ln, col, step_data[ln][col], 0))
                        step_data[ln][col] = 0

        update_validity(step_data, ln_from - 1, ln_to + 1)

        coor_redo = (state.coor_cur, state.coor_base)

        history_manager.append(StepChartChangeDelta(coor_undo, coor_redo, step_diff))


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

            block_idx = step_data[state.coor_cur[1]][STEP_DATA_BI_IDX]
            if block_idx != block_idx_prev:
                state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True

        if not (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]):
            state.coor_base = state.coor_cur
        state.sync_scr_y()

        # # Useful Debug
        # ln = state.coor_cur[1]
        # print(ln, step_data[ln])


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

        if not (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]):
            state.coor_base = state.coor_cur

        state.sync_scr_y()

        # # Useful Debug
        # ln = state.coor_cur[1]
        # print(ln, step_data[ln])


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
                x = cols - 1
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
                state.focus_idx + 19
            ) % 20  # 20 = Total number of UI elements
            if state.focus_idx == 13 and not state.APPLY_ENABLED:
                state.focus_idx -= 1
        else:
            state.focus_idx = (
                state.focus_idx + 1
            ) % 20  # 20 = Total number of UI elements
            if state.focus_idx == 13 and not state.APPLY_ENABLED:
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

        print(state.clipboard)


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
        if state.clipboard is None:
            print("Nothing in clipboard")
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


# Goto the error line
class FindKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and event.key == pygame.K_f
        )

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        pressed_keys = pygame.key.get_pressed()
        step_data, block_info = state.get_step_info()
        ln, tot_ln = state.coor_cur[1], len(step_data)

        d, ln_condition = (
            (-1, lambda x: x >= 0)
            if (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT])
            else (1, lambda x: x < tot_ln)
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

    def condition(self, state: State, event: pygame.Event) -> bool:
        return event.type == pygame.KEYDOWN and event.key == pygame.K_F5

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        if state.music_len == 0:
            print("MUSIC NOT LOADED")
            return
        if state.MUSIC_PLAYING:
            state.MUSIC_PLAYING = False
            pygame.mixer.music.stop()
        else:
            state.music_start_time = int(time.time() * 1000)
            state.music_start_offset = state.scr_to_time[state.scr_y]
            state.MUSIC_PLAYING = True
            pygame.mixer.music.play(loops=0, start=state.music_start_offset / 1000)


class SaveKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and event.key == pygame.K_s
        )

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        save_ucs_file(state)


class LoadKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and event.key == pygame.K_l
        )

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        state.focus_idx = 2  # Focus to Load button
        state.EMIT_BUTTON_PRESS = True


class StepSizeKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        pressed_keys = pygame.key.get_pressed()
        return (
            event.type == pygame.KEYDOWN
            and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL])
            and event.key in [pygame.K_EQUALS, pygame.K_MINUS]
        )

    def action(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ) -> None:
        print("hi", str(event))
        if event.key == pygame.K_EQUALS and state.step_size_idx != 2:
            print("Adjust to larger")
            state.step_size_idx += 1
            state.update_x_info()
            state.update_y_info()
        elif event.key == pygame.K_MINUS and state.step_size_idx != 0:
            print("Adjust to smaller")
            state.step_size_idx -= 1
            state.update_x_info()
            state.update_y_info()


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
            # Find Error
            FindKey(),
            # Music Play/Stop
            MusicKey(),
            # Save, Load
            SaveKey(),
            LoadKey(),
            # Step Size Adjust
            StepSizeKey(),
        ]

    def process_event(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ):
        for key in self.keys:
            if key.condition(state, event):
                key.action(history_manager, state, event)
                break
