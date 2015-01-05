#!/usr/local/bin/env python
##############
# A G Athanassiadis
# Dec 2014
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
filepath = "/Users/thanasi/Dropbox (MIT)/data/flow_rates_v1/"


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

        # set up system timer (will take up FIO0 line)
        # and a single counter (FIO1) (Counter0 is disabled)
        d.configIO(NumberTimersEnabled=1, EnableCounter1=True)

        configCommand = []
        configCommand.append(u6.Timer0Config(TimerMode = u6.LJ_tmSYSTIMERLOW))      # system timer runs at 4 MHz
        d.getFeedback(configCommand)

        sys.stdout.write("Configured timers...")

        counts = []
        times = []

        command = []
        command.append(u6.Timer0())         # results[0]
        command.append(u6.Counter1(False))  # results[1]


        sys.stdout.write("collecting data for %d seconds\n" % runTime)
        start_time = datetime.now()

        # reset the counter
        d.getFeedback( u6.Counter1(True) )

        # now actually get the first data point
        r = d.getFeedback( command )
        times.append(r[0])
        counts.append(r[1])

        nSamples = 0

        # record data for preset duration
        while (datetime.now() - start_time).seconds < runTime:
            # get number of counts
            r = d.getFeedback( command )
            nSamples += 1

            # only save if the count has increased
            if r[1] > counts[-1]:
                times.append(r[0])
                counts.append(r[1])


        # nSamples = len(counts)
        sys.stdout.write("%0s per sample\n" % (runTime/nSamples))           ## this gives an x-error bar
        sys.stdout.write("%4.3f samples/sec\n" % (nSamples/runTime))
        sys.stdout.flush()


        # make everything numpy-ified
        nCounts = np.array(counts, dtype = np.int32)    # counts
        nTimes = np.array(times, dtype = np.float32)    # seconds

        nTimes -= nTimes[0]
        nTimes /= 4e6           # convert from 4MHz clock cycles to seconds


        # name the file based on start time and the fact that is the flow data
        filename = start_time.strftime("%Y.%m.%d.%H%M%S.fbundle")


        # np.savez("%s%s.npz" % (filepath,filename),
        #          counts=nCounts, times=nTimes, notes=notes)

    # clean up if we run into issues
    # that way there are no problems re-running
    except Exception, e:
        print "Caught an exception:", e
        pass


    # finally
    d.close()