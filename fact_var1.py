# calculate factorial(n) = (1*2*3*4*5*...*n)
# version 1 with loop
n = 120000
fact = 1
for c in range(n):
    fact = fact * (c+1)
# calculate horizontal checksum
checksum = 0
for digit in str(fact):
    checksum += int(digit)
# print
print(checksum)
