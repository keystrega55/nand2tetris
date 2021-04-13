# Creates dictionary of symbol labels
# and their corresponding numeric addresses
class SymbolTable:
    def __init__(self) -> None:
        self.symbol_dict = self.base_table()
        self.ram_position = 16  # 0-15 have preset values

    def get_address(self, symbol: str) -> str:
        address = self.symbol_dict[symbol]
        if address is None:
            return ''

        return self.symbol_dict[symbol]

    def contains(self, symbol: str) -> bool:
        return symbol in self.symbol_dict

    def add_entry(self, symbol: str, address: str = None) -> str:
        if self.contains(symbol):
            return self.get_address(symbol)

        if address is None:
            address = -1
            if self.contains(symbol):
                address = self.symbol_dict[symbol]
            if address == -1:
                address = self.ram_position
                self.ram_position += 1

        self.symbol_dict[symbol] = address
        return self.get_address(symbol)

    def base_table(self):  # 15-bit addresses, 32K locations
        return {
            'SP': '0',
            'LCL': '1',
            'ARG': '2',
            'THIS': '3',
            'THAT': '4',
            'R0': '0',
            'R1': '1',
            'R2': '2',
            'R3': '3',
            'R4': '4',
            'R5': '5',
            'R6': '6',
            'R7': '7',
            'R8': '8',
            'R9': '9',
            'R10': '10',
            'R11': '11',
            'R12': '12',
            'R13': '13',
            'R14': '14',
            'R15': '15',
            'SCREEN': '16384',
            'KBD': '24576',
        }
