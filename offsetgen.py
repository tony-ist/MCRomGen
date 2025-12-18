def generate_offsets(
    groups=9,
    blocks_per_group=7,
    intra_step=-2,
    inter_group_gap=-4,
    start=0,
):
    offsets = []
    current = start

    for _ in range(groups):
        for i in range(blocks_per_group):
            offsets.append(current + i * intra_step)
        current = offsets[-1] + inter_group_gap

    return offsets


if __name__ == "__main__":
    offsets = generate_offsets()
    print(' '.join(map(str, offsets)))
