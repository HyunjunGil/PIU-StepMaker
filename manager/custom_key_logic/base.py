import pygame, pygame_gui
from typing import List, Tuple, Dict
from gui.custom_ui_elements.base import ElementBase
from manager.history_manager import (
    HistoryManager,
    StepChartChangeDelta,
)
from manager.state_manager import State


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
