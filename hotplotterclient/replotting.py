import os
import threading

class drivePlots(object):
    driveName = ""
    plots = []
    plotTypes = ""
    formatLengthOffset = 52
    def __init__(self, driveName, plotTypes):
        self.driveName = driveName
        self.populatePlots(PlotTypes.OgPlots)

    def filterPlotsInDirectory(self, files):
        plots = filter(lambda c: 'plot' in c, files)
        return plots

    def getLength(self, byteArray):
        length = byteArray[1] >> byteArray[0]
        return length
    
    def populatePlots(self, filterPlotType):
        files = os.listdir(self.driveName)
        plots = self.filterPlotsInDirectory(files)
        for plot in plots:
            plotWithFullPath = ''
            if self.driveName[-1] != '/':
                plotWithFullPath = self.driveName + '/' + plot
            else:
                plotWithFullPath = self.driveName + plot

            with open(plotWithFullPath, "rb") as plotFile:
                plotFile.read(self.formatLengthOffset)
                res = plotFile.read(2)
                formatLength = self.getLength(res)
                plotFile.read(formatLength)

                memo = plotFile.read(2)
                memoLength = self.getLength(memo)
                
                plotType = self.getPlotType(memoLength)
                if plotType == filterPlotType:
                    self.plots.append(plotWithFullPath)
                    
    def getPlotType(self, memoLength):
        if memoLength == 112:
            return PlotTypes.NftPlots
        
        elif memoLength == 128:
            return PlotTypes.OgPlots
        
        #I did not understand this as well as I thought
        return None
    
    def getPlot(self):
        if len(self.plots) > 0:
            plotName = self.plots.pop()
            return plotName
        return None
                
    
class replotting(object):
    drivePlotsLookup = {}
    shouldReplot = False
    lock = threading.Lock()
    
    def __init__(self):
        return None
        
    #Only call upon new plot starting
    def addDrivePlots(self, drivePath, clientIdentifier, enabled):        
        if enabled:
            dp = drivePlots(drivePath, PlotTypes.OgPlots)
            self.drivePlotsLookup[drivePath + clientIdentifier] = dp
        

    def getPlotToDelete(self, drive, clientIdentifier):
        with self.lock:
            plotLookUp = self.drivePlotsLookup[drive + clientIdentifier]
            plotName = plotLookUp.getPlot()
            return plotName
    
    def deletePlot(self, drive, clientIdentifier):
        if drive + clientIdentifier in self.drivePlotsLookup:
            plotWithFullPath = self.getPlotToDelete(drive, clientIdentifier)
            if plotWithFullPath is not None:
                os.remove(plotWithFullPath)
                return True
            else:
                return False
        return None
    
class PlotTypes(object):
    OgPlots = "OgPlots"
    NftPlots = "NftPlots"

    
if __name__ == '__main__':
    replotting = replotting()
    replotting.addDrivePlots('A:/Plots', '1', True)
