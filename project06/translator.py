# Translates Hack assembly language mnemonics into binary code
class Translator:
    # Returns 3-bit binary code of dest mnemonic
    def translate_dest(self, mnemonic: str) -> str:
        ddd = ['0'] * 3
        if mnemonic is None:
            return ''.join(ddd)
        if 'A' in mnemonic:
            ddd[0] = '1'
        if 'D' in mnemonic:
            ddd[1] = '1'
        if 'M' in mnemonic:
            ddd[2] = '1'

        return ''.join(ddd)

    def translate_comp(self, mnemonic: str) -> str:
        comp_dict = {
            '0': '101010',
            '1': '111111',
            '-1': '111010',
            'D': '001100',
            'A': '110000',
            '!D': '001101',
            '!A': '110001',
            '-D': '001111',
            '-A': '110011',
            'D+1': '011111',
            'A+1': '110111',
            'D-1': '001110',
            'A-1': '110010',
            'D+A': '000010',
            'D-A': '010011',
            'A-D': '000111',
            'D&A': '000000',
            'D|A': '010101',
        }

        a_bit = '0'
        if 'M' in mnemonic:
            a_bit = '1'
            mnemonic = mnemonic.replace('M', 'A')

        c_bit = comp_dict.get(mnemonic, '000000')

        return a_bit + c_bit

    def translate_jump(self, mnemonic: str) -> str:
        jump_dict = {
            'JGT': '001',
            'JEQ': '010',
            'JGE': '011',
            'JLT': '100',
            'JNE': '101',
            'JLE': '110',
            'JMP': '111',
        }

        return jump_dict.get(mnemonic, '000')

    def construct_a_instruction(self, address: str) -> str:
        return '0' + address

    def construct_c_instruction(self, comp: str, dest: str, jump: str) -> str:
        return '111' + comp + dest + jump
