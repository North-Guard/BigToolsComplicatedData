import regex as re
import sys
from pathlib import Path
from collections import OrderedDict

sys.setrecursionlimit(25000)


def task_max_pattern_length(task_inputs):
    return sum([len(val) if isinstance(val, str) else max(val) for val in task_inputs])


def task_re_pattern(task_inputs):
    return "".join(val if isinstance(val, str) else f".{{{val[0]},{val[1]}}}" for val in task_inputs)


def nested_search(task_inputs, string, identifier=None):
    pattern = task_re_pattern(task_inputs)

    # Get searches through substrings
    all_searches = _nested_re_search(pattern, string, identifier=identifier)

    # Convert to include starting-point
    all_searches = list(all_searches)

    return all_searches


def _nested_re_search(pattern, string, identifier, start=None, end=None):
    start = start if start is not None else 0
    end = end if end is not None else len(string)

    # Search in string
    searches = list(re.finditer(pattern, string, pos=start, endpos=end, overlapped=True))
    all_searches = set((identifier, val.start(), val.end(), val.group()) for val in searches)

    # Search substring
    for search in searches:
        # Cut off start
        all_searches.update(_nested_re_search(pattern, string,
                                              start=search.start() + 1,
                                              end=search.end(),
                                              identifier=identifier))

        # Cut off end
        all_searches.update(_nested_re_search(pattern, string,
                                              start=search.start(),
                                              end=search.end() - 1,
                                              identifier=identifier))

    # Recursion
    return all_searches


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

    bob = "english-to-chinese dictionary and is arranged [[english alphabet"
    print(nested_search(['english', (0, 100), 'alphabet'], bob))
