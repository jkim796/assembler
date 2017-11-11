# Assembler
This is an assembler for a simple ISA. We're using Python 2.7. No particular reason.
Fixed-length, 32-bit instructions are supported. The microarchitecutre this assmelber supports includes word-addressable memory. It also includes 16 32-bit registers. 

To run:
$python assembler.py \<filename\>.a32

TODO:
1. Figure out how to handle .NAME bit trimming. Do we take the MSB or LSB? --> We use the LSB, except for the MVHI instruction

2. When calculating label offset, add the case were label being used is after the label defiiton. This should be trivial.

3. Trimming, zero extension functions are kind of messy. Need to make it consistent regarding the leading '0x'.

4. label offset --> right now, doing it by the byte addressable memory format, instead of word addressable. Do we need to change this?

5. Error handling

6. [DONE]print out memory address to file. This is trivial.

7. Handle pseudo intructions (like NOT, CALL). This shouldn't be too hard.
