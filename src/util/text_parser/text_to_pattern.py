from pattern.flat_pattern.pattern import Pattern
from util.text_parser.text_parser import text_to_list_of_atoms, text_to_list_of_vars

def text_to_pattern(text: str, restricted_vars: str):
    return Pattern(text_to_list_of_atoms(text), text_to_list_of_vars(restricted_vars))