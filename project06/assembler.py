def main():
    import sys
    from parsr import Parser, A_COMMAND, C_COMMAND, L_COMMAND
    from writer import Writer
    from translator import Translator
    from symbol_table import SymbolTable

    # Get arguments
    arguments = sys.argv[1:]
    path = arguments[0]

    # Load files
    # Check input file extension
    assert '.asm' in path, 'File extension must be .asm'

    # Open input file
    asm_file = Parser(path)

    # Create/open output file
    hack_file_path = path.replace('.asm', '.hack')
    hack_file = Writer(hack_file_path)

    translator = Translator()

    while asm_file.has_more_commands():
        line = asm_file.advance()

        # Determine instruction type
        command_type = asm_file.command_type()

        if command_type == A_COMMAND:
            address = asm_file.get_symbol()

            hack_file.write_line(translator.construct_a_instruction(address))

        elif command_type == C_COMMAND:

            asm_comp = asm_file.get_comp()
            asm_dest = asm_file.get_dest()
            asm_jump = asm_file.get_jump()

            bin_comp = translator.translate_comp(asm_comp)
            bin_dest = translator.translate_dest(asm_dest)
            bin_jump = translator.translate_jump(asm_jump)

            hack_file.write_line(translator.construct_c_instruction(
                bin_comp, bin_dest, bin_jump))

        elif command_type == L_COMMAND:
            address = asm_file.get_symbol()


if __name__ == '__main__':
    main()
