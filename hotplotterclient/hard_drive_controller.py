import shutil


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
        
    def get_hard_drives(self):
        hard_drives = []
        for available_drive in self.available_drive_letters:
            try:
                hd = self.get_hard_disk_space(available_drive)
                hard_drives.append(hd)
            except Exception:
                continue
        return hard_drives
    
    def get_hard_disk_space(self, drive):
        total, used, free = shutil.disk_usage(drive)
        hd = hard_drive(total, free, drive)
        return hd
        
    
if __name__ == '__main__':
    controller = hard_drive_controller()
