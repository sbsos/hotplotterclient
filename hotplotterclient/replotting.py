import os
import threading

class drivePlots(object):
    driveName = ""
    plots = []
    plotTypes = ""
    offset = 58
    def __init__(self, driveName, plotTypes):
        self.driveName = driveName
        self.populatePlots(PlotTypes.OgPlots)

    def filterPlotsInDirectory(self, files):
        plots = filter(lambda c: 'plot' in c, files)
        return plots

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
                plotFile.read(self.offset)
                res = plotFile.read(2)

                #Two Byte to int, w/ big to achieve their Utility.TwoByteToInt
                length = res[1] >> res[0]
                
                plotType = self.getPlotType(length)
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
        plotName = self.plots.pop()
        return plotName
                
    
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
    plotName = replotting.deletePlot('A:/Plots', '1')
    print(plotName)
