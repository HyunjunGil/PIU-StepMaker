from manager.custom_key_logic.base import *
from constants import *
from core import update_validity, clear_step


# Step Chart
class StepChartKey(KeyBase):
    def __init__(self):
        super().__init__()

    @staticmethod
    def condition(state: State, event: pygame.Event) -> bool:
        if state.MUSIC_PLAYING:
            return False
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
                step_diff.append((ln_from, col, 0, 1))
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
                elif ln_from < ln < ln_to - 1 and v != 3:
                    done = False
                    step_diff.append((ln, col, v, 3))
                elif ln == ln_to - 1 and v != 4:
                    done = False
                    step_diff.append((ln, col, v, 4))
            if done:
                return
            else:
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
