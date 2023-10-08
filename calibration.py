import math
import time
import psutil
from multiprocessing import Process

# python softwarefootprint_with_ref.py python > logs/calibration-n.log
# python calibration.py

inner_loop_nr = 1000
load_intesity = 40000
cpu_number = psutil.cpu_count() # number of CPUs in current machine
outer_loop_nr = cpu_number

def makeLoad(loop_nr):
    global load_intesity
    global inner_loop_nr
    b = 1
    while (b <= inner_loop_nr):
        erg = math.factorial(load_intesity)
        if (not (b % 100)):
            print("process " + str(loop_nr) + ": " + str(int(b/100)) + "/" + str(int(inner_loop_nr/100)) + (" finished" if (b == inner_loop_nr) else "") ) # print every 100th loop "process i: j/max"
        b += 1
    # print ("Finished Sub-Process: " + str(loop_nr))

if __name__ == '__main__':
    a = 1
    print ("Start " + str(outer_loop_nr) + " Sub-Processes")
    while (a <= outer_loop_nr):
        Process(target=makeLoad, args=[a]).start()
        a+=1
        time.sleep(0.001)
