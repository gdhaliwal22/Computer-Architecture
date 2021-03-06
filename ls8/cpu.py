"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
MOD = 0b10100100
DIV = 0b10100011
ADD = 0b10100000
SUB = 0b10100001
PRA = 0b01001000
AND = 0b10101000
NOT = 0b01101001
OR = 0b10101010
XOR = 0b10101011
SHL = 0b10101100
SHR = 0b10101101
NOP = 0b00000000
LD = 0b10000011
ST = 0b10000100
CMP = 0b10100111

INC = 0b01100101
DEC = 0b01100110

PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001

CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.running = False
        self.fl = [0] * 8
        self.fl_lt = 5
        self.fl_gt = 6
        self.fl_equal = 7
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.stack_pointer = 7
        self.branchtable = {}
        self.reg[self.stack_pointer] = 0xF4
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[POP] = self.handle_POP
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[RET] = self.handle_RET

        # Sprint challenge: add CMP, JMP, JEQ and JNE
        self.branchtable[CMP] = self.handle_CMP
        self.branchtable[JMP] = self.handle_JMP
        self.branchtable[JEQ] = self.handle_JEQ
        self.branchtable[JNE] = self.handle_JNE


# Inside the CPU, there are two internal registers used for memory operations: the Memory Address Register (MAR) and the Memory Data Register (MDR). The MAR contains the address that is being read or written to. The MDR contains the data that was read or the data to write. You don't need to add the MAR or MDR to your CPU class, but they would make handy paramter names for ram_read() and ram_write(), if you wanted.


    def ram_read(self, mar):
        mdr = self.ram[mar]
        return mdr

    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        try:
            address = 0
            # open the file
            with open(sys.argv[1]) as f:
                # read every line
                for line in f:
                    # parse out comments
                    comment_split = line.strip().split("#")
                    # Cast number string to int
                    value = comment_split[0].strip()
                    # ignore blank lines
                    if value == "":
                        continue
                    instruction = int(value, 2)
                    # populate memory array
                    self.ram[address] = instruction
                    address += 1

        except:
            print("cant find file")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == CMP:
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl[self.fl_equal] = 1

            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl[self.fl_lt] = 1

            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl[self.fl_gt] = 1

            else:
                self.fl[self.fl_lt] = 0
                self.fl[self.fl_gt] = 0
                self.fl[self.fl_equal] = 0
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_LDI(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def handle_PRN(self, operand_a, _):
        print(self.reg[operand_a])

    def handle_ADD(self, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)

    def handle_MUL(self, operand_a, operand_b):
        self.alu(MUL, operand_a, operand_b)

    def handle_PUSH(self, operand_a, _):
        # you're moving down the stack, pushing the value into the next register. so F4 would go to F3
        self.reg[self.stack_pointer] -= 1
        self.ram[self.reg[self.stack_pointer]] = self.reg[operand_a]

    def handle_POP(self, operand_a, __):
        # you're moving up the stack, popping the value into the next register. so F4 would go to F3
        self.reg[operand_a] = self.ram[self.reg[self.stack_pointer]]
        self.reg[self.stack_pointer] += 1

    def handle_CALL(self, operand_a, _):
        return_addr = self.pc + 2
        self.reg[self.stack_pointer] -= 1
        self.ram[self.reg[self.stack_pointer]] = return_addr

        dest_addr = self.reg[operand_a]
        self.pc = dest_addr

    def handle_RET(self, _, __):
        register = 0
        self.handle_POP(register, __)
        self.pc = self.reg[register]

    def handle_JMP(self, register, _):
        self.pc = self.reg[register]

    def handle_JEQ(self, register, _):
        if self.fl[self.fl_equal] == 1:
            self.handle_JMP(register, _)
        else:
            self.pc += 2

    def handle_JNE(self, register, _):
        if self.fl[self.fl_equal] == 0:
            self.handle_JMP(register, _)
        else:
            self.pc += 2

    def handle_CMP(self, operand_a, operand_b):
        self.alu(CMP, operand_a, operand_b)

    def run(self):
        """Run the CPU."""

        self.running = True

        while self.running:
            opcode = self.ram_read(self.pc)

            inst_len = ((opcode & 0b11000000) >> 6) + 1
            # returns true if IR will modify pc
            incr_pc = (opcode & 0b10000) >> 4
            # print((opcode & 0b11000000), inst_len)

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if opcode == HLT:
                # exiting the system if HLT is encountered
                sys.exit(0)
            try:
                self.branchtable[opcode](operand_a, operand_b)
            except:
                print(f"Did not work")

            if not incr_pc == 1:
                self.pc += inst_len
