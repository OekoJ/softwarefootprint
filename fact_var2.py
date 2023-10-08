# calculate factorial(n) = (1+2+3+4+5+...+n)
# version 2 with math library
n = 120000
import math
fact = math.factorial(n)

# calculate horizontal checksum
checksum = 0
for digit in str(fact):
    checksum += int(digit)

# print
print(checksum)