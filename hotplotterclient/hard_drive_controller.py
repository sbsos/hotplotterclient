import shutil
import psutil
import os

class hard_drive(object):
    total = 0
    free = 0
    drive_name = ""
    gb_formula = 1024 * 1024 * 1024

    def __init__(self, total, free, drive_name):
        gb_total = total / self.gb_formula
        gb_free = free / self.gb_formula
        self.totalSpace = gb_total
        self.freeSpace = gb_free
        self.drive = drive_name

    
class hard_drive_controller(object):
    available_drive_letters = ["A:/", "B:/", "C:/", "D:/", "E:/", "F:/", "G:/", "H:/", "I:/", "J:/", "K:/", "L:/", "M:/", "N:/", "O:/", "P:/", "Q:/", "R:/", "S:/", "T:/", "U:/", "V:/", "W:/", "X:/", "Y:/", "Z:/"]
    supported_hard_drive_formats = ['vfat','ext4', 'ext3', 'ext2', 'fat32', 'ntfs']

    def get_hard_drives_linux(self):
        hard_drives = []
        hds = psutil.disk_partitions()
        for available_drive in hds:
            try:
                if available_drive.fstype.lower() in self.supported_hard_drive_formats:
                    hd = self.get_hard_disk_space(available_drive.mountpoint)
                    hard_drives.append(hd)
            except Exception:
                continue
        return hard_drives
        
    def get_hard_drives_windows(self):
        hard_drives = []
        for available_drive in self.available_drive_letters:
            try:
                hd = self.get_hard_disk_space(available_drive)
                hard_drives.append(hd)
            
            except Exception:
                continue
        return hard_drives
    
    def get_hard_drives(self):
        if os.name == 'nt':
            return self.get_hard_drives_windows()   
        elif os.name == 'posix':
            return self.get_hard_drives_linux()
        else:
            print("Auto hard-drive mapping is not supported for this operating system")
            return []
    
    def get_hard_disk_space(self, drive):
        if os.name == 'nt':
            total, used, free = shutil.disk_usage(drive)
            hd = hard_drive(total, free, drive)
            return hd
        elif os.name == 'posix':
            diskUsage = psutil.disk_usage(drive)
            hd = hard_drive(diskUsage.total, diskUsage.free, drive)
            return hd
        
    
if __name__ == '__main__':
    controller = hard_drive_controller()
