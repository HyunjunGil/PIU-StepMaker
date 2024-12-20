import os, sys
from datetime import datetime
from typing import List, Tuple, Dict
from constants import (
    STEP_DATA_OFFSET,
    STEP_DATA_VD_IDX,
    BLOCK_BM_IDX,
    BLOCK_MS_IDX,
    BLOCK_BT_IDX,
    BLOCK_SP_IDX,
    BLOCK_SB_IDX,
    BPM_MIN_COLOR,
    BPM_MAX_COLOR,
)


def get_base_path():
    if getattr(sys, "frozen", False):  # 실행 파일로 패키징된 상태
        base_path = sys._MEIPASS
    else:  # 개발 환경
        base_path = os.path.abspath(os.path.dirname(__file__))
        # base_path = os.path.join(base_path, "..\\")
    return base_path


def get_bpm_color(bpm_min: int, bpm_max: int, bpm: int):
    if bpm_min == bpm_max:
        return BPM_MIN_COLOR
    r = (bpm - bpm_min) / (bpm_max - bpm_min)
    r1, g1, b1 = BPM_MIN_COLOR
    r2, g2, b2 = BPM_MAX_COLOR
    return (r1 * (1 - r) + r2 * r, g1 * (1 - r) + g2 * r, b1 * (1 - r) + b2 * r)


def num_to_str(num: float | int):
    if type(num) == float and int(num) == num:
        return str(int(num))
    else:
        return str(num)


def str_to_num(x: str):
    try:
        return int(x)
    except:
        return round(float(x), 4)


def ms_to_beats(bpm: float | int, ms: float | int):
    v = round(bpm / 60_000 * ms, 4)
    if v == int(v):
        return int(v)
    else:
        return v


def beats_to_ms(bpm: float | int, beats: float | int):
    v = round(round(60_000 * beats / bpm, 4))
    if v == int(v):
        return int(v)
    else:
        return v


def binary_search(arr: List[int], v: int):

    left, right = 0, len(arr) - 1
    result = -1

    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == v:
            return mid
        elif arr[mid] < v:
            result = mid
            left = mid + 1
        else:
            right = mid - 1

    return result


def _valid_before(prev: int, cur: int) -> bool:
    return (prev in [0, 1, 4] and cur in [0, 1, 2]) or (
        prev in [2, 3] and cur in [3, 4]
    )


def _valid_after(cur: int, next: int) -> bool:
    return (next in [0, 1, 2] and cur in [0, 1, 4]) or (
        next in [3, 4] and cur in [2, 3]
    )


def update_validity(step_data: List[List[int]], ln_from: int, ln_to: int) -> int:
    ln_from, ln_to = max(0, ln_from), min(len(step_data), ln_to)
    assert 0 <= ln_from < ln_to <= len(step_data), "Invalid parameters, {} {}".format(
        ln_from, ln_to
    )
    tot_len = len(step_data)
    cols = range(STEP_DATA_OFFSET, len(step_data[0]))
    error_cnt = 0
    for ln in range(ln_from, ln_to):
        line = step_data[ln]
        flag = True
        for col in cols:
            if ln == 0:
                flag &= (ln + 1 == tot_len) or _valid_after(
                    step_data[ln][col], step_data[ln + 1][col]
                )
            elif ln < len(step_data) - 1:
                flag &= _valid_before(
                    step_data[ln - 1][col], step_data[ln][col]
                ) and _valid_after(step_data[ln][col], step_data[ln + 1][col])
            else:
                flag &= _valid_before(step_data[ln - 1][col], step_data[ln][col])
            if not flag:
                break
        error_cnt += 1 - flag
        step_data[ln][STEP_DATA_VD_IDX] = flag

    return error_cnt


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


def _clear_step(
    step_data: List[List[int]], ln: int, col: int
) -> Tuple[List[Tuple[int, int, int, int]], int, int]:
    res: List[Tuple[int, int, int, int]] = []
    if step_data[ln][col] == 0:
        return res, ln, ln

    v = step_data[ln][col]
    res.append((ln, col, v, 0))
    step_data[ln][col] = 0
    if v == 1:
        return res, ln, ln + 1
    elif v == 2:
        e = ln + 1
        while e < len(step_data) and step_data[e][col] in [3, 4]:
            res.append((e, col, step_data[e][col], 0))
            step_data[e][col] = 0
            e += 1
        return res, ln, e
    elif v == 4:
        s = ln - 1
        while s >= 0 and step_data[s][col] in [2, 3]:
            res.append((s, col, step_data[s][col], 0))
            step_data[s][col] = 0
            s -= 1
        return res, s + 1, ln + 1
    elif v == 3:
        s = ln - 1
        while s >= 0 and step_data[s][col] in [2, 3]:
            res.append((s, col, step_data[s][col], 0))
            step_data[s][col] = 0
            s -= 1
        e = ln + 1
        while e < len(step_data) and step_data[e][col] in [3, 4]:
            res.append((e, col, step_data[e][col], 0))
            step_data[e][col] = 0
            e += 1
        return res, s + 1, e


# col = with offset
def clear_step(
    step_data: List[List[int]], ln_from: int, ln_to: int, col: int  # col with  offset
) -> List[Tuple[int, int, int, int]]:
    res: List[Tuple[int, int, int, int]] = []
    if ln_from == ln_to - 1:
        res = _clear_step(step_data, ln_from, col)[0]
    else:
        res, ln_min, ln_max = _clear_step(step_data, ln_from, col)
        if ln_max < ln_to:
            res = res + _clear_step(step_data, ln_to - 1, col)[0]
    return res


def ms_to_str(ms: int):
    return datetime.fromtimestamp(ms / 1000).strftime("%M:%S.%f")[:-3]


def get_note_range(step_data: List[List[int]], ln: int, col: int) -> Tuple[int, int]:
    if step_data[ln][col] == 0:
        return ln, ln
    elif step_data[ln][col] == 1:
        return ln, ln
    elif step_data[ln][col] == 2:
        ln_to = ln
        while ln_to + 1 < len(step_data) and (
            (step_data[ln_to][col] == 2 and step_data[ln_to + 1][col] == 3)
            or (step_data[ln_to][col] == 3 and step_data[ln_to + 1][col] in [3, 4])
        ):
            ln_to += 1
        return ln, ln_to
    elif step_data[ln][col] == 3:
        ln_from = ln
        while ln_from - 1 < len(step_data) and (
            (step_data[ln_from][col] == 4 and step_data[ln_from - 1][col] == 3)
            or (step_data[ln_from][col] == 3 and step_data[ln_from - 1][col] in [2, 3])
        ):
            ln_from -= 1
        ln_to = ln
        while ln_to + 1 < len(step_data) and (
            (step_data[ln_to][col] == 2 and step_data[ln_to + 1][col] == 3)
            or (step_data[ln_to][col] == 3 and step_data[ln_to + 1][col] in [3, 4])
        ):
            ln_to += 1
        return ln_from, ln_to
    elif step_data[ln][col] == 4:
        ln_from = ln
        while ln_from - 1 < len(step_data) and (
            (step_data[ln_from][col] == 4 and step_data[ln_from - 1][col] == 3)
            or (step_data[ln_from][col] == 3 and step_data[ln_from - 1][col] in [2, 3])
        ):
            ln_from -= 1
        return ln_from, ln


def reduce_diff(step_diff: List[Tuple[int, int, int, int]]):
    initial_state: Dict[Tuple[int, int], int] = dict()
    final_state: Dict[Tuple[int, int], int] = dict()
    res_diff: List[Tuple[int, int, int, int]] = []
    for diff in step_diff:
        ln, col, prev, cur = diff
        if not (ln, col) in initial_state:
            initial_state[(ln, col)] = prev
        final_state[(ln, col)] = cur

    for ln, col in initial_state.keys():
        res_diff.append((ln, col, initial_state[(ln, col)], final_state[(ln, col)]))
    return res_diff
