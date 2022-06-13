################################################################
#
# softwarefootprint.py
#
# Description: Which footprint does a software cause? This script scans the process 
# statistics for the appearance of a given command name and adds up its CPU runtimes. 
# Based on this, the script calculates the energy consumption of the software on the 
# local computer and its greenhouse gas emissions.
#  
# install the missing packages by
# python -m pip install SomePackage
# 
# usage examples:
# python softwarefootprint.py CMDNAME [LOGTIME]
# CMDNAME is the name of the software which should be logged, e.g. firefox, lastteiber.py, stress
# example: python softwarefootprint.py stress
# LOGTIME is an optional value for the maximum logging time in seconds. Logging will automatically stop if logging time exceeds this value
# example: python softwarefootprint.py firefox 60
# 
# The software to be examined must be started in a second terminal window (or in some other way) 
# or must already be running. The program terminates as soon as CMDNAME no longer appears 
# in the process statistics or by cancelling the script with ctrl-c.
#
# example loads (python)
# python -c "import math;print (math.factorial(100000));"
# python -c "exec(\"f=1\nfor n in range(100000):\n\tf=f*(n+1)\nprint(f)\")"
# 
# example loads (linux):
# stress --cpu 2 --timeout 10s # run 2 cpu-cores with full load for 10 seconds
# 
################################################################
# 
# MIT License
# 
# Copyright (c) 2022 OekoJ
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################

import time
import sys
import os
import psutil

# This Computer (CHANGE THESE VALUES TO CURRENT MACHINE)
max_power = 11 # Watt maximum of current machine
cpu_number = psutil.cpu_count() # number of CPUs in current machine

# This power grid (CHANGE THESE VALUES TO YOUR LOCATION)
kgCO2_per_kWh = 0.311 # kgCO2/kWh German electricity mix 2020 https://www.eea.europa.eu/data-and-maps/daviz/co2-emission-intensity-9/download.table
gCO2_per_Ws = kgCO2_per_kWh / 3600 # gCO2/Ws

def get_load(cmdname):
    cpu = 0
    pids = ""
    pidsCpuTime = {} # pidsCpuTime[pid] = sumCpuTimes of this pid
    pidsCmdline = {} # pidsCmdline[pid] = Cmdline of this pid
    for proc in psutil.process_iter(['pid', 'cmdline', 'cpu_times', 'memory_info', 'cpu_percent']):
        if proc.info["cmdline"]:
            cmdline = " ".join(proc.info["cmdline"]) # packe alle elemente von cmdline in cmdline
            if ((str(cmdname) in cmdline) and (int(proc.info["pid"]) != thisPID)): # nicht dieses script selbst mitzaehlen
                cpu += float(proc.info["cpu_percent"])
                pidsCpuTime[str(proc.info["pid"])] = float(proc.info["cpu_times"].user) + float(proc.info["cpu_times"].system)
                pidsCmdline[str(proc.info["pid"])] = proc.info["cmdline"][0] # cmdline
                if (len(proc.info["cmdline"]) > 1):
                    pidsCmdline[str(proc.info["pid"])] += " " + proc.info["cmdline"][1]
                pids = pids + str(proc.info["pid"]) + "_"
    pids = pids[:-1] # remove last character
    return (cpu, pidsCpuTime, pids, pidsCmdline)

def get_energy_this(sumCpuTimes):
    energy = sumCpuTimes * max_power / cpu_number # energy consumption of the current computer in Ws (Watt * seconds)
    return energy

def print_results(sumRealTime,sumCpuPercent,sumCpuTimes):
    # sumCpuTimes = 4 * 60 * 60 # 4 CPUs * 1h
    print("Time\tCPU\t\tcpuTime")
    print("[s]\t[%*s]\t\t[s]")
    print("%.2f\t%.2f\t\t%s" % (sumRealTime,sumCpuPercent,sumCpuTimes))
    print("")
    energyconsumption = get_energy_this(sumCpuTimes)
    print("This Computer has "+str(cpu_number)+" CPUs or CPU-cores and a maximum power of "+str(max_power)+" Watt")
    print("energyconsumption = cpuTime / cpu_number * max_power")
    print("")
    print("Software Footprint of '"+sys.argv[1]+"' on this Computer:")
    print("%s\t%i\t%s" % ("Energy Consumption:", energyconsumption, "Ws"))
    print("%s\t%.3f\t%s" % ("Carbon emissions:", gCO2_per_Ws * energyconsumption, "gCO2e"))
    print("")
    

if __name__ == '__main__':
    if not (len(sys.argv) == 2 or len(sys.argv) == 3):
        print("usage: %s CMDNAME [LOGTIME]" % sys.argv[0])
        exit(2)
    if len(sys.argv) == 3 and sys.argv[2]: 
        logtime = sys.argv[2]
        try:
            logtime = float(logtime)
        except:
            print('LOGTIME must be a number (maximum log time in seconds)')   
            exit(2)
    else:
        logtime = 0
    thisPID = os.getpid()
    waiting = True
    sumCpuPercent = 0
    sumRealTime = 0
    lasttime = time.time()
    timediff = 0
    everyPidsCpuTime = {} # collect also PIDs that have already been stopped
    everyPidsCmdline = {} # collect cmdline also for PIDs that have already been stopped
    print("\nStart the Software '"+sys.argv[1]+"' from another Terminal Window!")
    print("Stop this logging script by ending '"+sys.argv[1]+"' or by pressing ctrl+c\n")
    try:
        while True:
            cpu, pidsCpuTime, pids, pidsCmdline = get_load(sys.argv[1])
            now = time.time()
            if pids and ((sumRealTime < logtime) or logtime == 0): # limit logging to logtime
                if waiting:
                    print("\n----------------------------------------------------------")
                    print("time\ttimestamp\t%CPU\tCPUTIME\tPIDs")
                    waiting = False
                everyPidsCpuTime.update(pidsCpuTime) 
                everyPidsCmdline.update(pidsCmdline)
                sumCpuTimes = sum(everyPidsCpuTime.values())
                print("%.2f\t%.2f\t%.2f\t%.2f\t%s" % (sumRealTime, now, cpu, sumCpuTimes, pids))
                timediff = (now - lasttime)
                sumCpuPercent += timediff * cpu      # %*s
                sumRealTime += timediff         # s
            elif waiting:
                print("waiting for '"+sys.argv[1]+"' to appear in process list")
            else:
                sumCpuTimes = sum(everyPidsCpuTime.values())
                print("%.2f\t%.2f\t%.2f\t%.2f\t%s" % (sumRealTime, now, cpu, sumCpuTimes, pids))
                print("----------------------------------------------------------")
                print("\nLoggig for Command '"+sys.argv[1]+"' finished")
                print("")
                print("PID\tcpuTime\tCommand")
                for pid in everyPidsCpuTime:
                    print("%s\t%.2f\t%s" % (pid, everyPidsCpuTime[pid], everyPidsCmdline[pid]))
                print("")
                print_results(sumRealTime,sumCpuPercent,sumCpuTimes)
                exit(1)
            lasttime = now
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nbreak")
        print("")
        print("PID\tcpuTime\tCommand")
        for pid in everyPidsCpuTime:
            print("%s\t%.2f\t%s" % (pid, everyPidsCpuTime[pid], everyPidsCmdline[pid]))
        print("")
        sumCpuTimes = sum(everyPidsCpuTime.values())
        print_results(sumRealTime,sumCpuPercent,sumCpuTimes)
        exit(0)
