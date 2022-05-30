# softwarefootprint
How much is the footprint of a piece of software? This script scans the process statistics for the appearance of a given command name and adds up its CPU runtimes. Based on this, the script calculates the energy consumption of the software on the local computer and its greenhouse gas emissions.

# usage examples:
python softwarefootprint.py CMDNAME [LOGTIME]
CMDNAME is the name of the software which should be logged, e.g. firefox, lastteiber.py, stress
example: python softwarefootprint.py stress
LOGTIME is an optional value for the maximum logging time in seconds. Logging will automatically stop if logging time exceeds this value
example: python softwarefootprint.py firefox 60

The software to be examined must be started in a second terminal window (or in some other way) 
or must already be running. The programme terminates as soon as CMDNAME no longer appears 
in the process statistics or by cancelling the script with ctrl-c.

# example loads (python)
python -c "import math;print (math.factorial(100000));"
python -c "exec(\"f=1\nfor n in range(100000):\n\tf=f*(n+1)\nprint(f)\")"

# example loads (linux):
stress --cpu 2 --timeout 10s run 2 cpu-cores with full load for 10 seconds
