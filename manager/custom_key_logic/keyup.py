from manager.custom_key_logic.base import *
from constants import *


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
