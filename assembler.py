import sys,os
import util

header = """WIDTH=32;
DEPTH=2048;
ADDRESS_RADIX=HEX;
DATA_RADIX=HEX;
CONTENT BEGIN"""

def main(assFile):
    lines = util.readFrom(assFile)

    origOffset = 0
    updatedLines = []
    ##################
    ### first pass ###
    ##################
    for line in lines:
        line = line.strip()
        if util.isComment(line) or line == '':
            continue
        elif util.isDirective(line):
            directive = line[:5]
            if directive == '.ORIG' or directive == '.orig':
                origOffset = 0 # in case .ORIG is used twice or more
                if '0x' in line:
                    addrIndex = line.index('0x')
                    origAddr = util.zext(line[addrIndex:], 8)                    
                else:
                    addrIndex = '0x' + line.split()[-1]
                    origAddr = util.zext(addrIndex, 8)
            updatedLines.append(line)
            # could update nameTable here...
        else:
            if util.isLabelDef(line):
                util.updateLabelTable(line[:-1], origOffset, origAddr) # just the label (without the :)
                continue
            elif util.isPseudoInstr(line):
                replacedLine, hasMoreLines = util.replacePseudoInstr(line)
                for l in replacedLine:
                    updatedLines.append(l)
                if hasMoreLines:
                    origOffset += 1
            updatedLines.append(line)
            origOffset += 1

    ###################            
    ### second pass ###
    ###################
    mifComment = '-- @ '
    origOffset = 0
    hexLine = ''.join(header) + '\n'
    for line in updatedLines:
        if ';' in line:
            line = line[:line.index(';')]
        line = line.strip()
        if util.isComment(line) or line == '':
            continue
        elif util.isDirective(line):
            #util.parseDirective(line)
            directive = line[:5]
            if directive == '.ORIG' or directive == '.orig':
                origOffset = 0
                if '0x' in line:
                    addrIndex = line.index('0x')
                    origAddr = util.format(line[addrIndex:], 8)                    
                else:
                    addrIndex = '0x' + line.split()[-1]
                    origAddr = util.format(addrIndex, 8)
            elif directive == '.NAME' or directive == '.name':
                util.updateNameTable(line)
            elif directive == '.WORD' or directive == '.word':
                pass
            else:
                raise Exception('Invalid directive!') #only three valid directives
        elif util.isLabelDef(line):
            continue
        else:
            opcode, regs, label = util.parseLine(line)
            opHex = util.transOpcode(opcode)
            if opcode == 'sw': # sw is the ONLY I-type instruction that has RS2 and RS1 backwards
                regs = regs[::-1]
            regsHex= util.transRegs(regs)
            if len(regs) == 1: # cases like mvhi, beqz...
                regsHex += '0'
                
            currAddr = '0x' + util.format(hex(int(origAddr, 16) + 4 * origOffset), 8)
            a32Addr = mifComment + ' ' + currAddr + ' : ' + line + '\n'
            mifAddr = util.format(hex((int(origAddr, 16) + 4 * origOffset) / 4), 8)

            if util.isImmType(opcode): # if I-type instruction
                if label.startswith('0x'):
                    imm = util.zext(label, 4)
                elif util.isDecimalOffset(label):
                    imm = util.zext(hex(int(label)), 4)
                else:
                    if label in util.nameTable:
                        imm = util.nameTable[label]
                        if opcode == 'mvhi': # mvhi takes the 4 MSBs
                            if len(imm[2:]) < 4: # cases like .NAME STUFF=0x234
                                imm = (4 - len(imm[2:])) * '0' + imm
                            else:
                                imm = imm[2:6] # cases like .NAME STUFF=0xdf00000000
                        else:
                            imm = util.format(imm, 4)
                    elif label in util.labelTable:
                        # we need to calculate address offset
                        labelDefAddr = util.labelTable[label] # this is the byte address
                        #currAddr = hex(int(origAddr, 16) + 4 * origOffset)
                        imm = util.calcLabelOffset(labelDefAddr, currAddr)
                        imm = util.format(imm, 4)
                        print('labelAddr: ', labelDefAddr)
                        print('currAddr: ', currAddr)
                        print('imm: ', imm)
                    elif label in util.wordTable:
                        # not sure if wordTable (and .WORD directive) is even going to be used...
                        pass
                    else:
                        raise Exception('label not defined!')
            else: # if R-type instruction
                imm = '000'
            origOffset += 1
            transLine = mifAddr + ' : ' + regsHex + imm + opHex + ';\n'
            hexLine += a32Addr + transLine
    print('labelTable: ', util.labelTable)
    print('nameTable: ', util.nameTable)
    #print(hexLine)

    filename, extension = os.path.splitext(assFile)
    util.writeTo(filename + '.mif', hexLine)

    
if __name__ == '__main__':
    if len(sys.argv) is 1:
        raise Exception('Provide at least one file!')
    fileList = sys.argv[1:]
    for assFile in fileList:
        main(assFile)
