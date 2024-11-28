from manager.custom_key_logic.base import *

from constants import *
from gui import (
    BlockAddAboveButton,
    BlockAddBelowButton,
    BlockDeleteButton,
    BlockSplitButton,
)


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

        if event.key == pygame.K_u:
            BlockAddAboveButton.action(history_manager, state, event, ui_elements)
        elif event.key == pygame.K_i:
            BlockAddBelowButton.action(history_manager, state, event, ui_elements)
        elif event.key == pygame.K_o:
            BlockSplitButton.action(history_manager, state, event, ui_elements)
        elif event.key == pygame.K_p:
            BlockDeleteButton.action(history_manager, state, event, ui_elements)
