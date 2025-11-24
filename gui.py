import globals
import tkinter as tk
import tkinter.messagebox
import parse
import schedule
from watchpoints import watch
import configparser
import simpleaudio
import threading
import sheets_conditional_formatting
import customizer
class mainWindow:
    def __init__(self,root):
        self.root = root
        self.root.title("Calendar Parser Without a Cool Acronym")
        root.protocol("WM_DELETE_WINDOW",self.shutdown)
        self.root.geometry("400x300")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.keybutton = tk.Button(root,text="Connect Accounts",command=self.connwindow)
        self.keybutton.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.syncbutton = tk.Button(root,text="Force Update" ,command=self.sync)
        self.syncbutton.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.alertbutton = tk.Button(root,text="Alert Settings",command=self.alertsettings)
        self.alertbutton.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.custbutton = tk.Button(root,text="Customize Spreadsheet")
        self.custbutton.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        self.datecheck()
        watch(globals.today,callback=self.onUpdate)
        schedule.every().hours.at("00:30").do(self.sync)
        schedule.every().day.at("09:00").do(self.daily_check)
        self.run_sched()

    def sync(self):
        self.syncSettings("read")
        try:
            self.reader.sync()
        except:
            print("Warning, no reader class yet.")

    def fileFuckery(self,command,file,section,lookfor,changeTo=None):
         config = configparser.ConfigParser()
         config.read(file)
         if section not in config:
             config.add_section(section)
         if command == "read":
             result = config[section][lookfor]
             return result
         elif command == "write":
             config[section][lookfor] = str(changeTo)
             with open(file,'w') as f:
                 config.write(f)

    def shutdown(self):
        if tk.messagebox.askokcancel("Quit","Do you want to quit? This will disable alerts!"):
            self.syncSettings("write")
            root.destroy()
   
    def syncSettings(self, command):
    # Save values TO ini
        if command == "write":
            self.fileFuckery("write","settings.ini","settings","alarm",globals.Alarm)
            self.fileFuckery("write", "settings.ini", "settings", "threshold", globals.threshold)
            self.fileFuckery("write", "settings.ini", "keys", "cURL", self.reader.inURL)
            self.fileFuckery("write", "settings.ini", "keys", "DriveFile", self.reader.outFile)

        # Load values FROM ini
        elif command == "read":
            Alarm = self.fileFuckery("read","settings.ini","settings","Alarm")
            threshold = self.fileFuckery("read", "settings.ini", "settings", "threshold")
            cURL      = self.fileFuckery("read", "settings.ini", "keys", "cURL")
            DriveFile = self.fileFuckery("read", "settings.ini", "keys", "DriveFile")
            if Alarm:
                globals.Alarm = Alarm
                
            if threshold is not None:
                globals.threshold = int(threshold)

            if cURL:
                self.reader.inURL = cURL

            if DriveFile:
                self.reader.outFile = DriveFile

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
    
    def customization_window(self):
        self.custwin = tk.Toplevel(self.root)
        self.custwin.title("Spreadsheet Customization")
        self.later = tk.StringVar()
        self.soon = tk.StringVar()
        self.now = tk.StringVar()
        self.quiz = tk.StringVar()
        self.optional = tk.StringVar()
        self.essay = tk.StringVar()
        self.project = tk.StringVar()
        self.final = tk.StringVar()
        self.quizprompt = tk.Label(self.custwin,text="Enter a color for quizzes/exams (R,G,B)")
        self.quizentry = tk.Entry(self.custwin, textvariable=self.quiz)
        self.optionalprompt = tk.Label(self.custwin,text="Enter a color for optional assignments")
        self.optionalentry = tk.Entry(self.custwin,textvariable=self.optional)

    def customize(self):
       quiz = (self.quiz.get()).split(",")
       optional = (self.optional.get()).split(",")
       essay = (self.essay.get()).split(",")
       final = (self.final.get()).split(",")
       project = (self.project.get()).split(",")
       later = (self.later.get()).split(",")
       soon = (self.soon.get()).split(",")
       now = (self.now.get()).split(",")
       dueColors = customizer.Rule("daysleft",[later,soon,now])
       typeColors = customizer.Rule("type",[quiz,optional,essay,project,final])
       for each in (dueColors,typeColors):
           try:
               sheets_conditional_formatting.conditional_formatting(self.reader.outFile,each.jsonobj)
           except Exception as e:
               print(f"Error saving formatting rule {each}: {e}")

    def alarm(self,assignment):
        def playalarm():
            try:
                wave = simpleaudio.WaveObject.from_wave_file(alarm.wav)
                play = wave.play()
            except Exception as e:
                print(f"Error playing sound: {e}")

        tk.messagebox.showwarning("Time's running out!",f"Assignment: {assignment[0]} is due in {assignment[1]} days!","OK")
        threading.Thread(target=playalarm()).start()

    def APIin(self):
        try: 
            cURL = (self.cURL.get() or "").strip()
            DriveFile = (self.DriveFile.get() or "").strip()
        except:
            cURL = ""
            DriveFile = ""
        if not cURL or not DriveFile:
            try: 
                 cURL = self.fileFuckery("read","settings.ini","keys","cURL")
                 DriveFile = self.fileFuckery("read","settings.ini","keys","DriveFile")
            except:
                self.connwindow()
        fileid = DriveFile or None
        self.reader = parse.Reader(cURL,fileid)
        DriveFile = self.reader.outFile
        self.fileFuckery("write","settings.ini","keys","cURL",cURL)
        self.fileFuckery("write","settings.ini","keys","DriveFile",DriveFile)
    
    def on_thres_change(self,sv):
        current = sv.get()
        globals.threshold = current
        self.fileFuckery("write","settings.ini","settings","threshold",globals.threshold)

    def datecheck(self):
        try:
            for each in self.reader.masterList:
                threading.Thread(target=each.upDate).start()
                if globals.Alarm:
                    if each.alert() is not None:
                        self.alarm(each.alert())
        except:
            self.APIin()

    def daily_check(self):
        globals.today = globals.datetime.date.today()
        
    def onUpdate(self):
        self.daily_check()
        self.sync()
    

if __name__ == "__main__":
    root = tk.Tk()
    app = mainWindow(root)
    root.mainloop()