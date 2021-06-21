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

    # load M[address] to D
    def write_push(self, segment: str, index: str) -> None:
        self.write_line(f'// push {segment} {index}')
        self.resolve_address(segment, index)
        if segment == 'constant':  # check
            self.write_line('D=A')
        else:
            self.write_line('D=M')
        self.push_D_to_stack()

    # load D to M[address]
    def write_pop(self, segment: str, index: str) -> None:
        self.write_line(f'// pop {segment} {index}')
        self.resolve_address(segment, index)
        self.write_lines(
            [
                'D=A',
                '@R13',  # store resolved address in R13
                'M=D'
            ]
        )
        self.pop_stack_to_D()
        self.write_lines(
            [
                '@R13',
                'A=M',
                'M=D'
            ]
        )

    def resolve_address(self, segment: str, index: int) -> None:
        address = self.addresses.get(segment)
        if segment == 'constant':
            self.write_line(f'@{str(index)}')
        elif segment == 'static':
            self.write_line(f'@{self.out_file_name}.{str(index)}')
        elif segment in ['pointer', 'temp']:
            self.write_line(f'@R{str(address + index)}')  # address type is int
        elif segment in ['local', 'argument', 'this', 'that']:
            self.write_lines(
                [
                    f'@{address}',
                    'D=M',
                    f'@{str(index)}',
                    'A=D+A'  # D is segment base
                ]
            )
        else:
            self.raise_unknown_error(segment)

    def write_arithmetic(self, operation: str) -> None:
        self.write_line(f'// {operation}')

        if operation not in ['neg', 'not']:  # binary operators
            self.pop_stack_to_D()
        self.decrement_sp()
        self.set_A_to_sp()

        if operation == 'add':  # arithmetic operators
            self.write_line('M=M+D')
        elif operation == 'sub':
            self.write_line('M=M-D')
        elif operation == 'and':
            self.write_line('M=M&D')
        elif operation == 'or':
            self.write_line('M=M|D')
        elif operation == 'neg':
            self.write_line('M=-M')
        elif operation == 'not':
            self.write_line('M=!M')
        elif operation == 'eq':  # Boolean operators
            self.write_eq()
        elif operation == 'gt':
            self.write_gt()
        elif operation == 'lt':
            self.write_lt()
        else:
            self.raise_unknown_error(operation)

        self.increment_sp()

    def write_eq(self) -> None:
        self.write_lines(
            [
                'D=M-D',
                f'@EQ.{self.eq_count}',
                'D;JEQ'
            ]
        )
        self.set_A_to_sp()
        self.write_lines(
            [
                'M=0',  # False
                f'@ENDEQ.{self.eq_count}',
                '0;JMP',
                f'(EQ.{self.eq_count})'
            ]
        )
        self.set_A_to_sp()
        self.write_lines(
            [
                'M=-1',  # True
                f'(ENDEQ.{self.eq_count})'
            ]
        )
        self.eq_count += 1

    def write_gt(self) -> None:
        self.write_lines(
            [
                'D=M-D',
                f'@GT.{self.gt_count}',
                'D;JGT'
            ]
        )
        self.set_A_to_sp()
        self.write_lines(
            [
                'M=0',  # False
                f'@ENDGT.{self.gt_count}',
                '0;JMP',
                f'(GT.{self.gt_count})'
            ]
        )
        self.set_A_to_sp()
        self.write_lines(
            [
                'M=-1',  # True
                f'(ENDGT.{self.gt_count})'
            ]
        )
        self.gt_count += 1

    def write_lt(self) -> None:
        self.write_lines(
            [
                'D=M-D',
                f'@LT.{self.lt_count}',
                'D;JLT'
            ]
        )
        self.set_A_to_sp()
        self.write_lines(
            [
                'M=0',  # False
                f'@ENDLT.{self.lt_count}',
                '0;JMP',
                f'(LT.{self.lt_count})'
            ]
        )
        self.set_A_to_sp()
        self.write_lines(
            [
                'M=-1',  # True
                f'(ENDLT.{self.lt_count})'
            ]
        )
        self.lt_count += 1

    def create_label(self, label: str, function_type: str = None) -> str:
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
        self.pop_stack_to_D()
        self.write_lines(
            [
                f"{self.create_label(label, 'if')}",
                'D;JNE'
            ]
        )

    def write_function(self, function_name: str, num_locals: int) -> None:  # check
        self.write_line(f'// function {function_name} {num_locals}')
        self.write_line(f'({function_name})')

        for i in range(num_locals):  # push constant 0 i times
            self.write_line('D=0')
            self.push_D_to_stack()

        self.function_name = function_name

    def write_return(self) -> None:  # debug if needed
        FRAME = 'R13'
        RET_ADDR = 'R14'

        self.write_line(f'// return')

        # FRAME = LCL
        self.write_lines(
            [
                '@LCL',
                'D=M',
                f'@{FRAME}',
                'M=D'
            ]
        )

        # RET = *(FRAME - 5)
        self.write_lines(
            [
                # f'@{FRAME}', # debug
                # 'D=M',  # debug - save start of frame
                '@5',
                'D=D-A',  # adjust address
                'A=D',  # prepare to load value at address
                'D=M',  # store value
                f'@{RET_ADDR}',
                'M=D'  # save value
            ]
        )

        # *ARG = pop()
        self.pop_stack_to_D()
        self.write_lines(
            [
                '@ARG',
                'A=M',
                'M=D'
            ]
        )

        # SP = ARG + 1
        self.write_lines(
            [
                '@ARG',
                'D=M',
                '@SP',
                'M=D+1'
            ]
        )

        # THAT = *(FRAME - 1)
        # THIS = *(FRAME - 2)
        # ARG = *(FRAME - 3)
        # LCL = *(FRAME - 4)
        offset = 1
        for address in ['@THAT', '@THIS', '@ARG', '@LCL']:
            self.write_lines(
                [
                    f'@{FRAME}',
                    'D=M',  # save start of frame
                    f'@{str(offset)}',
                    'D=D-A',  # adjust address
                    'A=D',  # prepare to load value at address
                    'D=M',  # store value
                    f'{address}',
                    'M=D'  # save value
                ]
            )
            offset += 1

        # goto RET_ADDR
        self.write_lines(
            [
                f'@{RET_ADDR}',
                'A=M',
                '0;JMP'
            ]
        )

    def write_call(self, function_name: str, num_args: int) -> None:  # check
        # unique return label
        RET_ADDR = f'{function_name}$Ret.{self.call_count}'

        self.write_line(f'// call {function_name} {num_args}')

        # push return address
        self.write_lines(
            [
                f'@{RET_ADDR}',
                'D=A'
            ]
        )
        self.push_D_to_stack()

        # push LCL, ARG, THIS, THAT
        for address in ['@LCL', '@ARG', '@THIS', '@THAT']:
            self.write_lines(
                [
                    f'{address}',
                    'D=M'
                ]
            )
            self.push_D_to_stack()

        # ARG = SP - (n - 5)
        self.write_lines(
            [
                '@SP',  # debug - remove if needed
                'D=M',  # debug - remove if needed
                f'@{str(num_args + 5)}',
                'D=D-A',
                '@ARG',
                'M=D'
            ]
        )

        # LCL = SP
        self.write_lines(
            [
                '@SP',
                'D=M',
                '@LCL',
                'M=D'
            ]
        )

        # goto f
        self.write_lines(
            [
                f'@{function_name}',
                '0;JMP'
            ]
        )

        self.write_line(f'({RET_ADDR})')  # (return_address)

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
            'pointer': 3,  # R3, R4
            'temp': 5,  # R5 - R12 (R13 - R15 are free)
            'static': 16,  # base addresses 16 - 255
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

    def pop_stack_to_D(self) -> None:
        # Decrement @SP, pop top of stack to D
        self.decrement_sp()
        self.write_lines(
            [
                'A=M',
                'D=M'
            ]
        )
        # self.write_lines( # more efficient
        #     [
        #         '@SP',
        #         'AM=M-1',
        #         'D=M'
        #     ]
        # )

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
