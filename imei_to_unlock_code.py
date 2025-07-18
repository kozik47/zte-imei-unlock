#!/usr/bin/env python3

import argparse

def generate_unlock_code(imei):
    """
    Generate an 8-digit unlock code from a given IMEI.

    Args:
        imei (str): The IMEI string (at least 15 characters).

    Returns:
        str: The 8-digit unlock code or an error message if IMEI is too short.
    """
    if len(imei) < 15:
        return "Error: IMEI too short"

    digits = [int(char) for char in imei[:15]]
    transform_map = {0: 1, 1: 3, 2: 5, 3: 7, 4: 9, 5: 0, 6: 2, 7: 4, 8: 6, 9: 8}
    transformed = [transform_map.get(d, 0) for d in digits]
    unlock_digits = [sum(transformed[i:i+8]) % 10 for i in range(8)]
    return ''.join(map(str, unlock_digits))

def main():
    parser = argparse.ArgumentParser(description="Generate an 8-digit unlock code from a given IMEI.")
    parser.add_argument("imei", help="The IMEI string (at least 15 characters).")
    args = parser.parse_args()
    unlock_code = generate_unlock_code(args.imei)
    print(unlock_code)

if __name__ == "__main__":
    main()
