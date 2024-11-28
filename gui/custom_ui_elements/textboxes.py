from gui.custom_ui_elements.base import *
from constants import *
from core import num_to_str, beats_to_ms


class PlayTimeTextbox(ElementBase):
    def __init__(
        self, element: UIButton | UITextEntryLine | UIPanel | UITextBox | UILabel
    ):
        super().__init__(element)
        self.e.disable()

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        pass


def _enable_apply_button(info: List[int | float], new_info: List[int | float]) -> bool:
    assert len(info) == len(
        new_info
    ), "len(info) != len(new_info) in _enable_apply_button"
    for v, nv in zip(info, new_info):
        if nv == "":
            return False
        elif v != nv:
            return True
    return False


# Block Information Text Box
class BlockInformationText(ElementBase):
    def __init__(self, element: UITextEntryLine):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return (
            event.type
            in [pygame_gui.UI_TEXT_ENTRY_FINISHED, pygame_gui.UI_TEXT_ENTRY_CHANGED]
            and event.ui_element == self.e
        )

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            ui_elements[state.focus_idx].e.redraw()
            new_info = get_block_info_texts(ui_elements)
            if (
                state.delay_unit == DelayUnit.beats
                and len(new_info[BLOCK_DL_IDX])
                and len(new_info[BLOCK_BPM_IDX])
            ):
                new_info[BLOCK_DL_IDX] = num_to_str(
                    beats_to_ms(
                        float(new_info[BLOCK_BPM_IDX]), float(new_info[BLOCK_DL_IDX])
                    )
                )
            step_data, block_info = state.get_step_info()
            info = block_info[step_data[state.coor_cur[1]][STEP_DATA_BI_IDX]]
            info = [num_to_str(x) for x in info]
            if _enable_apply_button(info, new_info):
                ui_elements[BI_APPLY_BUTTON].enable()
                state.APPLY_ENABLED = True
            else:
                ui_elements[BI_APPLY_BUTTON].disable()
                state.APPLY_ENABLED = False
        else:
            text = ui_elements[state.focus_idx].get_text()
            if text == "":
                state.log("(Error) Cannot modify block : Empty input")
                return
            pygame.event.post(
                pygame.event.Event(
                    pygame_gui.UI_BUTTON_PRESSED,
                    {
                        "user_type": pygame_gui.UI_BUTTON_PRESSED,
                        "ui_element": ui_elements[BI_APPLY_BUTTON].e,
                    },
                )
            )

    def set_text(self, s: str):
        self.e.set_text(s)
        self.e.redraw()


# UI_INDEX : 5
class BPMTexbox(BlockInformationText):
    def __init__(self, element: UIElement):
        super().__init__(element)
        self.e.set_allowed_characters([f"{i}" for i in range(10)] + ["."])

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


# UI_INDEX : 6
class BeatPerMeasureTextbox(BlockInformationText):
    def __init__(self, element: UIElement):
        super().__init__(element)
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


# UI_INDEX : 7
class SplitPerBeatTextbox(BlockInformationText):
    def __init__(self, element: UIElement):
        super().__init__(element)
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


# UI_INDEX : 8
class DelayTexbox(BlockInformationText):
    def __init__(self, element: UIElement):
        super().__init__(element)
        self.e.set_allowed_characters([f"{i}" for i in range(10)] + ["."])

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


# UI_INDEX : 10
class MeasuresTexbox(BlockInformationText):
    def __init__(self, element: UIElement):
        super().__init__(element)
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


# UI_INDEX : 11
class BeatsTexbox(BlockInformationText):
    def __init__(self, element: UIElement):
        super().__init__(element)
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


# UI_INDEX : 12
class SplitsTexbox(BlockInformationText):
    def __init__(self, element: UIElement):
        super().__init__(element)
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


class LogTextbox(ElementBase):
    def __init__(
        self, element: UIButton | UITextEntryLine | UIPanel | UITextBox | UILabel
    ):
        super().__init__(element)
        self.e.disable()

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        pass
