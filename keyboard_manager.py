import pygame, copy

from typing import List, Tuple
from state import State
from constants import *
from enum import Enum


def check_hk_pressed(hk: List[int]):
    pressed_keys = pygame.key.get_pressed()
    res = True
    for k in hk:
        if not pressed_keys[k]:
            res = False
            break
    return res


def clear_step(step_data: List[List[int]], ln: int, col: int):
    if step_data[ln][col] == 0:
        pass
    elif step_data[ln][col] == 1:
        step_data[ln][col] = 0
    else:
        s = e = ln
        while step_data[s][col] != 2:
            s -= 1
        while step_data[e][col] != 4:
            e += 1
        for i in range(s, e + 1):
            step_data[i][col] = 0


class KeyBase:

    def __init__(self):
        pass

    def condition(self, state: State, event: pygame.Event) -> bool:
        raise Exception("Condition for KeyBase is Not implemented")

    def action(self, state: State, event: pygame.Event) -> None:
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

    def action(self, state: State, event: pygame.Event) -> None:
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        col = STEP_DATA_OFFSET + KEY_DOUBLE[pygame.key.name(event.key)]
        ln_start = y_to_ln[min(state.y_cur, state.y_base)]
        ln_end = y_to_ln[max(state.y_cur, state.y_base)]

        if ln_start == ln_end:  # Only one line is selected
            step = step_data[ln_start][col]
            if step == 1:
                step_data[ln_start][col] = 0
            else:
                if step != 0:
                    clear_step(ln_start, col)
                step_data[ln_start][col] = 1
        else:  # Many lines are selected
            flag = (step_data[ln_start][col] == 2) and (step_data[ln_end][col] == 4)
            for ln in range(ln_start + 1, ln_end):
                if not flag:
                    break
                flag = flag and (step_data[ln][col] == 3)

            if flag:
                for i in range(ln_start, ln_end + 1):
                    step_data[i][col] = 0
            else:
                clear_step(step_data, ln_start, col)
                clear_step(step_data, ln_end, col)
                step_data[ln_start][col] = 2
                step_data[ln_end][col] = 4
                for i in range(ln_start + 1, ln_end):
                    step_data[i][col] = 3


# Up
class UpKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        return event.type == pygame.KEYDOWN and event.key == pygame.K_UP

    def action(self, state: State, event: pygame.Event) -> None:
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        ln = y_to_ln[state.y_cur]
        pressed_keys = pygame.key.get_pressed()
        if ln != 0:
            block_idx_prev = step_data[ln][STEP_DATA_BI_IDX]
            if pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]:
                bi, mi = (
                    step_data[ln - 1][STEP_DATA_BI_IDX],
                    step_data[ln - 1][STEP_DATA_MS_IDX],
                )

                ln -= 1
                while (
                    ln >= 0
                    and step_data[ln][STEP_DATA_BI_IDX] == bi
                    and step_data[ln][STEP_DATA_MS_IDX] == mi
                ):
                    ln -= 1
                ln += 1
                state.y_cur = ln_to_y[ln]
            else:
                info = block_info[step_data[ln - 1][STEP_DATA_BI_IDX]]
                bm, sb = info[1], info[2]
                dy = min(max((CELL_SIZE * 2) // sb, MIN_SPLIT_SIZE), CELL_SIZE)
                state.y_cur -= dy
                ln -= 1

            block_idx = step_data[ln][STEP_DATA_BI_IDX]
            if block_idx != block_idx_prev:
                state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True

            if not pressed_keys[pygame.K_LSHIFT]:
                state.y_base = state.y_cur

        state.scr_y = min(state.y_cur, state.scr_y)


# Down
class DownKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        return event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN

    def action(self, state: State, event: pygame.Event) -> None:
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()

        ln = y_to_ln[state.y_cur]
        pressed_keys = pygame.key.get_pressed()
        if ln != len(step_data) - 1:
            block_idx_prev = step_data[ln][STEP_DATA_BI_IDX]
            if pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]:
                bi, mi = (
                    step_data[ln + 1][STEP_DATA_BI_IDX],
                    step_data[ln + 1][STEP_DATA_MS_IDX],
                )

                ln += 1
                while (
                    ln <= len(step_data) - 1
                    and step_data[ln][STEP_DATA_BI_IDX] == bi
                    and step_data[ln][STEP_DATA_MS_IDX] == mi
                ):
                    ln += 1
                ln -= 1

                state.y_cur = ln_to_y[ln]
            else:
                info = block_info[step_data[ln][STEP_DATA_BI_IDX]]
                bm, sb = info[1], info[2]
                dy = min(max((CELL_SIZE * 2) // sb, MIN_SPLIT_SIZE), CELL_SIZE)
                state.y_cur += dy
                ln += 1

            if not pressed_keys[pygame.K_LSHIFT]:
                state.y_base = state.y_cur

            block_idx = step_data[ln][STEP_DATA_BI_IDX]
            if block_idx != block_idx_prev:
                state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True

        state.scr_y = max(
            state.y_cur + state.step_size - state.screen_height, state.scr_y
        )


class TabKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        return (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_TAB
            and state.focus_idx != -1
        )

    def action(self, state: State, event: pygame.Event) -> None:
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

    def action(self, state: State, event: pygame.Event) -> None:
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

    def action(self, state: State, event: pygame.Event) -> None:

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
            state.y_base = state.y_cur = state.y_info[state.scr_y][1]


class EnterKey(KeyBase):
    def __init__(self):
        super().__init__()

    def condition(self, state: State, event: pygame.Event) -> bool:
        return event.type == pygame.KEYDOWN and event.key in [
            pygame.K_RETURN,
            pygame.K_KP_ENTER,
        ]

    def action(self, state: State, event: pygame.Event) -> None:
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

    def action(self, state: State, event: pygame.Event) -> None:
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        ln_start = y_to_ln[min(state.y_base, state.y_cur)]
        ln_end = y_to_ln[max(state.y_base, state.y_cur)]
        cols = 5 if state.mode == "Single" else 10
        for i in range(cols):
            clear_step(step_data, ln_start, STEP_DATA_OFFSET + i)
            clear_step(step_data, ln_end, STEP_DATA_OFFSET + i)
        for i in range(ln_start, ln_end + 1):
            for j in range(STEP_DATA_OFFSET, STEP_DATA_OFFSET + cols):
                step_data[i][j] = 0


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

    def action(self, state: State, event: pygame.Event) -> None:
        print("COPY")
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        ln_from, ln_to = (
            y_to_ln[min(state.y_cur, state.y_base)],
            y_to_ln[max(state.y_cur, state.y_base)],
        )

        cols = 5 if state.mode == "Single" else 10

        state.clipboard = copy.deepcopy(step_data[ln_from : ln_to + 1])

        for i in range(cols):
            col = STEP_DATA_OFFSET + i
            ln = 0
            while ln < len(state.clipboard) and state.clipboard[ln][col] in [3, 4]:
                state.clipboard[ln][col] = 0
                ln += 1

            ln = len(state.clipboard) - 1
            while ln >= 0 and state.clipboard[ln][col] in [2, 3]:
                state.clipboard[ln][col] = 0
                ln -= 1


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

    def action(self, state: State, event: pygame.Event) -> None:
        print("CUT")
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        ln_from, ln_to = (
            y_to_ln[min(state.y_cur, state.y_base)],
            y_to_ln[max(state.y_cur, state.y_base)],
        )

        cols = 5 if state.mode == "Single" else 10

        state.clipboard = copy.deepcopy(step_data[ln_from : ln_to + 1])

        for i in range(cols):
            col = STEP_DATA_OFFSET + i
            ln = 0
            while ln < len(state.clipboard) and state.clipboard[ln][col] in [3, 4]:
                state.clipboard[ln][col] = 0
                ln += 1

            ln = len(state.clipboard) - 1
            while ln >= 0 and state.clipboard[ln][col] in [2, 3]:
                state.clipboard[ln][col] = 0
                ln -= 1

        # Erase copied lane
        for i in range(len(state.clipboard)):
            for j in range(cols):
                col = STEP_DATA_OFFSET + j
                if state.clipboard[i][col] != 0 and step_data[ln_from + i][col] != 0:
                    clear_step(step_data, ln_from + i, col)


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

    def action(self, state: State, event: pygame.Event) -> None:
        print("PASTE")
        if state.clipboard is None:
            return

        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()

        clipboard = state.clipboard
        ln_from = y_to_ln[min(state.y_cur, state.y_base)]
        ln_to = ln_from + len(clipboard) - 1

        if ln_to >= len(step_data):
            # Unable to paste steps
            return

        cols = 5 if state.mode == "Single" else 10

        for i in range(len(clipboard)):
            for j in range(cols):
                col = STEP_DATA_OFFSET + j
                if clipboard[i][col] != 0:
                    if step_data[ln_from + i][col] > 1:
                        clear_step(step_data, ln_from + i, col)
                    step_data[ln_from + i][col] = clipboard[i][col]

        # Update y_cur, y_base and scr_y
        state.y_base = ln_to_y[ln_from]
        state.y_cur = ln_to_y[ln_to]
        state.scr_y = max(
            min(state.scr_y, state.y_cur),
            state.y_cur + state.step_size - state.screen_height,
            state.scr_y,
        )


class KeyboardManager:

    def __init__(self):
        self.keys: List[KeyBase] = [
            # Step Chart Keys
            StepChartKey(),
            # Up & Down
            UpKey(),
            DownKey(),
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
        ]

    def process_event(self, state: State, event: pygame.Event):
        for key in self.keys:
            if key.condition(state, event):
                key.action(state, event)
                break
