'''
There are two tables in thie file: 
1) opcodeTable - this holds mapping from opcode to hex
2) regTable - this holds mapping from register name to hex
'''

# opcode to hex mapping
opcodeTable = {
    # ALU-R 
    'add' : '00',
    'sub' : '10',
    'and' : '40',
    'or' : '50',
    'xor' : '60',
    'nand' : 'c0',    
    'nor' : 'd0',    
    'xnor' : 'e0',

    # ALU-I
    'addi' : '08',
    'subi' : '18',
    'andi' : '48',
    'ori' : '58',
    'xori' : '68',
    'nandi' : 'c8',
    'nori' : 'd8',
    'xnori' : 'e8',
    'mvhi' : 'b8',

    # Load/Store
    'lw' : '09',
    'sw' : '05',

    # CMP-R
    'f' : '02',
    'eq' : '12',
    'lt' : '22',
    'lte' : '32',
    't' : '82',
    'ne' : '92',
    'gte' : 'a2',
    'gt' : 'b2',

    # CMP-I
    'fi' : '0a',
    'eqi' : '1a',
    'lti' : '2a',
    'ltei' : '3a',
    'ti' : '8a',
    'nei' : '9a',
    'gtei' : 'aa',
    'gti' : 'ba',

    # Branch
    'bf' : '06',
    'beq' : '16',
    'blt' : '26',
    'blte' : '36',
    'beqz' : '56',
    'bltz' : '66',
    'bltez' : '76',
    
    'bt' : '86',
    'bne' : '96',
    'bgte' : 'a6',
    'bgt' : 'b6',
    'bnez' : 'd6',
    'bgtez' : 'e6',
    'bgtz' : 'f6',
    
    'jal' : '0b'
}

# register to hex mapping
regTable = {
    'a0' : '0',
    'a1' : '1',
    'a2' : '2',
    'a3' : '3',
    't0' : '4',
    't1' : '5',
    's0' : '6',
    's1' : '7',
    's2' : '8',

    # R9 - R11 are reserved for assembler and system
    'r9' : '9',
    'r10': 'a',
    'r11': 'b',
    
    'gp' : 'c',
    'fp' : 'd',
    'sp' : 'e',
    'ra' : 'f'
}

# pseudo instruction table
pseudoTable = {
    'br' : 'beq',
    'not' : 'nand',
    'ble' : 'lte',
    'bge' : 'gte',
    'call' : 'jal',
    'ret' : 'jal',
    'jmp' : 'jal'
}
