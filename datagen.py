def generate_values():
    values = []
    value = 1
    for i in range(63):
        values.append(f"{value:04X}")
        value <<= 1

        if value == 0x1000:
            value = 1

    return values

if __name__ == "__main__":
    values = generate_values()
    print(' '.join(values))
