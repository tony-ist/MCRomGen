def generate_values():
 return [f"{i:02X}" for i in range(252)]

if __name__ == "__main__":
    values = generate_values()
    print(' '.join(values))
