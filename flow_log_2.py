#!/usr/local/bin/env python
##############
# A G Athanassiadis
# Jan 2015
#
# use the period timing feature to detect
# the period between two rising edges
#
# this method is more accurate in the timing,
# and should be used if the time-resolution
# is limiting analysis
#
# currently this version uses the 16 bit counter
# meaning that the LabJack won't resort to an interrupt
# and there should be no issue extending this method to
# two simultaneous measurements
#
##############
from __future__ import division

import numpy as np
import u6
from datetime import datetime
import sys

# CONSTANTS

runTime = 10    # [seconds] time to acquire data for

# output file
filepath = "/Users/thanasi/Dropbox (MIT)/data/flow_rates_v1b/"


if __name__ == "__main__":

    # get any notes if there are any

    try:
        notes = sys.argv[1]
    except IndexError:
        notes = None

    try:
        # initialize device
        d = u6.U6()

        # For applying the proper calibration to readings.
        d.getCalibrationData()

        sys.stdout.write("Initialized U6...")

        # set up period timer
        # make sure to disable the two counters
        #  Timer0 will read on FIO0
        d.configIO(NumberTimersEnabled=1, EnableCounter0='F', EnableCounter1='F')
        d.configTimerClock(TimerClockBase=1, TimerClockDivisor=100)

        d.getFeedback( u6.Timer0Config(TimerMode = u6.LJ_tmRISINGEDGES16) )

        sys.stdout.write("collecting data for %d seconds\n" % runTime)

        delays = []
        times = []

        start_time = datetime.now()
        dt = 0  # seconds

        # get the first count and reset the counter
        c = d.getFeedback( u6.Timer0(True) )[0]
        times.append(dt)
        delays.append(0)

        while dt < runTime:

            # get number of delays
            c = d.getFeedback( u6.Timer0(False) )[0]

            dt = datetime.now() - start_time    # datetime object
            dt = dt.seconds + float(dt.microseconds)/1000000.   # seconds

            times.append(dt)
            delays.append(c)


        nSamples = len(delays)
        sys.stdout.write("%0ss per sample\n" % (dt/nSamples))
        sys.stdout.write("%4.3f samples/sec\n" % (nSamples/dt))
        sys.stdout.flush()


        nDelays = np.array(delays)      # clock cycles
        nTimes = np.array(times)    # seconds


        # name the file based on start time and the fact that is the flow data
        filename = start_time.strftime("%Y.%m.%d.%H%M%S.fbundle")


        # np.savez("%s%s.npz" % (filepath,filename),
        #          delays=nDelays, times=nTimes, notes=notes)

    # clean up if we run into issues
    # that way there are no problems re-running
    except Exception, e:
        print "Caught an exception:", e
        pass


    # finally
    d.close()