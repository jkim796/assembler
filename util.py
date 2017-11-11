import re
import tables

### TODO: Error message when R-type, S-type are used wrong ###

nameTable = {}
labelTable = {}
wordTable = {}

# returns a list of lines, delimited by the \n character
def readFrom(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    return lines

def writeTo(path, hex):
    with open(path, 'w') as f:
        f.write(hex)

# This creates a dictionary of .NAME names and values. For example, .NAME IOBASE=0xF0000000 is parsed, then IOBASE and 0xF0000000 pair is put in util.nameTable
def updateNameTable(line):
    nameRE = re.compile('\w+')
    names = nameRE.findall(line)
    name = names[1]
    value = names[2].lower()
    nameTable[name] = value

# equivalent of parseName. Don't really understand what this does, and haven't seen any examples yet...
def parseWord(line):
    pass

# Will figure out what this actually does later
def parseOrig(line):
    pass

# Returns true if the current line is a directive (like .NAME). False otherwise.
def isDirective(line):
    if line.startswith('.'):
        return True
    else:
        return False

# Will expand more on this later. For now, only checks if the beginning of a line is a comment.
def isComment(line):
    if line.startswith(';'):
        return True
    else:
        return False

# Returns true if current line is a label definition (like MainLoop:). False otherwise.
def isLabelDef(line):
    if line.endswith(':'):
        return True
    else:
        return False

# Determines whether given instruction is a pseudo instruction
def isPseudoInstr(line):
    wordsRE = re.compile('\w+')
    opcode = wordsRE.findall(line)[0].lower()
    if opcode in tables.pseudoTable:
        return True
    else:
        return False

# Replaces pseudo instruction with regular instruction
def replacePseudoInstr(line):
    wordsRE = re.compile('\w+')
    words = wordsRE.findall(line)
    opcode = words[0].lower()
    replacedLine = []
    hasMoreLines = False
    if opcode == 'br':
        imm = words[-1]
        rest = 's0' + ', ' + 's0' + ', ' + imm
        replacedLine.append(tables.pseudoTable[opcode] + ' ' + rest)
    elif opcode == 'not':
        rd = words[-2]
        rs = words[-1]
        rest = rd + ', ' + rs + ', ' + rs
        replacedLine.append(tables.pseudoTable[opcode] + ' ' + rest)
    elif opcode == 'ble':
        rs1 = words[-3]
        rs2 = words[-2]
        imm = words[-1]
        rest = 's0' + ', ' + rs1 + ', ' + rs2
        replacedLine.append(tables.pseudoTable[opcode] + ' ' + rest)
        rest = 's0' + ', ' + imm
        replacedLine.append('bnez' + ' ' + rest)
        hasMoreLines = True
    elif opcode == 'bge':
        rs1 = words[-3]
        rs2 = words[-2]
        imm = words[-1]
        rest = 's0' + ', ' + rs1 + ', ' + rs2
        replacedLine.append(tables.pseudoTable[opcode] + ' ' + rest)
        rest = 's0' + ', ' + imm
        replacedLine.append('bnez' + ' ' + rest)
        hasMoreLines = True
    elif opcode == 'call':
        rs1 = words[-1]
        imm = words[-2]
        rest = 'ra' + ', ' + imm + '(' + rs1 + ')'
        replacedLine.append(tables.pseudoTable[opcode] + ' ' + rest)
    elif opcode == 'ret':
        rest = 'r9' + ', ' + '0' + '(' + 'ra' + ')'
        replacedLine.append(tables.pseudoTable[opcode] + ' ' + rest)
    elif opcode == 'jmp':
        imm = words[-2]
        rs1 = words[-1]
        rest = 'r9' + ', ' + imm + '(' + rs1 + ')'
        replacedLine.append(tables.pseudoTable[opcode] + ' ' + rest)
    return replacedLine, hasMoreLines
    
# This puts label and the location it was defined in a table. Location is in hex string, based on the 0x40 byte addressable address (instead of the 2-bit shifted address)
def updateLabelTable(label, origOffset, origAddr):
    location = '0x' + zext(hex(int(origAddr, 16) + 4 * origOffset), 8)
    # or this: location = hex(0x10 + offsetFromORIG)[2:0]
    labelTable[label] = location
    
# Given a hex, zero extends it to 4 hexademical places
def zext(imm, size):
    #if len(imm) > size:
        #raise Exception('Imm size too big!')
    imm = imm[2:] # strip 0x in front
    zeros = (size - len(imm)) * '0'
    return zeros + imm

# Given a hex, trims it down to given size
def trim(imm, size):
    #if len(imm) < size:
        #raise Exception('Imm size too small to be trimmed!')
    imm = imm[2:]
    # need to figure out which part to trim out...for now just trim out the 4 MSB's
    imm = imm[-4:]
    return imm

def format(imm, size):
    if len(imm[2:]) > size:
        return trim(imm, size)
    elif len(imm[2:]) < size:
        return zext(imm, size)
    else:
        return imm[2:]

# Returns true if given input is a decimal number string. False otherwise.
def isDecimalOffset(imm):
    decimalRE = re.compile('[0-9]+')
    potential = decimalRE.match(imm)
    if potential is None: # if input starts with a char, we know for sure this is not a decimal number string.
        return False
    else: # even if input starts with a decimal number, it could still contain chars so we need to check if the entire given input is a decimal number string.
        num = potential.group()
        if len(num) == len(imm):
            return True
        else:
            return False

# I don't think this function is useful
def parseDirective(line):
    directiveRE = re.compile('\w+') # this doesn't match the leading dot(.)
    directives = directiveRE.findall(line)
    directive = directives[0]
    if directive == 'NAME':
        updateNameTable(line)
    elif directive == 'ORIG':
        parseOrig(line)
    elif directive == 'WORD':
        parseWord(line)
    else:
        raise Exception('Not a valid assembler directive!')

# parses each line to opcode, registers, (and possibly labels)
def parseLine(line):
    lineArr = line.split(' ', 1)
    opcode = lineArr[0].lower()
    stripOpcode = lineArr[1]
    splitComma = stripOpcode.split(',')
    stripSplit = []
    for split in splitComma:
        stripSplit.append(split.strip().lower()) #get rid of whitespace if any
    #throw an error if it's not a valid opcode
    if opcode not in tables.opcodeTable:
        raise Exception('Invalid instruction opcode!')
    #then, based on which opcode it is,
    #look at how many registers it requires
    if isImmType(opcode) == False:
        #there are three registers
        regs = [stripSplit[0], stripSplit[1], stripSplit[2]]
        label = '000000000000' #don't care what this is
    else:
        #its either one or two registers
        if opcode == 'mvhi' or opcode == 'bltz' or opcode == 'bltez' or opcode == 'bnez' or opcode == 'bgtez' or opcode == 'bgtz':
            #its one register
            regs = [stripSplit[0]]
            label = stripSplit[1]
        else:
            #its two registers
            if opcode == 'jal' or opcode == 'lw' or opcode == 'sw':
                beginIndex = stripSplit[1].find("(")
                endIndex = stripSplit[1].find(")")
                regs = [stripSplit[0], stripSplit[1][beginIndex+1:endIndex]]
                label = stripSplit[1][:beginIndex]
            else:
                regs = [stripSplit[0], stripSplit[1]]
                label = stripSplit[2]

    #check validity of registers
    for reg in regs:
        if reg not in tables.regTable:
            print reg
            raise Exception('Invalid register(s)!')

    #check label validity partially
    # this always throws an erro so im commenting it out for now
    # if(label.startswith('0x')):
    #     #make sure its valid hex
    #     hexcheck = re.match('[0-9a-fA-F]{1,4}', label[1:])
    #     if hexcheck == None:
    #         raise Exception('Invalid Immediate value!')

    return opcode, regs, label

# translate opcode to hex
def transOpcode(opcode):
    return tables.opcodeTable[opcode]

# translate reg to hex
def transReg(reg):
    return tables.regTable[reg]

# For now, there's no checking on if there are too many or not enough registers (there should only be 2 or 3 registers)
def transRegs(regs):
    hex = ''
    for reg in regs:
        hex += transReg(reg)
    return hex

# Returns true if instruction is Immediate type, otherwise false. In case of false, fill in 0x000 in the translated instruction. 
def isImmType(opcode):
    if opcode.endswith('i') or opcode.startswith('b') or opcode == 'jal' or opcode == 'lw' or opcode == 'sw':
        return True
    else:
        return False

# calculates the Imm value from label
def calcLabelOffset(labelDefAddr, currAddr):
    labelDefAddr = int(labelDefAddr, 16)
    currAddr = int(currAddr, 16)
    if labelDefAddr > currAddr:
        return hex((labelDefAddr - (currAddr + 4)) / 4)
    elif labelDefAddr < currAddr:
        return hex(((labelDefAddr - (currAddr + 4)) / 4) & 0xffff)
