from typing import List, Tuple
from constants import STEP_DATA_OFFSET, STEP_DATA_VD_IDX


def _valid_before(prev: int, cur: int) -> bool:
    return (prev in [0, 1, 4] and cur in [0, 1, 2]) or (
        prev in [2, 3] and cur in [3, 4]
    )


def _valid_after(cur: int, next: int) -> bool:
    return (next in [0, 1, 2] and cur in [0, 1, 4]) or (
        next in [3, 4] and cur in [2, 3]
    )


def update_validity(
    step_data: List[List[int]], ln_from: int, ln_to: int, col: int | None = None
):
    print("update_validity", ln_from, ln_to, col)
    ln_from, ln_to = max(0, ln_from), min(len(step_data), ln_to)
    assert (
        0 <= ln_from < ln_to <= len(step_data)
    ), "Invalid parameters, {} {} {}".format(ln_from, ln_to, col)
    tot_len = len(step_data[0])
    cols = range(STEP_DATA_OFFSET, tot_len) if col is None else [col]
    for ln in range(ln_from, ln_to):
        line = step_data[ln]
        for col in cols:
            if ln == 0:
                step_data[ln][STEP_DATA_VD_IDX] &= _valid_after(
                    step_data[ln][col], step_data[ln + 1][col]
                )
            elif ln < len(step_data) - 1:
                step_data[ln][STEP_DATA_VD_IDX] &= _valid_before(
                    step_data[ln - 1][col], step_data[ln][col]
                ) and _valid_after(step_data[ln][col], step_data[ln + 1][col])
            else:
                step_data[ln][STEP_DATA_VD_IDX] &= _valid_before(
                    step_data[ln - 1][col], step_data[ln][col]
                )
            if not step_data[ln][STEP_DATA_VD_IDX]:
                break


def get_step_diff(
    prev_step_data: List[List[int]], step_data: List[List[int]], ln_offset: int
):
    assert len(prev_step_data) == len(
        step_data
    ), "len(prev_step_data) != len(step_data)"

    # Get StepChartChangeDelta
    step_diff: List[Tuple[int, int, int, int]] = []
    for ln in range(len(prev_step_data)):
        for col in range(STEP_DATA_OFFSET, len(prev_step_data[0])):
            if step_data[ln][col] != prev_step_data[ln][col]:
                step_diff.append(
                    (
                        ln_offset + ln,
                        col,
                        prev_step_data[ln][col],
                        step_data[ln][col],
                    )
                )

    return step_diff
