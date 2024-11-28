from manager.custom_key_logic import *


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
