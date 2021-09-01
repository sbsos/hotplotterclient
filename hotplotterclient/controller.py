import threading
from plotter import plot_process_controller, settings_config
from hard_drive_controller import hard_drive_controller
import configparser
import requests
import json
import time


class plotProcessDto(object):
    processId = None
    phase = ""
    step = ""
    plotNumber = ""
    destinationDrive = "N/A"
    plotDrive = "N/A"
    
    def __init__(self, processId, phase, step, plotNumber, destinationDrive, plottingDrive, clientIdentifier):
        self.processId = processId
        self.phase = phase
        self.step = step
        self.plotNumber = plotNumber
        self.destinationDrive = destinationDrive
        self.plotDrive = plottingDrive
        self.clientIdentifier = clientIdentifier


class payload(object):

    def __init__(self):
        self.plottingStatuses = []
        self.hardDrives = []
        self.username = ""
        self.plotterKey = ""
    
    def addHardDrives(self, hardDrives):
        self.hardDrives = hardDrives

    def addPlots(self, plotController):
        self.plottingStatuses = []
        
        for plotMonitor in plotController.active_plot_monitors:
            plotProcess = plotProcessDto(plotMonitor.proc.pid, plotMonitor.phase, plotMonitor.step, plotMonitor.plot_number, plotMonitor.destination_drive, plotMonitor.plotting_drives, plotMonitor.client_identifier)
            self.plottingStatuses.append(plotProcess)

    def addAuth(self, username, plotterKey):
        self.username = username
        self.plotterKey = plotterKey

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class master_controller(object):
    plot_controllers = []
    plot_controller = plot_process_controller()
    hd_controller = hard_drive_controller()
    username = ''
    plotterKey = ''
    api_url = 'https://api.hotplotter.com/api/Plotter/UpdateStatus'

    def __init__(self, username, plotterKey):
        self.username = username
        self.plotterKey = plotterKey
    
    def start_plot(self, farm_config):
        runner = threading.Thread(target = self.plot_controller.start_plotting, args =(farm_config,))
        runner.daemon = True
        runner.start()

    # this isn't clean, but API should be agnostic of content here... probably would require a refactor on the settings/plotter, and i'm not in the mood to do that.
    def transformToPlotConfig(self, queuedPlot):
        config = {}
        if queuedPlot['parallelPlots'] is None:
            queuedPlot['parallelPlots'] = 1  # we need this number to always be at least 1.
        config['drives'] = [{"destination_drive": queuedPlot['destinationDrive'], "temp_drive": queuedPlot['plotDrive'], "temp_drive_two": queuedPlot['plotDriveTwo'], "parallel_plots": queuedPlot['parallelPlots'], "client_identifier": queuedPlot['clientIdentifier']}]
        config['size'] = queuedPlot['size']
        config['stagger_type'] = queuedPlot['staggerType']
        config['pool_key'] = queuedPlot['poolKey']
        config['farm_key'] = queuedPlot['farmKey']
        config['ram'] = queuedPlot['ram']
        config['stagger_time'] = queuedPlot['staggerTime']
        config['threads'] = queuedPlot['threads']
        config['count'] = queuedPlot['count']
        config['buckets'] = queuedPlot['buckets']
        config['plotter_type'] = queuedPlot['plotterType']
        config['pool_type'] = queuedPlot['poolType']
        config['client_identifier'] = queuedPlot['clientIdentifier']
        
        return config
        
    def heart_beat(self):
        heartbeat_interval = 120.0
        
        postData = payload()
        postData.addHardDrives(self.hd_controller.get_hard_drives())
        postData.addPlots(self.plot_controller)
        postData.addAuth(self.username, self.plotterKey)
        try:
            x = requests.post(self.api_url, data=postData.toJSON(), headers={"Content-Type": "application/json"})
            if(x.ok):
                for plotToRun in x.json():
                    print("Plot Request Received")
                    transformedConfig = self.transformToPlotConfig(plotToRun)
                    print(str(transformedConfig))
                    run_config = settings_config(transformedConfig)
                    self.start_plot(run_config)
            else:
                if x.status_code == 400:
                    raise Exception("Please confirm your username and plotter key are correct!")
        except requests.ConnectionError as err:
            print("API Error. " + str(err) + ". Retrying in " + str(heartbeat_interval))
            
        heartbeat = threading.Timer(heartbeat_interval, self.heart_beat)
        heartbeat.daemon = True
        heartbeat.start()
        
        
# delete:
def generate_config():
    parser = configparser.RawConfigParser()
    parser.read('plotter_config.txt')

    controller_config = settings_config(dict(parser.items('Settings')))
    return controller_config


def main():
    parser = configparser.RawConfigParser()
    parser.read('plotter_config.txt')
    settings = dict(parser.items('Settings'))
    controller = master_controller(settings['username'], settings['plotterkey'])
    controller.heart_beat()
        
    
if __name__ == '__main__':
    main()
    while True:
        time.sleep(3)
