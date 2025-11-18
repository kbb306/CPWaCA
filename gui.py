import globals
import tkinter as tk
import parse
import schedule
from watchpoints import watch
import configparser
class mainWindow:
    def __init__(self,root):
        self.root = root
        self.root.title("Calendar Parser Without a Cool Acronym")
        root.protocol("WM_DELETE_WINDOW",self.shutdown)
        self.root.geometry("400x300")
        self.keybutton = tk.Button(root,text="Connect Accounts",command=self.connwindow)
        self.keybutton.pack(side=tk.LEFT, padx=5)
        self.syncbutton = tk.Button(root,text="Force Update" ,command=self.sync)
        self.syncbutton.pack(side=tk.RIGHT,padx=5)
        self.alertbutton = tk.Button(root,text="Alert Settings",command=self.alertsettings)
        self.alertbutton.pack(pady=5)
        self.custbutton = tk.Button(root,text="Customize Spreadsheet")
        self.custbutton.pack(side=tk.LEFT,padx=10)
        self.datecheck()
        watch(globals.today,callback=self.onUpdate())
        schedule.every().minutes.at(":30").do({self.sync})
        schedule.every().day.at("09:00").do(self.daily_check)
        self.run_sched()


    def sync(self):
        self.syncSettings()
        try:
            self.reader.sync()
        except:
            print("Warning, no reader class yet.")

    def fileFuckery(self,command,file,section,lookfor,changeTo=None):
         config = configparser.ConfigParser()
         config.read(file)
         if command == "read":
             result = config[section][lookfor]
             return result
         elif command == "write":
             config[section][lookfor] = changeTo
             with open(file,'w') as f:
                 config.write(f)

    def shutdown(self):
        if tk.messagebox.askokcancel("Quit","Do you want to quit? This will disable alerts!"):
            self.syncSettings()
            root.destroy()
   
    def syncSettings(self,command):
        for name in globals:
            
            var = getattr(globals,name)
     
            try:
                self.fileFuckery(command,"settings.ini","settings",name,var)
            except ValueError:
                self.fileFuckery(command,"settings.ini","keys",name,var)
            finally:
                raise ValueError("Error",name,"not found in ini")
            
        cURL = self.fileFuckery(command,"settings.ini","keys","cURL",self.reader.inURL)
        DriveFile = self.fileFuckery(command,"settings.ini","keys","DriveFile",self.reader.outFile)
        if cURL is not None and DriveFile is not None:
            try:
                self.reader.inURL = cURL
                self.reader.outFile = DriveFile
            except:
                print("Warning: file vars not set!")

    def run_sched(self):
        schedule.run_pending()
        self.root.after(1000, self.run_sched)

    def connwindow(self):
       self.connwin = tk.Toplevel(self.root)
       self.connwin.title("Connect Accounts")
       self.gAPI = tk.StringVar()
       self.cURL = tk.StringVar()
       self.DriveFile = tk.StringVar()
       self.Cprompt = tk.Label(self.connwin, text="Enter canvas URL:")
       self.Cprompt.pack(pady=5)
       self.Centry = tk.Entry(self.connwin,textvariable=self.cURL)
       self.Centry.pack(pady=5)
       self.DrivePrompt = tk.Label(self.connwin,text="Enter the file ID of your google sheets file (leave blank to create one)")
       self.DrivePrompt.pack(pady=5)
       self.DriveEntry = tk.Entry(self.connwin,textvariable=self.DriveFile)
       self.DriveEntry.pack(pady=5)
       tk.Button(self.connwin,text="Submit",command=self.APIin).pack(pady=10)
       tk.Button(self.connwin,text="Close",command=self.connwin.destroy).pack(pady=10)

    def alertsettings(self):
        self.alertwin = tk.Toplevel(self.root)
        self.alertwin.title("Alert Settings")
        self.toggle = tk.Button(self.alertwin,text="Toggle alerts on/off")
        self.daysUntil = tk.StringVar()
        self.daysUntil.trace_add("write", self.on_thres_change)
        self.thresholdPrompt = tk.Label(self.alertwin,text="Enter alert threshold (Days until due)")
        self.threshold = tk.Entry(self.alertwin, textvariable=self.daysUntil)
        self.toggle.pack(pady=5)
        self.thresholdPrompt.pack(pady=5)
        self.threshold.pack(pady=5)
    
    def alarm(self):
        self.popup = tk.Toplevel(root)

    def APIin(self):
        cURL = self.cURL.get()
        DriveFile = self.DriveFile.get()
        if cURL is None or DriveFile is None:
            try: 
                 cURL = self.fileFuckery("read","keys.ini","cURL")
                 DriveFile = self.fileFuckery("read","keys.ini","DriveFile")
            except:
                self.connwindow()
        self.reader = parse.Reader(cURL,DriveFile)
        self.fileFuckery("write","settings.ini","keys","cURL",cURL)
        self.fileFuckery("wrire","settings.ini","keys","DriveFile",DriveFile)
    
    def on_thres_change(self,sv):
        current = sv.get()
        globals.threshold = current
        self.fileFuckery("write","settings.ini","settings","threshold",globals.threshold)

    def datecheck(self):
        try:
            for each in self.reader.masterList:
                each.upDate()
                if globals.Alarm:
                    if each.alert() is not None:
                        self.alarm()
        except:
            self.APIin()

    def daily_check(self):
        globals.today = globals.datetime.date.today()
        
   

    def onUpdate(self):
        self.daily_check()
        self.sync()
    
    def sync(self):
        try:
            self.reader.sync()
        except:
            print("No reader class yet.")
            self.APIin()


if __name__ == "__main__":
    root = tk.Tk()
    app = mainWindow(root)
    root.mainloop()