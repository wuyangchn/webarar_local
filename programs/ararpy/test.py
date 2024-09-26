#  Copyright (C) 2024 Yang. - All Rights Reserved
"""
# ==========================================
# Copyright 2024 Yang
# ararpy - test.py
# ==========================================
#
#
#
"""
import ararpy as ap
import os


def test():
    example_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), r'examples')
    print(f"Running: ararpy.test()")
    print(f"============= Open an example .arr file =============")
    file_path = os.path.join(example_dir, r'22WHA0433.arr')
    sample = ap.from_arr(file_path=file_path)
    # file_path = os.path.join(example_dir, r'22WHA0433.age')
    # sample = ap.from_age(file_path=file_path)
    print(f"{file_path = }")
    print(f"sample = from_arr(file_path=file_path)")
    print(f"{sample.name() = }")
    print(f"{sample.help = }")
    print(f"sample.parameters() = {sample.parameters()}")
    print(f"sample.parameters().to_df() = \n{sample.parameters().to_df()}")
    print(sample.show_data())
    print(sample.sample())
    print(sample.blank().to_df().iloc[:, [1, 2, 3]])


if __name__ == "__main__":
    test()
