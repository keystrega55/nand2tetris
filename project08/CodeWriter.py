from pathlib import Path
from typing import List


class CodeWriter:
    def __init__(self, asm_file) -> None:
        self.out_file = asm_file
        self.out_file_name = Path(asm_file).stem

        # counters for Boolean comparisons
        self.eq_count = 0
        self.gt_count = 0
        self.lt_count = 0

        self.call_count = 0
        self.function_name = None  # for function labels

        self.addresses = self.address_dict()

    def write_push(self, segment: str, index: str) -> None:
        self.write_line(f'// push {segment} {index}')
        if segment == 'constant':  # check
            self.write_lines(
                [
                    f'@{index}',
                    'D=A',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'M=M+1'
                ]
            )
        elif segment == 'temp':  # check
            self.write_lines(
                [
                    f'@{index}',
                    'D=A',
                    f'@{self.addresses.get(segment)}',
                    'A=D+A',
                    'D=M',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'M=M+1'
                ]
            )
        elif segment == 'pointer':  # check - all new
            symbol = 'THIS' if index == '0' else 'THAT'
            self.write_lines(
                [
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    f'@{symbol}',
                    'M=D'
                ]
            )
        elif segment == 'static':  # check - all new
            self.write_lines(
                [
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    f'@{self.out_file_name}.{index}',
                    'M=D'
                ]
            )
        else:  # check
            self.write_lines(
                [
                    f'@{index}',
                    'D=A',
                    f'@{self.addresses.get(segment)}',
                    'A=D+M',
                    'D=M',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'M=M+1'
                ]
            )

    def write_pop(self, segment: str, index: str) -> None:
        self.write_line(f'// pop {segment} {index}')  # for debugging
        if segment == 'temp':
            self.write_lines(
                [
                    f'@{index}',
                    'D=A',
                    f'@{self.addresses.get(segment)}'
                    'D=D+A',
                    '@frame',
                    'M=D',
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    '@frame',
                    'A=M',
                    'M=D'
                ]
            )
        elif segment == 'pointer':
            # debug if needed -> compare str to int ?
            symbol = 'THAT' if index == '1' else 'THIS'
            self.write_lines(
                [
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    f'@{symbol}',
                    'M=D'
                ]
            )
        elif segment == 'static':
            self.write_lines(
                [
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    f'@{self.out_file_name}.{index}',
                    'M=D'
                ]
            )
        else:
            self.write_lines(
                [
                    f'@{index}',
                    'D=A',
                    f'@{self.addresses.get(segment)}',
                    'D=D+M',
                    '@frame',
                    'M=D',
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    '@frame',
                    'A=M',
                    'M=D'
                ]
            )

    def write_arithmetic(self, operation: str) -> None:
        self.write_line(f'// {operation}')  # For debugging

        if operation == 'add':
            self.write_add()
        elif operation == 'sub':
            self.write_sub()
        elif operation == 'and':
            self.write_and()
        elif operation == 'or':
            self.write_or()
        elif operation == 'neg':
            self.write_neg()
        elif operation == 'not':
            self.write_not()
        elif operation == 'eq':
            self.write_eq()
            self.eq_count += 1
        elif operation == 'gt':
            self.write_gt()
            self.gt_count += 1
        elif operation == 'lt':
            self.write_lt()
            self.lt_count += 1
        else:
            self.raise_unknown_error(operation)

    def write_add(self) -> None:  # check
        self.write_lines(
            [
                '@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'M=D+M',
                '@SP',
                'M=M+1'
            ]
        )

    def write_sub(self) -> None:  # check
        self.write_lines(
            [
                '@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'M=M-D',
                '@SP',
                'M=M+1'
            ]
        )

    def write_neg(self) -> None:  # check
        self.write_lines(
            [
                '@SP',
                'AM=M-1',
                'D=-M'  # new - M=-M
                'M=D',  # new
                '@SP',
                'M=M+1'
            ]
        )

    def write_and(self) -> None:
        self.write_lines(
            [
                '@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'M=D&M',
                '@SP',
                'M=M+1'
            ]
        )

    def write_or(self) -> None:
        self.write_lines(
            [
                '@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'M=D|M',
                '@SP',
                'M=M+1'
            ]
        )

    def write_not(self) -> None:
        self.write_lines(
            [
                '@SP',
                'M=M-1',
                'A=M',
                'D=!M',  # new - M=!M
                'M=D',  # new
                '@SP',
                'M=M+1'
            ]
        )

    def write_eq(self) -> None:  # check
        self.write_lines(
            [
                '@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'D=D-M',
                f'@eq{self.eq_count}',
                'D;JEQ',
                'D=0',
                f'@eq.end{self.eq_count}',
                '0;JEQ',  # new - 0;JMP
                f'(eq{self.eq_count})',
                'D=-1',
                f'(eq.end{self.eq_count})',
                '@SP',
                'A=M',
                'M=D',
                '@SP',
                'M=M+1'
            ]
        )
        self.eq_count += 1

    def write_gt(self) -> None:  # check
        self.write_lines(
            [
                '@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'D=D-M',
                f'@gt{self.gt_count}',
                'D;JGT',  # new - D;JLT
                'D=0',
                f'@gt.end{self.gt_count}',
                '0;JEQ',  # new - 0;JMP
                f'(gt{self.gt_count})',
                'D=-1',
                f'(gt.end{self.gt_count})',
                '@SP',
                'A=M',
                'M=D',
                '@SP',
                'M=M+1'
            ]
        )
        self.gt_count += 1

    def write_lt(self) -> None:  # check
        self.write_lines(
            [
                '@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'D=M-D',  # new - D=D-M
                f'@lt{self.lt_count}',
                'D;JLT',  # new - D;JGT
                'D=0',
                f'@lt.end{self.lt_count}',
                '0;JEQ',  # new - 0;JMP
                f'(lt{self.lt_count})',
                'D=-1',
                f'(lt.end{self.lt_count})',
                '@SP',
                'A=M',
                'M=D',
                '@SP',
                'M=M+1'
            ]
        )
        self.lt_count += 1

    def create_label(self, label: str, function_type: str = None) -> str:  # debug if needed
        asm_label = ''
        if self.function_name is not None:
            asm_label += f'{self.function_name}${label}'
        else:
            asm_label += f'{label}'

        if function_type in ['if', 'goto']:
            return f'@{asm_label}'
        else:
            return f'({asm_label})'

    def write_label(self, label: str) -> None:
        self.write_line(f'// label {label}')
        self.write_line(f'{self.create_label(label)}')

    def write_goto(self, label: str) -> None:  # check
        self.write_line(f'// goto {label}')
        self.write_lines(
            [
                f"{self.create_label(label, 'goto')}",
                '0;JMP'
            ]
        )

    def write_if(self, label: str) -> None:  # check
        self.write_line(f'// if-goto {label}')
        self.write_lines(
            [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                f"{self.create_label(label, 'if')}",
                'D;JNE'
            ]
        )

    def write_function(self, function_name: str, num_locals: str) -> None:  # check
        self.function_name = function_name

        self.write_line(f'// function {function_name} {num_locals}')
        self.write_line(f'({function_name})')
        for i in range(num_locals):
            self.write_push('constant', '0')

        self.function_name = function_name

    def write_return(self) -> None:  # debug if needed
        self.write_line(f'// return')
        self.write_lines(
            [
                # endFrame = LCL
                '@LCL',
                'D=M',
                '@frame',
                'M=D',

                # retAddr = *(endFrame - 5)
                '@5',
                'D=D-A',
                'A=D',
                'D=M',
                '@return',
                'M=D',

                # *ARG = pop()
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                '@ARG',
                'A=M',
                'M=D',

                # SP = ARG + 1
                '@ARG',
                'D=M+1',
                '@SP',
                'M=D',

                # THAT = *(endFrame - 1)
                '@frame',
                'D=M',
                '@1',
                'D=D-A',
                # 'D=D-1',  # debug
                'A=D',
                'D=M',
                '@THAT',
                'M=D',

                # THIS = *(endFrame - 2)
                '@frame',
                'D=M',
                '@2',
                'D=D-A',
                'A=D',
                'D=M',
                '@THIS',
                'M=D',

                # ARG = *(endFrame - 3)
                '@frame',
                'D=M',
                '@3',
                'D=D-A',
                'A=D',
                'D=M',
                '@ARG',
                'M=D',

                # LCL = *(endFrame - 4)
                '@frame',
                'D=M',
                '@4',
                'D=D-A',
                'A=D',
                'D=M',
                '@LCL',
                'M=D',

                # goto retAddr
                '@return',
                'A=M',
                '0;JMP'
            ]
        )

    def write_call(self, function_name: str, num_args: int) -> None:  # check
        self.write_line(f'// call {function_name} {num_args}')
        self.write_lines(
            [
                # push return address
                f'@{function_name}$ret.{self.call_count}',
                'D=A',
                '@SP',
                'A=M',
                'M=D',
                '@SP',
                'M=M+1',

                # Push frame
                '@LCL',
                'D=M',
                '@SP',
                'A=M',
                'M=D',
                '@SP',
                'M=M+1',

                '@ARG',
                'D=M',
                '@SP',
                'A=M',
                'M=D',
                '@SP',
                'M=M+1',

                '@THIS',
                'D=M',
                '@SP',
                'A=M',
                'M=D',
                '@SP',
                'M=M+1',

                '@THAT',
                'D=M',
                '@SP',
                'A=M',
                'M=D',
                '@SP',
                'M=M+1',

                # ARG = SP - 5 - num_args
                'D=M',
                f'@{str(5 + num_args)}',
                'D=D-A',
                '@ARG',
                'M=D',

                # LCL = SP
                '@SP',
                'D=M',
                '@LCL',
                'M=D',

                # goto function_name
                f'@{function_name}',
                '0;JMP',

                # return address
                f'({function_name}$ret.{self.call_count})'
            ]
        )
        self.call_count += 1

    def write_bootstrap(self) -> None:
        self.write_lines(
            [
                '@256',
                'D=A',
                '@SP',
                'M=D'
            ]
        )
        self.write_call('Sys.init', 0)

    def address_dict(self) -> dict:
        return {
            'local': 'LCL',  # base address R1
            'argument': 'ARG',  # R2
            'this': 'THIS',  # R3
            'that': 'THAT',  # R4
            'pointer': '3',  # R3, R4
            'temp': '5',  # R5 - R12 (R13 - R15 are free)
            'static': '16',  # base addresses 16 - 255
        }

    def write_line(self, line: str) -> None:
        with open(self.out_file, 'a') as f:
            f.write(f'{line}\n')

    def write_lines(self, lines: List[str]) -> None:
        with open(self.out_file, 'a') as f:
            for line in lines:
                f.write(f'{line}\n')

    def push_D_to_stack(self) -> None:
        # Push D value to top of stack, increment @SP
        self.set_A_to_sp()
        self.write_line('M=D')  # Push D to stack
        self.increment_sp()

    def pop_stack(self) -> None:
        # Decrement @SP, pop top of stack to D
        self.write_lines(['@SP',
                          'AM=M-1'])

    def increment_sp(self) -> None:
        self.write_lines(['@SP',
                          'M=M+1'])

    def decrement_sp(self) -> None:
        self.write_lines(['@SP',
                          'M=M-1'])

    def set_A_to_sp(self) -> None:
        self.write_lines(['@SP',  # Get current stack pointer (SP)
                          'A=M'])  # Set address to current SP

    def raise_unknown_error(self, argument: str) -> ValueError:
        raise ValueError(f'{argument} is an invalid argument.')
