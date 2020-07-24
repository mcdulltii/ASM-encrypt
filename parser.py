#!/usr/bin/python
import sys, argparse
import re
import random


class obfuscator():
    # Setup variables
    def __init__(self, filename, encoding):
        self.filename = filename
        self.encode_fmt = ['push', 'sub', 'xor']
        if len(encoding) != len(self.encode_fmt):
            raise ValueError(
                "Invalid encoding given!\nlen({}) != len({})".format(
                    encoding, self.encode_fmt))
        self.encoding = encoding
        self.registers = ['eax', 'ebx', 'ecx', 'edx']
        self.setup()
        self.reset()

    # Setup input_file list from file input
    def setup(self):
        # Replace \t chars and split by new line
        input_file = open(self.filename, 'r').read().replace('\t',
                                                             '').split('\n')
        # Remove spaces with length > 1 and remove comments
        input_file = [
            re.sub('  +', '',
                   i.split(';')[0]) for i in input_file if i
        ]
        self.input_file = input_file

    # Generate list of instructions to be obfuscated
    def reset(self):
        # Filter for strings in encode_fmt and output tuples with its original index
        to_encode = [(self.input_file.index(i), i) for i in self.input_file
                     if sum([j in i for j in self.encode_fmt])]
        # print(to_encode)
        self.encode = to_encode

    # To obfuscate push instructions (specifically with registers)
    def push(self, to_encode):
        # Obfuscate register push and output a tuple with original index
        to_encode = [(i[0], '\n'.join([
            'sub esp, 4', 'mov dword [esp], ' + i[1].split(' ')[1]
        ])) if len(i[1].split(' ')) == 2
                     and i[1].split(' ')[0] == self.encode_fmt[0] else i
                     for i in to_encode]
        # print(to_encode)
        return to_encode

    # To obfuscate sub instructions
    def sub(self, to_encode):
        # Extract sub and output a tuple with original index and random choice of unused register
        to_encode = [
            (i,
             random.choice(
                 [j for j in self.registers
                  if j != i[1].split(' ')[-1]])) if len(i[1].split(' ')) == 3
            and i[1].split(' ')[0] == self.encode_fmt[1] else i
            for i in to_encode
        ]
        # Obfuscate sub and output a tuple with original index
        to_encode = [(i[0][0], '\n'.join([
            'push ' + i[1],
            'mov ' + i[1] + ', ' + i[0][1].split(' ')[1].replace(',', ''),
            'xchg [' + i[0][1].split(' ')[1].replace(',', '') + '], ' + i[1],
            'pop ' + i[0][1].split(' ')[1].replace(',', '')
        ])) if type(i[0]) == tuple else i for i in to_encode]
        # print(to_encode)
        return to_encode

    # To obfuscate xor instructions (specifically with different registers)
    def xor(self, to_encode):
        # Filter for xor instructions for only those of different registers, and obfuscate using xor swap trick
        to_encode = [(i[0], '\n'.join([
            'xor ' + i[1].replace(',', '').split(' ')[1] + ', ' +
            i[1].split(' ')[2], 'xor ' + i[1].split(' ')[2] + ', ' +
            i[1].replace(',', '').split(' ')[1], 'xor ' +
            i[1].replace(',', '').split(' ')[1] + ', ' + i[1].split(' ')[2]
        ])) if i[1].split(' ')[1][:-1] != i[1].split(' ')[2]
                     and i[1].replace(',', '').split(' ')[1] in self.registers
                     and i[1].split(' ')[2] in self.registers else i
                     for i in to_encode]
        # print(to_encode)
        return to_encode

    # Start obfuscation
    def obfuscate(self):
        if_push, if_sub, if_xor = self.encoding

        # Replace push reg instructions
        if (if_push):
            self.encode = self.push(self.encode)

        # Replace sub instructions
        if (if_sub):
            self.encode = self.sub(self.encode)

        # Replace xor reg instructions
        if (if_xor):
            self.encode = self.xor(self.encode)

        # Replace original instructions with amended instructions into output
        output_file = '\n'.join([
            self.encode[[
                self.input_file.index(i) == j[0] for j in self.encode
            ].index(True)][1]
            if sum([self.input_file.index(i) == j[0]
                    for j in self.encode]) else i for i in self.input_file
        ])
        self.input_file = output_file.split('\n')
        self.reset()  # Regenerate to-be-encoded list
        return output_file

    # Reencode instructions using multiplier
    def repeat(self, multiplier):
        out = ""
        for i in range(multiplier):
            out = self.obfuscate()
        return out


def main(filename, out, encode_mul, encoding):
    obfuscation = obfuscator(filename, encoding)
    if encode_mul < 1:
        print("Invalid multiplier given!")
        sys.exit()
    else:
        obf = obfuscation.repeat(encode_mul)
    if out:
        open(out, 'w').write(obf)
        print("Outputted to {}".format(out))
    else:
        print(obf)
    return


parser = argparse.ArgumentParser(description='ASM Encryption')
parser.add_argument('--input', '-i', help='File input')
parser.add_argument('--output', '-o', help='File output')
parser.add_argument('--mul', '-m', help='Encoding multiplier', default=1)
parser.add_argument(
    '--encode', '-e', help='Allow: if_push, if_sub, if_xor', nargs='+')
args = parser.parse_args()
in_file = args.input
out_file = args.output
multiple = int(args.mul)
encode = args.encode

if __name__ == '__main__':
    if not args.encode:
        print("No encoding given!")
        parser.print_help()
    elif not in_file:
        print("No input file given!")
        parser.print_help()
    else:
        main(in_file, out_file, multiple, [int(i) for i in encode])
