from collections.abc import Callable
from typing import TypeVar

Number = TypeVar("Number", int, float)

# keep promting a input from user
def _ask_number(prompt: str, convert: Callable[[str], Number],
                is_valid: Callable[[Number], bool],
                rule_message: str, format_message: str) -> Number:
    while True:
        try:
            value = convert(input(prompt))
        except ValueError:
            print(format_message)
            continue
        if not is_valid(value):
            print(rule_message)
            continue
        return value

def get_positive_float(prompt: str) -> float:
    return _ask_number(prompt, float, lambda value: value > 0,"Please enter a number greater than zero.","Please enter a valid number, e.g. 12.50")

def get_non_negative_float(prompt: str) -> float:
    return _ask_number(prompt, float, lambda value: value >= 0,"Please enter zero or a positive number.","Please enter a valid number, e.g. 2.5")

def get_positive_int(prompt: str) -> int:
    return _ask_number(prompt, int, lambda value: value > 0,"Please enter a whole number greater than zero.","Please enter a whole number, e.g. 5")

def get_non_negative_int(prompt: str) -> int:
    return _ask_number(prompt, int, lambda value: value >= 0,"Please enter zero or a positive whole number.","Please enter a whole number, e.g. 5")

def get_int(prompt: str) -> int:
    return _ask_number(prompt, int, lambda value: True, "","Please enter a whole number, e.g. +10 or -5")

def get_text(prompt: str) -> str:
    while not (text := input(prompt).strip()):
        print("This field cannot be empty.")
    return text

def get_choice(prompt: str, choices: list[str]) -> str:
    while (choice := input(prompt).strip()) not in choices:
        print(f"Please choose one of: {', '.join(choices)}")
    return choice
