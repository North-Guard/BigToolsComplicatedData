import regex as re
import sys
from pathlib import Path


sys.setrecursionlimit(25000)


def task_max_pattern_length(task_inputs):
    return sum([len(val) if isinstance(val, str) else max(val) for val in task_inputs])


def task_re_pattern(task_inputs):
    return "".join(val if isinstance(val, str) else f".{{{val[0]},{val[1]}}}" for val in task_inputs)


def nested_search(task_inputs, string):
    # Find all starting points
    start_pattern = task_inputs[0]
    starting_points = list(reversed([val.start() for val in re.finditer(start_pattern, string)]))

    # Make search-pattern
    pattern = task_re_pattern(task_inputs)
    pattern = "(?<=(" + pattern + "))"

    # Determine longest possible pattern-string
    max_pattern_length = task_max_pattern_length(task_inputs)

    # Recursively apply pattern
    return _nested_re_search(pattern, string, starting_points, max_pattern_length)


def _nested_re_search(pattern, string, starting_points, max_pattern_length=None):
    if not starting_points:
        return []

    # Cut off start, which has already been handled
    c_start = starting_points.pop()
    c_end = c_start + max_pattern_length

    # Search in string
    search = list(re.finditer(pattern, string, pos=c_start, endpos=c_end))

    # Convert to include starting-point
    search = [(val.start(1), val.end(1), val.group(1)) for val in search]

    # Recursion
    return search + _nested_re_search(pattern, string, starting_points, max_pattern_length)


if __name__ == "__main__":

    inputs_list = [
        ["A", (2, 8), "C"],
        ["A", (2, 8), "C", (2, 8), "A"]
    ]

    for inputs in inputs_list:

        test_str = "AdddddddddddddAbbCAddCAegCAgrC"

        print(f"\nInputs: {inputs}")
        print(f"Test string: {test_str}")
        print("Matches:")
        for match in nested_search(inputs, test_str):
            print(f"\t{match!s:40s}", "Correctness-check:", match[2] == test_str[match[0]:match[1]])

    pattern = ["cat", (2, 8), "dog"]
    print(f"\nMatching {pattern} in file 'catz.txt'")
    with Path("Source/BigTools/catz.txt").open("r") as file:
        test_str = ""
        for line in file:
            test_str += line + "\n"
    results = nested_search(pattern, test_str)
    for result in results:
        print(f"\t{result!s:40s}", "Correctness-check:", result[2] == test_str[result[0]:result[1]])
