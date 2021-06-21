import sys
from pathlib import Path
import Parser
import CodeWriter


class VMTranslator():
    def __init__(self) -> None:
        self.parser = None
        self.code_writer = None
        self.input_path_is_dir = None
        self.vm_files_count = 0
        self.asm_file = None
        self.has_boostrap = False

    def set_input_output_files(self, vm_file) -> None:
        self.parser = Parser.Parser(vm_file)

        if self.input_path_is_dir:
            asm_file = self.asm_file.with_suffix('.asm')
        else:
            asm_file = vm_file.with_suffix('.asm')

        self.code_writer = CodeWriter.CodeWriter(asm_file)

    def write_bootstrap(self) -> None:
        if self.input_path_is_dir and self.vm_files_count > 1:
            self.code_writer.write_bootstrap()
            self.code_writer.write_line('')
            self.has_boostrap = True

    def translate(self) -> None:
        if not self.has_boostrap:
            self.write_bootstrap()

        while self.parser.has_more_commands():
            self.parser.advance()
            if self.parser.command_type() == 'C_ARITHMETIC':
                self.code_writer.write_arithmetic(self.parser.command())
            elif self.parser.command_type() == 'C_PUSH':
                self.code_writer.write_push(
                    self.parser.arg1(), self.parser.arg2())
            elif self.parser.command_type() == 'C_POP':
                self.code_writer.write_pop(
                    self.parser.arg1(), self.parser.arg2())
            elif self.parser.command_type() == 'C_LABEL':
                self.code_writer.write_label(self.parser.arg1())
            elif self.parser.command_type() == 'C_IF':
                self.code_writer.write_if(self.parser.arg1())
            elif self.parser.command_type() == 'C_GOTO':
                self.code_writer.write_goto(self.parser.arg1())
            elif self.parser.command_type() == 'C_FUNCTION':
                self.code_writer.write_function(
                    self.parser.arg1(), self.parser.arg2())
            elif self.parser.command_type() == 'C_RETURN':
                self.code_writer.write_return()
            elif self.parser.command_type() == 'C_CALL':
                self.code_writer.write_call(
                    self.parser.arg1(), self.parser.arg2())
            else:
                continue

            self.code_writer.write_line('')


def main() -> None:
    input = sys.argv[1]
    file_path = Path(input)
    input_is_dir = Path.is_dir(file_path)

    if input_is_dir:
        vm_files = []
        for f in Path.iterdir(file_path):
            if f.name.endswith('.vm'):
                vm_files.append(f)
    else:
        vm_files = [file_path]

    vm_translator = VMTranslator()
    vm_translator.input_path_is_dir = input_is_dir
    vm_translator.vm_files_count = len(vm_files)

    child_path = file_path.joinpath(f'{file_path.stem}')
    vm_translator.asm_file = child_path

    for file in vm_files:
        vm_translator.set_input_output_files(file)
        vm_translator.translate()


if __name__ == '__main__':
    main()
