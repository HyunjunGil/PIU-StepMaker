import pygame, pygame_gui

from typing import List, Tuple, Dict
from state import State
from enum import Enum
from block_logic import *


class DeltaType(Enum):
    INITIAL = "INITIAL"
    STEP_CHART_CHANGE = "STEP_CHART_CHANGE"
    BLOCK_MODIFY = "BLOCK_MODIFY"
    BLOCK_ADD_ABOVE = "BLOCK_ADD_ABOVE"
    BLOCK_ADD_BELOW = "BLOCK_ADD_BELOW"
    BLOCK_SPLIT = "BLOCK_SPLIT"
    BLOCK_DELETE = "BLOCK_DELETE"


class StateDelta:
    def __init__(
        self, y_undo: Tuple[int, int], y_redo: Tuple[int, int], delta_type: DeltaType
    ):
        self.y_undo = y_undo
        self.y_redo = y_redo
        self.delta_type = delta_type

    def undo(self, state: State):

        state.update_y_info()
        state.y_cur, state.y_base = self.y_undo()
        state.sync_scr_y()

    def redo(self, state: State):
        state.update_y_info()
        state.y_cur, state.y_base = self.y_redo()
        state.sync_scr_y()


class InitialDelta(StateDelta):
    def __init__(self, y_undo: Tuple[int], y_redo: Tuple[int]):
        super().__init__(y_undo, y_redo, DeltaType.INITIAL)

    def undo(self, state: State):
        raise Exception("InitialDelta should not be undo")

    def redo(self, state: State):
        raise Exception("InitialDelta should not be redo")


class StepChartChangeDelta(StateDelta):
    def __init__(
        self,
        y_undo: Tuple[int, int],
        y_redo: Tuple[int, int],
        step_diff: List[
            Tuple[int, int, int, int]
        ],  # ln, col(added STEP_DATA_OFFSET), before, after
    ):
        super().__init__(y_undo, y_redo, DeltaType.STEP_CHART_CHANGE)
        self.step_diff = step_diff

    def undo(self, state: State):
        step_data = state.step_data
        for diff in self.step_diff:
            ln, col, prev, _ = diff
            step_data[ln][col] = prev

        state.y_cur, state.y_base = self.y_undo()
        state.sync_scr_y()

    def redo(self, state: State):
        step_data = state.step_data
        for diff in self.step_diff:
            ln, col, _, cur = diff
            step_data[ln][col] = cur

        state.y_cur, state.y_base = self.y_redo()
        state.sync_scr_y()


class BlockModifyDelta(StateDelta):
    def __init__(
        self,
        y_undo: Tuple[int],
        y_redo: Tuple[int],
        block_idx: int,
        prev_block_step_data: List[List[int]],
        prev_block: List[float | int],
        new_info: List[float | int],
    ):
        super().__init__(y_undo, y_redo, DeltaType.BLOCK_MODIFY)
        self.block_idx = block_idx
        self.prev_block_step_data = prev_block_step_data
        self.prev_block = prev_block
        self.new_info = new_info

    def undo(self, state: State):
        step_data, block_info = state.get_step_info()
        ln_from, ln_to = state.get_block_range_by_block_idx(self.block_idx)
        state.step_data = (
            step_data[:ln_from] + self.prev_block_step_data + step_data[ln_to:]
        )
        state.block_info[self.block_idx] = self.prev_block
        super().undo(state)

    def redo(self, state: State):
        state.step_data, state.block_info = modify_block(
            state.step_data, state.block_info, self.new_info, self.block_idx
        )
        super().redo(state)


class BlockDeleteDelta(StateDelta):
    def __init__(
        self,
        y_undo: Tuple[int],
        y_redo: Tuple[int],
        block_idx: int,
        deleted_step_data: List[List[int]],
        deleted_block_info: List[float | int],
    ):
        super().__init__(y_undo, y_redo, DeltaType.BLOCK_DELETE)
        self.block_idx = block_idx
        self.deleted_step_data = deleted_step_data
        self.deleted_block_info = deleted_block_info

    def undo(self, state: State):
        step_data, block_info = state.get_step_info()
        _, ln_to = state.get_block_range_by_y(state.ln_to_y[self.ln - 1])
        for ln in range(ln_to, len(step_data)):
            step_data[ln][STEP_DATA_BI_IDX] += 1
        state.step_data = step_data[:ln_to] + self.deleted_step_data + step_data[ln_to:]
        block_info.insert(self.block_idx, self.deleted_block_info)

        super().undo(state)

    def redo(self, state: State):
        state.step_data, state.block_info = delete_block(
            state.step_data, state.block_info, self.block_idx
        )
        super().redo(state)


class BlockAddAboveDelta(StateDelta):
    def __init__(
        self, y_undo: Tuple[int, int], y_redo: Tuple[int, int], block_idx: int
    ):

        super().__init__(y_undo, y_redo, DeltaType.BLOCK_ADD_ABOVE)
        self.block_idx: int = block_idx  # origin block idx (= added block idx + 1)

    def undo(self, state: State):
        step_data, block_info = state.get_step_info()
        ln_from, idx = 0, 0
        while idx < self.block_idx - 1:
            block = block_info[idx]
            ln_from += (block[4] * block[1] + block[5]) * block[2] + block[
                6
            ]  # number of lines in the block
        block = block_info[self.block_idx]
        ln_to = ln_from + (block[4] * block[1] + block[5]) * block[2] + block[6]

        state.step_data = step_data[:ln_from] + step_data[ln_to:]
        state.block_info.pop(self.block_idx - 1)

        super().undo(state)

    def redo(self, state: State):
        state.step_data, state.block_info = add_block_up(
            state.step_data, state.block_info, self.block_idx
        )

        super().redo(state)


class BlockAddBelowDelta(StateDelta):
    def __init__(
        self, y_undo: Tuple[int, int], y_redo: Tuple[int, int], block_idx: int
    ):

        super().__init__(y_undo, y_redo, DeltaType.BLOCK_ADD_BELOW)
        self.block_idx: int = block_idx  # origin block idx (= added block idx - 1)

    def undo(self, state: State):
        step_data, block_info = state.get_step_info()
        ln_from, idx = 0, 0
        while idx < self.block_idx:
            block = block_info[idx]
            ln_from += (block[4] * block[1] + block[5]) * block[2] + block[
                6
            ]  # number of lines in the block
        block = block_info[self.block_idx + 1]
        ln_to = ln_from + (block[4] * block[1] + block[5]) * block[2] + block[6]

        state.step_data = step_data[:ln_from] + step_data[ln_to:]
        state.block_info.pop(self.block_idx + 1)

        super().undo(state)

    def redo(self, state: State):
        state.step_data, state.block_info = add_block_down(
            state.step_data, state.block_info, self.block_idx
        )

        super().redo(state)


class BlockSplitDelta(StateDelta):
    def __init__(self, y_undo: Tuple[int], y_redo: Tuple[int], block_idx: int, ln: int):
        super().__init__(y_undo, y_redo, DeltaType.BLOCK_SPLIT)
        self.block_idx: int = block_idx
        self.ln: int = ln

    def undo(self, state: State):
        step_data, block_info = state.get_step_info()
        ln_from, _ = state.get_block_range_by_y(state.ln_to_y[self.ln])
        _, ln_to = state.get_block_range_by_y(state.ln_to_y[self.ln + 1])

        tot_ln = ln_to - ln_from
        block = block_info[step_data[self.ln][STEP_DATA_BI_IDX]]
        bpm, bm, sb, delay = block[0], block[1], block[2], block[3]
        for ln in range(ln_from, ln_to):
            lcnt = ln - ln_from
            step_data[ln][STEP_DATA_BI_IDX] = self.block_idx
            step_data[ln][STEP_DATA_MS_IDX] = lcnt // (bm * sb)
            step_data[ln][STEP_DATA_BT_IDX] = (lcnt % (bm * sb)) // sb
            step_data[ln][STEP_DATA_SP_IDX] = lcnt % sb
        for ln in range(ln_to, len(step_data)):
            step_data[ln][STEP_DATA_BI_IDX] -= 1

        block_info.pop(self.block_idx + 1)
        block_info[self.block_idx] = [
            bpm,
            bm,
            sb,
            delay,
            tot_ln // (bm * sb),
            (tot_ln % (bm * sb)) // sb,
            tot_ln % sb,
        ]

        super().undo(state)

    def redo(self, state: State):
        state.step_data, state.block_info = split_block(
            state.step_data, state.block_info, self.block_idx, self.ln
        )

        super().redo(state)


class StateManager:
    def __init__(self):
        self.state: State = State()
        self.history: List[StateDelta] = []
        self.cur_idx = 0
        self.initialized = False

    def initialize(self, state: State):
        self.history.append(
            InitialDelta((state.y_cur, state.y_base), (state.y_cur, state.y_base))
        )
        self.initialized = True

    def undo(self, state: State):
        assert (
            self.initialized
        ), "Unable to perform undo() : HistoryManager is not Initialized"
        if self.cur_idx == 0:
            return
        self.history[self.cur_idx].undo()
        self.cur_idx -= 1

    def redo(self, state: State):
        assert (
            self.initialized
        ), "Unable to perform redo() : HistoryManager is not Initialized"
        if self.cur_idx >= len(self.history):
            return
        self.cur_idx += 1
        self.history[self.cur_idx].redo()

    def append(self, state_delta: StateDelta):
        assert (
            self.initialized
        ), "Unable to perform append() : HistoryManager is not Initialized"
        self.history = self.history[: self.cur_idx + 1]
        self.history.append(state_delta)


if __name__ == "__main__":
    print(DeltaType.BLOCK_ADD_BELOW.value)
