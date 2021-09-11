import shutil
import psutil
import os
import subprocess
import re

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
    supported_hard_drive_formats = ['vfat','ext4', 'ext3', 'ext2', 'fat32', 'ntfs', 'fuseblk', 'tmpfs']

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
        mountvol_hds = []
        result = subprocess.run(['mountvol'], capture_output=True, text=True)
        parsed_hard_drives = re.findall('[A-Z]:\\\.*', result.stdout)
        
        for hd in parsed_hard_drives:
            try:
                formatted_hd = hd.replace("\\","/")
                mountvol_hds.append(formatted_hd)
                hd_object = self.get_hard_disk_space(formatted_hd)
                hard_drives.append(hd_object)
            except Exception:
                continue

        #network drives don't show up in mountvol. manually iterate to see if they have any network storage
        not_checked_drives = [i for i in self.available_drive_letters if i not in mountvol_hds]
        for hd in not_checked_drives:
            try:
                hd_object = self.get_hard_disk_space(hd)
                hard_drives.append(hd_object)
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
    hds = controller.get_hard_drives_windows()    
