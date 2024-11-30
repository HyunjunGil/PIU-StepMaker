import time, copy

from manager.custom_key_logic.base import *
from constants import *
from core import get_note_range


# Up
class UpKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        if state.MUSIC_PLAYING:
            return False
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
        x, ln = state.coor_cur
        pressed_keys = pygame.key.get_pressed()
        ctrl_pressed = pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL]
        if (
            ln != 0
            and step_data[ln][x + STEP_DATA_OFFSET] != 0
            and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT])
        ) and state.coor_cur == state.coor_base:
            step_diff: List[Tuple[int, int, int, int]] = []
            coor_undo = (state.coor_cur, state.coor_base)
            col = x + STEP_DATA_OFFSET
            ln_init, v_init = ln, step_data[ln][col]
            bi, mi = (
                step_data[ln_init - 1][STEP_DATA_BI_IDX],
                step_data[ln_init - 1][STEP_DATA_MS_IDX],
            )

            if v_init == 1 and step_data[ln - 1][col] == 0:
                # Move short note
                ln -= 1
                if ctrl_pressed:
                    while (
                        ln - 1 >= 0
                        and step_data[ln - 1][col] == 0
                        and step_data[ln - 1][STEP_DATA_BI_IDX] == bi
                        and step_data[ln - 1][STEP_DATA_MS_IDX] == mi
                    ):
                        ln -= 1
                step_data[ln_init][col] = 0
                step_data[ln][col] = 1
                step_diff.append((ln_init, col, 1, 0))
                step_diff.append((ln, col, 0, 1))
                state.coor_base = state.coor_cur = (x, ln)
                coor_redo = ((x, ln), (x, ln))
                history_manager.append(
                    StepChartChangeDelta(coor_undo, coor_redo, step_diff)
                )
            elif v_init == 2 and step_data[ln - 1][col] == 0:
                # Move head of long note
                step_diff.append((ln, col, 2, 3))
                step_data[ln][col] = 3
                ln -= 1
                if ctrl_pressed:
                    while (
                        ln - 1 >= 0
                        and step_data[ln - 1][col] == 0
                        and step_data[ln - 1][STEP_DATA_BI_IDX] == bi
                        and step_data[ln - 1][STEP_DATA_MS_IDX] == mi
                    ):
                        step_diff.append((ln, col, 0, 3))
                        step_data[ln][col] = 3
                        ln -= 1
                step_diff.append((ln, col, 0, 2))
                step_data[ln][col] = 2
                state.coor_base = state.coor_cur = (x, ln)
                coor_redo = ((x, ln), (x, ln))
                history_manager.append(
                    StepChartChangeDelta(coor_undo, coor_redo, step_diff)
                )
            elif v_init == 3:
                # Move entire long note
                note_from, note_to = get_note_range(step_data, ln, col)
                if note_from - 1 < 0 or step_data[note_from - 1][col] != 0:
                    return
                bi, mi = (
                    step_data[note_from - 1][STEP_DATA_BI_IDX],
                    step_data[note_from - 1][STEP_DATA_MS_IDX],
                )
                ln = note_from

                ln -= 1
                if ctrl_pressed:
                    while (
                        ln - 1 >= 0
                        and step_data[ln - 1][col] == 0
                        and step_data[ln - 1][STEP_DATA_BI_IDX] == bi
                        and step_data[ln - 1][STEP_DATA_MS_IDX] == mi
                    ):
                        ln -= 1
                prev_step_data = copy.deepcopy(step_data[ln : note_to + 1])
                offset = note_from - ln
                for l in range(ln, note_to + 1):
                    if l < ln + (note_to - note_from + 1):
                        step_data[l][col] = step_data[l + offset][col]
                    else:
                        step_data[l][col] = 0

                    if prev_step_data[l - ln][col] != step_data[l][col]:
                        step_diff.append(
                            (
                                l,
                                col,
                                prev_step_data[l + offset - note_from][col],
                                step_data[l][col],
                            )
                        )
                state.coor_base = state.coor_cur = (x, ln_init - offset)
                coor_redo = (state.coor_cur, state.coor_base)
                history_manager.append(
                    StepChartChangeDelta(coor_undo, coor_redo, step_diff)
                )
            elif v_init == 4 and step_data[ln - 1][col] == 3:
                # Adjust tail of long note
                step_diff.append((ln, col, 4, 0))
                step_data[ln][col] = 0
                ln -= 1
                if ctrl_pressed:
                    while (
                        ln - 1 >= 0
                        and step_data[ln - 1][col] == 3
                        and step_data[ln - 1][STEP_DATA_BI_IDX] == bi
                        and step_data[ln - 1][STEP_DATA_MS_IDX] == mi
                    ):
                        step_diff.append((ln, col, 3, 0))
                        step_data[ln][col] = 0
                        ln -= 1
                step_diff.append((ln, col, 3, 4))
                step_data[ln][col] = 4
                state.coor_base = state.coor_cur = (x, ln)
                coor_redo = ((x, ln), (x, ln))
                history_manager.append(
                    StepChartChangeDelta(coor_undo, coor_redo, step_diff)
                )

        elif ln != 0:
            ln -= 1
            bi, mi = (
                step_data[ln][STEP_DATA_BI_IDX],
                step_data[ln][STEP_DATA_MS_IDX],
            )
            if ctrl_pressed:
                while (
                    ln - 1 >= 0
                    and step_data[ln - 1][STEP_DATA_BI_IDX] == bi
                    and step_data[ln - 1][STEP_DATA_MS_IDX] == mi
                ):
                    ln -= 1
            state.coor_cur = (state.coor_cur[0], ln)

            block_idx = step_data[state.coor_cur[1]][STEP_DATA_BI_IDX]
            if block_idx != bi:
                state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True

            if state.AUTO_LINE_PASS:
                state.coor_base = (state.coor_base[0], state.coor_cur[1])
            elif not (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]):
                state.coor_base = state.coor_cur

        else:
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

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        if state.MUSIC_PLAYING:
            return False
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
        x, ln = state.coor_cur
        ln_max = len(step_data) - 1
        pressed_keys = pygame.key.get_pressed()
        ctrl_pressed = pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL]
        if (
            ln != ln_max
            and step_data[ln][x + STEP_DATA_OFFSET] != 0
            and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT])
        ) and state.coor_cur == state.coor_base:
            step_diff: List[Tuple[int, int, int, int]] = []
            coor_undo = (state.coor_cur, state.coor_base)
            col = x + STEP_DATA_OFFSET
            ln_init, v_init = ln, step_data[ln][col]
            bi, mi = (
                step_data[ln_init + 1][STEP_DATA_BI_IDX],
                step_data[ln_init + 1][STEP_DATA_MS_IDX],
            )

            if v_init == 1 and step_data[ln + 1][col] == 0:
                # Move short note
                ln += 1
                if ctrl_pressed:
                    while (
                        ln + 1 <= ln_max
                        and step_data[ln + 1][col] == 0
                        and step_data[ln + 1][STEP_DATA_BI_IDX] == bi
                        and step_data[ln + 1][STEP_DATA_MS_IDX] == mi
                    ):
                        ln += 1
                step_data[ln_init][col] = 0
                step_data[ln][col] = 1
                step_diff.append((ln_init, col, 1, 0))
                step_diff.append((ln, col, 0, 1))
                state.coor_base = state.coor_cur = (x, ln)
                coor_redo = ((x, ln), (x, ln))
                history_manager.append(
                    StepChartChangeDelta(coor_undo, coor_redo, step_diff)
                )
            elif v_init == 2 and step_data[ln + 1][col] == 3:
                # Adjust tail of long note
                step_diff.append((ln, col, 2, 0))
                step_data[ln][col] = 0
                ln += 1
                if ctrl_pressed:
                    while (
                        ln + 1 <= ln_max
                        and step_data[ln + 1][col] == 3
                        and step_data[ln + 1][STEP_DATA_BI_IDX] == bi
                        and step_data[ln + 1][STEP_DATA_MS_IDX] == mi
                    ):
                        step_diff.append((ln, col, 3, 0))
                        step_data[ln][col] = 0
                        ln += 1
                step_diff.append((ln, col, 3, 2))
                step_data[ln][col] = 2
                state.coor_base = state.coor_cur = (x, ln)
                coor_redo = ((x, ln), (x, ln))
                history_manager.append(
                    StepChartChangeDelta(coor_undo, coor_redo, step_diff)
                )

            elif v_init == 3:
                # Move entire long note
                note_from, note_to = get_note_range(step_data, ln, col)
                if note_to + 1 > ln_max or step_data[note_to + 1][col] != 0:
                    return
                bi, mi = (
                    step_data[note_to + 1][STEP_DATA_BI_IDX],
                    step_data[note_to + 1][STEP_DATA_MS_IDX],
                )
                ln = note_to

                ln += 1
                if ctrl_pressed:
                    while (
                        ln + 1 <= ln_max
                        and step_data[ln + 1][col] == 0
                        and step_data[ln + 1][STEP_DATA_BI_IDX] == bi
                        and step_data[ln + 1][STEP_DATA_MS_IDX] == mi
                    ):
                        ln += 1

                prev_step_data = copy.deepcopy(step_data[note_from : ln + 1])
                offset = ln - note_to
                for l in range(ln, note_from - 1, -1):
                    if l > ln - (note_to - note_from + 1):
                        step_data[l][col] = step_data[l - offset][col]
                    else:
                        step_data[l][col] = 0
                    if prev_step_data[l - note_from][col] != step_data[l][col]:
                        step_diff.append(
                            (
                                l,
                                col,
                                prev_step_data[l - note_from][col],
                                step_data[l][col],
                            )
                        )
                state.coor_base = state.coor_cur = (x, ln_init + offset)
                coor_redo = (state.coor_cur, state.coor_base)
                history_manager.append(
                    StepChartChangeDelta(coor_undo, coor_redo, step_diff)
                )
            elif v_init == 4 and step_data[ln + 1][col] == 0:
                # Move head of long note
                step_diff.append((ln, col, 4, 3))
                step_data[ln][col] = 3
                ln += 1
                if ctrl_pressed:
                    while (
                        ln + 1 <= ln_max
                        and step_data[ln + 1][col] == 0
                        and step_data[ln + 1][STEP_DATA_BI_IDX] == bi
                        and step_data[ln + 1][STEP_DATA_MS_IDX] == mi
                    ):
                        step_diff.append((ln, col, 0, 3))
                        step_data[ln][col] = 3
                        ln += 1
                step_diff.append((ln, col, 0, 4))
                step_data[ln][col] = 4
                state.coor_base = state.coor_cur = (x, ln)
                coor_redo = ((x, ln), (x, ln))
                history_manager.append(
                    StepChartChangeDelta(coor_undo, coor_redo, step_diff)
                )

        elif ln != ln_max:
            ln += 1
            # block_idx_prev = step_data[ln][STEP_DATA_BI_IDX]
            bi, mi = (
                step_data[ln][STEP_DATA_BI_IDX],
                step_data[ln][STEP_DATA_MS_IDX],
            )
            if ctrl_pressed:
                while (
                    ln + 1 <= ln_max
                    and step_data[ln + 1][STEP_DATA_BI_IDX] == bi
                    and step_data[ln + 1][STEP_DATA_MS_IDX] == mi
                ):
                    ln += 1
            state.coor_cur = (state.coor_cur[0], ln)

            block_idx = step_data[state.coor_cur[1]][STEP_DATA_BI_IDX]
            if block_idx != bi:
                state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True

            if state.AUTO_LINE_PASS:
                state.coor_base = (state.coor_base[0], state.coor_cur[1])
            elif not (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]):
                state.coor_base = state.coor_cur

        else:
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

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        if state.MUSIC_PLAYING:
            return False
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
        if pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL]:
            x = 0
        elif x != 0:
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
        if state.MUSIC_PLAYING:
            return False
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
        if pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL]:
            x = cols - 1
        elif x != cols - 1:
            x += 1
        state.coor_cur = (x, state.coor_cur[1])
        if not (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]):
            state.coor_base = state.coor_cur
