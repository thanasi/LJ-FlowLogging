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

        # set up counter
        # Max input frequency = 8 MHz
        # if it's the only timer/counter
        #  Counter0 will read on FIO0
        # Just read the number of counts
        # at a fixed sampling rate
        d.configIO(EnableCounter0=True)

        sys.stdout.write("collecting data for %d seconds\n" % runTime)

        counts = []
        times = []

        start_time = datetime.now()
        dt = 0  # seconds

        # get the first count and reset the counter
        c = d.getFeedback( u6.Counter0(True) )[0]
        times.append(dt)
        counts.append(c)

        while dt < runTime:

            # get number of counts
            c = d.getFeedback( u6.Counter0(False) )[0]

            dt = datetime.now() - start_time    # datetime object
            dt = dt.seconds + float(dt.microseconds)/1000000.   # seconds

            times.append(dt)
            counts.append(c)


        nSamples = len(counts)
        sys.stdout.write("%0ss per sample\n" % (dt/nSamples))
        sys.stdout.write("%4.3f samples/sec\n" % (nSamples/dt))
        sys.stdout.flush()


        nCounts = np.array(counts)      # counts
        nTimes = np.array(times)    # seconds

        # find edges where the counts increased
        mask = nCounts[1:] > nCounts[:-1]

        # this is the relevant data
        nCounts1 = nCounts[mask]
        nTimes1 = nTimes[mask]


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