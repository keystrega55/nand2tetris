import re
from pathlib import Path


class Parser:
    """
    Parses a single .vm file and encapsulates access to input code.
    Reads VM commands, parses them, and provides access to their components.
    Removes all white space and comments.

    A command is composed of three parts:
    <command> <segment> <index>
    e.g. push local 2

    If command type is arithmetic, segment and index parts are excluded.
    e.g. add
    """

    def __init__(self, vm_file) -> None:
        self.in_file = vm_file
        self.in_file_name = Path(vm_file).stem

        self.lines = self.remove_comments(self.remove_empty_strings(vm_file))
        self.lines.reverse()
        self.current_line = None
        # self.current_command = None
        self.command_types = self.command_types_dict()

    def remove_comments(self, lines: list) -> list:
        return [re.sub(r'//(.+)*', '', line) for line in lines]

    def remove_empty_strings(self, vm_file) -> list:
        lines = []
        with open(vm_file, 'r') as f:
            for line in f:
                if line.strip():
                    lines.append(line)
        return lines

    def advance(self) -> None:
        self.current_line = self.lines.pop()

    def has_more_commands(self) -> bool:
        return self.lines != []

    def command_type(self):
        if len(self.current_line) == 0:
            return None
        elif self.current_line.count(' ') < 1:
            return self.command_types.get(self.current_line.rstrip())
        else:
            return self.command_types.get(self.current_line.split()[0])

    def command_types_dict(self) -> dict:
        return {
            'add': 'C_ARITHMETIC',
            'sub': 'C_ARITHMETIC',
            'neg': 'C_ARITHMETIC',
            'eq': 'C_ARITHMETIC',
            'gt': 'C_ARITHMETIC',
            'lt': 'C_ARITHMETIC',
            'and': 'C_ARITHMETIC',
            'or': 'C_ARITHMETIC',
            'not': 'C_ARITHMETIC',
            'push': 'C_PUSH',
            'pop': 'C_POP',
            'label': 'C_LABEL',
            'goto': 'C_GOTO',
            'if-goto': 'C_IF',
            'function': 'C_FUNCTION',
            'return': 'C_RETURN',
            'call': 'C_CALL',
        }

    def command(self) -> str:
        # Returns vm command (e.g. push, pop, add, sub, etc.)
        return self.current_line.split()[0]

    def arg1(self) -> str:
        # Returns first argument of current command.
        # Should be called only if current command is
        # C_PUSH, C_POP, C_FUNCTION or C_CALL.
        # Should NOT be called if current command is C_RETURN.
        return self.current_line.split()[1]

    def arg2(self) -> int:
        return int(self.current_line.split()[2])
