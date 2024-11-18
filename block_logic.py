from typing import List, Tuple
from constants import *


def check_input(
    new_info: List[
        int
    ],  # [bpm, beat/measure, split/beat, delay, #measures, #beats, #splits]
):
    # new_bpm, new_bm, new_sb, new_delay, new_mcnt, new_bcnt, new_scnt = (
    #     new_info[0],
    #     new_info[1],
    #     new_info[2],
    #     new_info[3],
    #     new_info[4],
    #     new_info[5],
    #     new_info[6],
    # )

    return True


def modify_block(
    step_data: List[List[int]],
    block_info: List[List[int | float]],
    new_info: List[
        float | int
    ],  # [bpm, beat/measure, split/beat, delay, #measures, #beats, #splits]
    block_idx: int,
) -> Tuple[List[List[int]], List[List[int | float]]]:
    cols = len(step_data[0]) - STEP_DATA_OFFSET
    info = block_info[block_idx]
    bpm, bm, sb, delay, mcnt, bcnt, scnt = (
        info[0],
        info[1],
        info[2],
        info[3],
        info[4],
        info[5],
        info[6],
    )

    new_bpm, new_bm, new_sb, new_delay, new_mcnt, new_bcnt, new_scnt = (
        new_info[0],
        new_info[1],
        new_info[2],
        new_info[3],
        new_info[4],
        new_info[5],
        new_info[6],
    )

    new_block_step_data: List[List[int]] = []

    # Get line index for start & end of block
    s = 0
    while step_data[s][STEP_DATA_BI_IDX] != block_idx:
        s += 1
    block_lines = mcnt * bm * sb + bcnt * sb + scnt
    e = s + block_lines

    new_lines = new_mcnt * new_bm * new_sb + new_bcnt * new_sb + new_scnt

    for i in range(new_lines):
        line = [
            block_idx,
            i // (new_bm * new_sb),
            (i % (new_bm * new_sb)) // new_sb,
            i % new_sb,
        ]
        if i < block_lines:
            # If block line exists, copy it
            new_block_step_data.append(
                line + [step_data[s + i][STEP_DATA_OFFSET + j] for j in range(cols)]
            )
        else:
            # If block line does not exists, create empty line
            new_block_step_data.append(line + [0 for _ in range(cols)])

    # Update step_data and block_info
    step_data = step_data[:s] + new_block_step_data + step_data[e:]
    block_info[block_idx] = [
        new_bpm,
        new_bm,
        new_sb,
        new_delay,
        new_mcnt,
        new_bcnt,
        new_scnt,
    ]

    return step_data, block_info


def delete_block(
    step_data: List[List[int]],
    block_info: List[List[int | float]],
    block_idx: int,
) -> Tuple[List[List[int]], List[List[int | float]]]:
    tot_ln, cols = len(step_data), len(step_data[0]) - STEP_DATA_OFFSET
    info = block_info[block_idx]
    bpm, bm, sb, delay, mcnt, bcnt, scnt = (
        info[0],
        info[1],
        info[2],
        info[3],
        info[4],
        info[5],
        info[6],
    )
    block_lines = mcnt * bm * sb + bcnt * sb + scnt

    ln_from = 0
    while step_data[ln_from][STEP_DATA_BI_IDX] != block_idx:
        ln_from += 1
    ln_to = ln_from + block_lines

    # Update block_idx for blcok after block_idx
    for ln in range(ln_to, tot_ln):
        step_data[ln][STEP_DATA_BI_IDX] -= 1

    # Update step_data and block_info
    step_data = step_data[:ln_from] + step_data[ln_to:]
    block_info.pop(block_idx)

    return step_data, block_info


def add_block_up(
    step_data: List[List[int]],
    block_info: List[List[int | float]],
    block_idx: int,
) -> Tuple[List[List[int]], List[List[int | float]]]:

    if block_idx == 0:
        cols = len(step_data[0]) - STEP_DATA_OFFSET
        info = block_info[block_idx]
        bpm, bm, sb, delay, mcnt, bcnt, scnt = (
            info[0],
            info[1],
            info[2],
            info[3],
            info[4],
            info[5],
            info[6],
        )
        for ln in range(len(step_data)):
            step_data[ln][STEP_DATA_BI_IDX] += 1
        step_data = [
            [
                0,
                i // (bm * sb),
                (i % (bm * sb)) // sb,
                i % sb,
            ]
            + [0 for _ in range(cols)]
            for i in range(bm * sb)
        ] + step_data
        block_info.insert(block_idx, [bpm, bm, sb, delay, 1, 0, 0])
        return step_data, block_info
    else:
        return add_block_down(step_data, block_info, block_idx - 1)


def add_block_down(
    step_data: List[List[int]],
    block_info: List[List[int | float]],
    block_idx: int,
) -> Tuple[List[List[int]], List[List[int | float]]]:
    # Create new block between current block and next block
    # New block will have size (1 Measure, 0 Beat, 0 Split) automatically
    tot_ln, cols = len(step_data), len(step_data[0]) - STEP_DATA_OFFSET
    info = block_info[block_idx]
    bpm, bm, sb, delay, mcnt, bcnt, scnt = (
        info[0],
        info[1],
        info[2],
        info[3],
        info[4],
        info[5],
        info[6],
    )
    block_lines = mcnt * bm * sb + bcnt * sb + scnt

    s = 0
    while step_data[s][STEP_DATA_BI_IDX] != block_idx:
        s += 1
    e = s + block_lines

    # Update block_idx for blcok after block_idx
    for ln in range(e, tot_ln):
        step_data[ln][STEP_DATA_BI_IDX] += 1

    # New block will save size 1 Measure, 0 Beat, 0 Split
    new_block_step_data = [
        [
            block_idx + 1,
            i // (bm * sb),
            (i % (bm * sb)) // sb,
            i % sb,
        ]
        + [0 for _ in range(cols)]
        for i in range(bm * sb)
    ]
    step_data = step_data[:e] + new_block_step_data + step_data[e:]
    block_info.insert(block_idx + 1, [bpm, bm, sb, delay, 1, 0, 0])

    return step_data, block_info


def split_block(
    step_data: List[List[int]],
    block_info: List[List[int | float]],
    block_idx: int,
    line_idx: int,
) -> Tuple[List[List[int]], List[List[int | float]]]:
    tot_ln, cols = len(step_data), len(step_data[0]) - STEP_DATA_OFFSET
    info = block_info[block_idx]
    bpm, bm, sb, delay, mcnt, bcnt, scnt = (
        info[0],
        info[1],
        info[2],
        info[3],
        info[4],
        info[5],
        info[6],
    )
    block_lines = mcnt * bm * sb + bcnt * sb + scnt

    s = 0
    while step_data[s][STEP_DATA_BI_IDX] != block_idx:
        s += 1
    e = s + block_lines

    if s > line_idx:
        raise Exception("Invalid parameter : s > line_idx")
    # If given line_idx is equal to line_idx, do nothing
    elif s == line_idx:
        return step_data, block_info

    assert s < line_idx < e
    new_block_lines = e - line_idx

    # Update block_idx for blcok after line_idx
    for ln in range(line_idx, tot_ln):
        step_data[ln][STEP_DATA_BI_IDX] += 1

    # Update
    for ln in range(line_idx, e):
        lcnt = ln - line_idx
        step_data[ln][STEP_DATA_MS_IDX] = lcnt // (bm * sb)
        step_data[ln][STEP_DATA_BT_IDX] = (lcnt % (bm * sb)) // sb
        step_data[ln][STEP_DATA_SP_IDX] = lcnt % sb

    block_info[block_idx] = [
        bpm,
        bm,
        sb,
        delay,
        (line_idx - s) // (bm * sb),
        ((line_idx - s) % (bm * sb)) // sb,
        (line_idx - s) % sb,
    ]
    block_info.insert(
        block_idx + 1,
        [
            bpm,
            bm,
            sb,
            delay,
            new_block_lines // (bm * sb),
            (new_block_lines % (bm * sb)) // sb,
            new_block_lines % sb,
        ],
    )

    return step_data, block_info
