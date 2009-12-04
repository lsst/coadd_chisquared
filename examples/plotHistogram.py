#!/usr/bin/env python
from __future__ import with_statement
"""Plot a histogram for a chi squared coadd and overlay a chi squared distribution
"""
import os
import sys
import math

import numpy
import pyfits
import matplotlib.pyplot as pyplot

NBins = 500
UseLogForY = True
UseSqrtForX = False


def clipOutliers(arr):
    """Clip values 3 sigma outside the median
    where sigma is estimated as the inter-quartile range * 0.741
    """
    arr.sort()
    arrLen = len(arr)
    iqr = arr[arrLen * 3 / 4] - arr[arrLen / 4]
    threeSigma = 4 * iqr * 0.741
    median = arr[arrLen / 2]
    minGood = median - threeSigma
    maxGood = median + threeSigma
    return numpy.extract((arr >= minGood) & (arr <= maxGood), arr)


def plotHistogram(coaddName, chiSqOrder):
    coadd = pyfits.open(coaddName)
    coaddData = coadd[0].data
    # undo normalization
    coaddData *= float(chiSqOrder)
    # get rid of nans and infs
    goodData = numpy.extract(numpy.isfinite(coaddData.flat), coaddData.flat)
    goodData = numpy.extract(goodData < 50, goodData)
    
    hist, binEdges = numpy.histogram(goodData, bins=NBins)
    hist = numpy.array(hist, dtype=float)
    hist /= hist.sum()
    
    if UseLogForY:
        dataY = numpy.log10(hist)
    else:
        dataY = hist
    
    dataX = binEdges[0:-1]
    if UseSqrtForX:
        plotDataX = numpy.sqrt(dataX)
    else:
        plotDataX = dataX

    # plot histogram: log10(frequency) vs. value
    pyplot.plot(plotDataX, dataY, drawstyle="steps")
    if UseLogForY:
        pyplot.ylabel('log10 frequency')
    else:
        pyplot.ylabel('frequency')

    if UseSqrtForX:
        pyplot.xlabel('sqrt of sum of (counts/noise)^2')
    else:
        pyplot.xlabel('sum of (counts/noise)^2')

    # plot chiSq probability distribution
    chiSqX = dataX
    chiSqDist = numpy.power(chiSqX, (chiSqOrder / 2.0) - 1) * numpy.exp(-chiSqX / 2.0)
    chiSqDist /= chiSqDist.sum()
    if UseLogForY:
        chiSqDistY = numpy.log10(chiSqDist)
    else:
        chiSqDistY = chiSqDist
    pyplot.plot(plotDataX, chiSqDistY)

    # set plot limits    
    goodY = numpy.extract(numpy.isfinite(dataY), dataY)
    maxY = goodY.max()
    minY = goodY.min()
    yRange = maxY - minY
    # plot out to where Y falls to 1% of max value
    maxYInd = goodY.argmax()
    yEndVal = minY + (yRange * 0.01)
    smallYIndices = numpy.where(goodY < yEndVal)[0]
    endInd = numpy.extract(smallYIndices > maxYInd, smallYIndices)[0]
    pyplot.xlim((0, plotDataX[endInd]))
    yMargin = yRange * 0.05
    pyplot.ylim((minY, maxY + yMargin))
    
    pyplot.show()


if __name__ == "__main__":
    helpStr = """Usage: plotHistogram.py coaddfile chiSqOrder

where:
- coaddfile is the path of the coadd
- chiSqOrder is the chi squared order for the best fit line; typically the # of images
"""
    if len(sys.argv) != 3:
        print helpStr
        sys.exit(0)
    
    coaddName = sys.argv[1]
    chiSqOrder = float(sys.argv[2])

    plotHistogram(coaddName, chiSqOrder)