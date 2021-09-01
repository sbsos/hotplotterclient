import subprocess
import threading
import datetime
import os
import shlex

class plot_process_monitor(object):
    proc = None
    start_time = None
    temp_drive = ""
    temp_drive_two = ""
    destination_drive = ""
    log_file_name = ""
    is_alive = True
    phase = 0
    file_name = ""
    step = ""
    plot_number = 0
    number_of_iterations = 0
    client_identifier = ""
    
    def __init__(self, proc, temp_drive, temp_drive_two, destination_drive, number_of_iterations, client_identifier):
        self.proc = proc
        self.temp_drive = temp_drive
        self.temp_drive_two = temp_drive_two
        self.destination_drive = destination_drive
        self.file_name = str(self.proc.pid) + ".txt"
        self.start_time = datetime.datetime.now()
        self.number_of_iterations = number_of_iterations
        self.client_identifier = client_identifier

    @property
    def plotting_drives(self):
        joined_drive_names = self.temp_drive
        if (self.temp_drive_two is None) or (str(self.temp_drive_two).strip() == ""):
            return joined_drive_names
        else:
            joined_drive_names += " and " + self.temp_drive_two

        return joined_drive_names
        
    def start_monitoring(self):
        self.log_to_file("Starting: " + self.plotting_drives + " Plotting To: " + self.destination_drive + " with PID of: " + str(self.proc.pid))
        while self.proc.poll() is None:
            line = self.proc.stdout.readline()
            self.step = line

            if "Starting phase 1/4".lower() in line.lower() or "plot name" in line.lower():
                self.plot_number += 1
            
            parsed_phase = self.get_phase(line)
            if parsed_phase != 0:
                self.phase = parsed_phase
            if not line:
                self.is_alive = False
                break

            self.log_to_file(line)

    def log_to_file(self, line):
        with open(self.file_name, 'a+') as file:
            file.write(self.plotting_drives + " " + self.destination_drive + ": " + str(line) + '\n')

    def get_phase(self, content):
        lower_content = content.lower()
        if "phase 1" in lower_content or '[p1]' in lower_content:
            return 1
        if "phase 2" in lower_content or "phase 1 took" in lower_content:
            return 2
        if "phase 3" in lower_content or "phase 2 took" in lower_content:
            return 3
        if "phase 4" in lower_content or "phase 3 took" in lower_content:
            return 4
        return 0


class settings_config(object):
    drives = []
    size = 0
    threads = 0
    ram = 0
    pool_key = ""
    farm_key = ""
    stagger_time = 0
    stagger_type = ""
    count = 0
    buckets = 0
    plotter_type = ""
    pool_type = "OriginalPlot"
    client_identifier = ""

    def __init__(self, dictionary_config):
        self.drives = dictionary_config["drives"]
        self.stagger_type = dictionary_config['stagger_type']
        if dictionary_config['stagger_time'] is not None:
            self.stagger_time = int(dictionary_config['stagger_time'])
            
        self.farm_key = dictionary_config['farm_key']
        self.pool_key = dictionary_config['pool_key']
        self.ram = dictionary_config['ram']
        self.threads = dictionary_config['threads']
        self.size = dictionary_config['size']
        self.count = dictionary_config['count']
        self.client_identifier = dictionary_config['client_identifier']
        self.buckets = dictionary_config['buckets']
        self.pool_type = dictionary_config['pool_type']    
        self.plotter_type = dictionary_config['plotter_type']

        
class plot_process_controller(object):
    list_of_plotting_processes = []
    log_file_name = "log_file_"
    active_plot_monitors = []

    def add_monitor(self, monitor):
        self.active_plot_monitors.add(monitor)

    def remove_inactive_plot_monitors(self):
        self.active_plot_monitors = [x for x in self.active_plot_monitors if x.is_alive is True]
    
    def event_listener(self, config):
        self.remove_inactive_plot_monitors()
        for plot_config in config.drives:
            iterations_left = int(plot_config['parallel_plots']) > 0
            if iterations_left is False:
                continue
            
            # get the most recently created active plot - temp drive two only will be created with madmax. we're fine filtering on it, since if it isn't used, they'll always be empty
            active_monitors = [x for x in self.active_plot_monitors if x.temp_drive == plot_config['temp_drive'] and x.temp_drive_two == plot_config['temp_drive_two'] and x.destination_drive == plot_config['destination_drive']]
            active_monitors.sort(key=lambda x: x.start_time, reverse=True)

            latest_monitor = None
            if len(active_monitors) > 0:
                latest_monitor = active_monitors[0]
            else:
                raise Exception("It's likely you are plotting to the root directory of C:/, which you will not have permission to do without running as an administrator.")
            
            if config.stagger_type.lower() == 'time':
                if latest_monitor.start_time < datetime.datetime.now() - datetime.timedelta(seconds = config.stagger_time):
                    print("Starting Next Plot")
                    self.start_plot(config, plot_config, len(active_monitors) + 1)
            elif config.stagger_type.lower() == 'phase':
                if latest_monitor.phase == 2:
                    print("Starting Next Plot")
                    self.start_plot(config, plot_config, len(active_monitors) + 1)
        
        listener = threading.Timer(5.0, self.event_listener, args = (config,))
        listener.daemon = True
        listener.start()

    def start_plotting(self, config):
        for plot_config in config.drives:
            count = int(plot_config["parallel_plots"])
            
            if count > 0:
                self.start_plot(config, plot_config, count)
    
        self.event_listener(config)

    def start_plot(self, config, plot_config, iteration):
        plot_proc = plot_process(config, plot_config["temp_drive"], plot_config["temp_drive_two"], plot_config["destination_drive"])
        proc = plot_proc.begin_plotting()

        plot_config["parallel_plots"] -= 1

        monitor = plot_process_monitor(proc, plot_config["temp_drive"], plot_config["temp_drive_two"], plot_config["destination_drive"], iteration, plot_config["client_identifier"])

        thread = threading.Thread(target = monitor.start_monitoring)
        thread.daemon = True
        thread.start()

        self.active_plot_monitors.append(monitor)


class plot_process(object):
    final_drive = ''
    temp_drive = ''
    temp_drive_two = ''

    @property
    def plotting_drives(self):
        joined_drive_names = self.temp_drive
        if (self.temp_drive_two is None) or (str(self.temp_drive_two).strip() == ""):
            return joined_drive_names
        else:
            joined_drive_names += " and " + self.temp_drive_two

        return joined_drive_names

    def __init__(self, config, temp_drive, temp_drive_two, final_drive):
        self.config = config
        self.temp_drive = temp_drive
        self.temp_drive_two = temp_drive_two
        self.final_drive = final_drive
                
    def begin_plotting(self):
        if self.config.plotter_type == "chia":
            return self.begin_chia_plot()
        else:
            return self.begin_mad_max_plot()
        
    def get_pool_flag(self):
        if self.config.pool_type == 'OriginalPlot':
            return ' -p '
        if self.config.pool_type == 'PoolPlot':
            return ' -c '
    
    def build_mad_max_command_safe(self):
        command = 'chia_plot' + ' -n ' + str(self.config.count) + ' -r ' + str(self.config.threads) + ' -u ' + str(self.config.buckets) + ' -t ' + self.temp_drive + ' -2 ' + self.temp_drive_two + ' -d ' + self.final_drive + ' -f ' + self.config.farm_key + self.get_pool_flag() + self.config.pool_key
        split = shlex.split(command)
        return split

    def build_chia_plot_command_safe(self):
        command = 'chia plots create' + ' -n ' + str(self.config.count) + ' -r ' + str(self.config.threads) + ' -b ' + str(self.config.ram) + ' -k ' + str(self.config.size) + ' -t ' + self.temp_drive + ' -d ' + self.final_drive + ' -f ' + self.config.farm_key + self.get_pool_flag() + self.config.pool_key
        split = shlex.split(command)
        return split 
    
    def begin_mad_max_plot(self):
        command = self.build_mad_max_command_safe()
        print('#Beginning Temp Plot: ' + self.plotting_drives + ' Plotting to ' + self.final_drive + " using Chia Plotter")
        print("Count: " + str(self.config.count) + " Threads: " + str(self.config.threads) + " Buckets: " + str(self.config.buckets) + " TempDrive: " + str(self.plotting_drives) + " Final Drive: " + str(self.final_drive) + " Farm Key: " + self.config.farm_key + " Pool Key: " + self.config.pool_key)
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
        return proc

    def begin_chia_plot(self):
        command = self.build_chia_plot_command_safe()
        print('#Beginning Temp Plot: ' + self.temp_drive + ' Plotting to ' + self.final_drive + " using Chia Plotter")
        print("Count: " + str(self.config.count) + " Ram: " + str(self.config.ram) + " Threads: " + str(self.config.threads) + " Size: " + str(self.config.size) + " TempDrive: " + str(self.temp_drive) + " Final Drive: " + str(self.final_drive) + " Farm Key: " + self.config.farm_key + " Pool Key: " + self.config.pool_key)
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
        return proc
