# A_COMMAND format: @Xxx where Xxx is a symbol or decimal number
from symbol_table import SymbolTable
from typing import Literal


A_COMMAND = 0

# C_COMMAND format: dest=comp;jump
C_COMMAND = 2

# L_COMMAND format: (Xxx) where Xxx is a symbol
L_COMMAND = 4

# Encapsulates access to input code.
# Reads an assembly language command, parses it,
# and provides access to the command's components (fields
# and symbols). Also removes white space and comments.


class Parser:
    # Opens file at file_path and prepares to parse it
    def __init__(self, path: str) -> None:
        # Open file
        self.path = path
        self.input_file = open(self.path, 'r')

        # Read file
        self.lines = self.input_file.readlines()
        # Line when reading file
        self.index = -1
        # Line index, not including empty spaces
        self.line_index = 0
        self.line = None
        self.symbol_table = SymbolTable()

        print('Opened file:', self.path)
        print('Fetching L commands...')
        self.fetch_l_commands()

    def __str__(self) -> str:
        return self.line

    def __len__(self) -> int:
        return len(self.line)

    def has_more_commands(self) -> bool:
        return self.index + 1 < len(self.lines)

    # Reads next command from input and sets it to current command.
    # Called only if has_more_commands is true.
    # Initially, there is no current command.
    def advance(self) -> str:
        self.line = self.get_next_line()

        # Skip empty lines
        while len(self.line) == 0:
            self.line = self.get_next_line()

        if self.command_type() != L_COMMAND:
            self.line_index += 1

        return self.line

    # Advances file reader.
    # Cleans line but does not ignore empty lines.
    def get_next_line(self) -> str:
        self.index += 1
        dirty_line = self.lines[self.index]

        # Remove white space and comments
        clean_line = dirty_line.split('//')[0].strip()

        return clean_line

    # Returns type of current command.
    def command_type(self) -> Literal:
        if self.line[0] == '@':
            return A_COMMAND
        elif self.line[0] == '(':
            return L_COMMAND
        else:
            return C_COMMAND

    def fetch_l_commands(self) -> None:
        i = 0
        for line in self.lines:
            clean_line = line.split('//')[0].strip()
            if len(clean_line) > 0:
                if clean_line[0] == '(':
                    address_only = clean_line[1:-1]
                    if not address_only.isdigit():
                        self.symbol_table.add_entry(
                            symbol=address_only, address=i)
                else:
                    i += 1

    # Returns symbol or decimal of current command @Xxx or (Xxx).
    # Called only if command_type is A_COMMAND or L_COMMAND
    def get_symbol(self) -> str:
        # Check if symbol
        address_dec = 0
        c_type = self.command_type()
        address_only = ''

        if c_type == L_COMMAND:
            address_only = self.line[1:-1]
        else:  # A_COMMAND
            address_only = self.line[1:]

        if address_only.isdigit():
            address_dec = int(address_only)
        else:
            if self.symbol_table.contains(address_only):
                address_dec = self.symbol_table.get_address(address_only)
            else:
                if c_type == L_COMMAND:
                    address_dec = self.symbol_table.add_entry(
                        symbol=address_only, address=self.line_index)
                else:
                    address_dec = self.symbol_table.add_entry(
                        symbol=address_only)

        # Returns binary conversion of address_dec w/0 '0b' at beginning
        return format(int(address_dec), '015b')

    # Returns dest mnemonic. Called only if command_type is C_COMMAND
    def get_dest(self) -> str:
        if '=' in self.line:
            return self.line.split('=')[0]

        return ''

    def get_comp(self) -> str:
        comp = self.line
        temp = comp.split('=')
        if len(temp) > 1:
            comp = temp[1]

        temp = comp.split(';')
        if len(temp) > 0:
            comp = temp[0]

        return comp

    # Returns jump mnemonic. Called only if command_type is C_COMMAND
    def get_jump(self) -> str:
        if ';' in self.line:
            return self.line.split(';')[1]

        return ''

    def __del__(self) -> None:
        print(self.line_index, "lines translated.")
        self.input_file.close()
        print("Closed file:", self.path)
