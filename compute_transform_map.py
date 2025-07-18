#!/usr/bin/env python3

import argparse
import z3

def solve_all_transform_maps(imei_samples, unlock_codes):
    """
    Use Z3 to find the transform map given IMEI and unlock code samples.

    Args:
        imei_samples (list of str): List of IMEI strings.
        unlock_codes (list of str): List of corresponding unlock codes.

    Returns:
        list of dict: List of possible transform maps.
    """
    mappings = [z3.Int(f'map_{i}') for i in range(10)]
    s = z3.Solver()
    for m in mappings:
        s.add(z3.And(m >= 0, m <= 9))

    for imei, unlock in zip(imei_samples, unlock_codes):
        digits = [int(c) if c.isdigit() else 0 for c in imei[:15]]
        for i in range(8):
            sum_expr = z3.Sum([mappings[digits[i + j]] for j in range(8)])
            s.add(sum_expr % 10 == int(unlock[i]))

    solutions = []
    while s.check() == z3.sat:
        model = s.model()
        transform_map = {i: model[mappings[i]].as_long() for i in range(10)}
        solutions.append(transform_map)
        block = z3.Or([mappings[i] != transform_map[i] for i in range(10)])
        s.add(block)

    return solutions if solutions else None

def main():
    parser = argparse.ArgumentParser(description="Compute possible transform maps from IMEI:unlock_code pairs.")
    parser.add_argument("pairs", nargs="+", help="IMEI:unlock_code pairs, e.g., 010203040506071:88552291")
    args = parser.parse_args()

    imei_list = []
    unlock_list = []
    for pair in args.pairs:
        try:
            imei, unlock = pair.split(":")
            imei_list.append(imei)
            unlock_list.append(unlock)
        except ValueError:
            print(f"Invalid pair format: {pair}. Expected IMEI:unlock_code")
            exit(1)

    transform_maps = solve_all_transform_maps(imei_list, unlock_list)
    if transform_maps:
        print(f"Found {len(transform_maps)} possible transform maps:")
        for i, tm in enumerate(transform_maps, 1):
            print(f"Solution {i}: {tm}")
    else:
        print("No solutions found")

if __name__ == "__main__":
    main()
