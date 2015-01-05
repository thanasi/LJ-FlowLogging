#!/usr/local/bin/env python
##############
# A G Athanassiadis
# Jan 2015
#
# use the period timing feature to detect
# the period between two rising edges
#
# this method will be more accurate in the timing between pulses,
#   and the onboard timer is also used to reduce jitter
#   from unsynced computer-LabJack connections
#
# this method is preferable for low-frequency measurements
#
# currently this version uses the 32 bit counter
#   meaning that the LabJack resorts to an interrupt
#   potentially interfering with timing measurements
#   on different channels if one edge arrives
#   while the routine is already interrupted
##############

from __future__ import division

import numpy as np
import u6
import sys
from datetime import datetime


runTime = 10    # seconds

if __name__ == "__main__":

    try:
        notes = sys.argv[1]
    except IndexError:
        notes = None


    try:
        d = u6.U6()
        d.getCalibrationData()

        # setup 2 timers 12 MHz and make sure the counters are disabled
        d.configIO(NumberTimersEnabled=2)
        d.configTimerClock(TimerClockBase=12)

        # configure one timer to measure the time between rising edges
        #   note that 32 bit rising requires interrupts
        # and the other timer to report the system time from startup
        configCommand = []
        configCommand.append(u6.Timer0Config(TimerMode = u6.LJ_tmRISINGEDGES32))    # this will run at 12 MHz
        configCommand.append(u6.Timer1Config(TimerMode = u6.LJ_tmSYSTIMERLOW))      # this will run at 4 MHz regardless
        d.getFeedback(configCommand)

        dt = []     # time since last rising edge
        t = []      # time that sample is taken

        command0 = []
        command0.append(u6.Timer0(True))    # reset timer before starting
        command0.append(u6.Timer1())        # get the clock time

        command1 = []
        command1.append(u6.Timer0(False))   # don't reset timer before starting
        command1.append(u6.Timer1())        # get the clock time


        start_time = datetime.now()

        r = d.getFeedback(command0)     # get initial data point
        dt.append(r[0])
        t.append(r[1])

        while (datetime.now() - start_time).seconds < runTime:
            r = d.getFeedback(command1)

            # TODO : figure out how to parse this data and only keep the relevant points (after a new edge has risen)

            dt.append(r[0])
            t.append(r[1])

        ndt = np.array(dt)
        nt = np.array(t, dtype=np.float)
        nt -= nt[0]         # only relative timing matters

        ds = 1.0 / 4e6      # clock cycles per sec given 4MHz clock
        nt *= ds            # convert cycles into seconds given 4MHz

    except Exception, e:
        print "Caught an exception:", e
        pass


    # finally
    d.close()