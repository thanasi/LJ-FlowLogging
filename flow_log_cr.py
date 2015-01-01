#!/usr/local/bin/env python
############################
## A G Athanassiadis
## Dec 2014
##
############################
from __future__ import division

import numpy as np
import u6
from datetime import datetime
import sys, os

## Constants
############################

## MODBUS channels to use





## feedback command
cmdlist = []    ## list of commands to send to U6





## output file
# filename = "/users/thanasi/Desktop/testdata2.npz"
filepath = "/Users/thanasi/Dropbox (MIT)/data/flow_rates_v1/"

if __name__ == "__main__":

    ## get
    notes = sys.argv[1]

    # initialize device
    d = u6.U6()


    try:
        # For applying the proper calibration to readings.
        d.getCalibrationData()


        data = []
        res = []
        gains = []
        times = []

        start_time = datetime.now()
        dt = 0
        while dt < runTime:
            ## get input voltage
            f = d.getAIN(AIN_CH, resolutionIndex=res_index, gainIndex=gain_index)   ## volts

            dt = datetime.now() - start_time ## datetime object
            dt = dt.seconds + float(dt.microseconds)/1000000.   ## seconds
            times.append(dt)

            data.append(f)
            # data.append(f['AIN'])
            # res.append(f['ResolutionIndex'])
            # gains.append(f['GainIndex'])


        nSamples = len(data)
        sys.stdout.write("%0ss per sample\n" % (dt/nSamples))
        sys.stdout.write("%4.3f samples/sec\n" % (nSamples/dt))
        sys.stdout.flush()

        # numSamples = len(data)
        # vData = [d.binaryToCalibratedAnalogVoltage(gains[i], data[i], False, res[i]) for i in range(numSamples)]

        nData = np.array(data)      ## volts
        nTimes = np.array(times)    ## seconds
        # nPress = VtoP(nData)        ## pascals
        # nRes = np.array(res)
        # nGains = np.array(gains)
        # np.savez(filename, data=nData, res=nRes, gains=nGains, times=times)


        ## name the file based on start time and the fact that is the pressure data
        filename = start_time.strftime("%Y.%m.%d.%H%M%S.fbundle")

        ## don't overwrite existing data
        i = 0
        while os.path.exists("%s%s-%d.npz" % (filepath,filename,i)):
            i += 1

        ## output voltage, pressure, and time data
        # np.savez("%s%s-%d.npz" % (filepath,filename,i),
        #          data=nData, press=nPress, times=nTimes, notes=notes)

        np.savez("%s%s-%d.npz" % (filepath,filename,i),
                 data=nData, times=nTimes, notes=notes)

    ## clean up if we run into issues
    ## that way there are no problems re-running
    except Exception, e:
        print "Caught an exception", e
        pass

    d.close()