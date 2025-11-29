import globals
import tkinter as tk
import tkinter.messagebox
import parse
import schedule
from watchpoints import watch
import configparser
class mainWindow:
    def __init__(self,root):
        self.root = root
        self.root.title("Calendar Parser Without a Cool Acronym")
        root.protocol("WM_DELETE_WINDOW",self.shutdown)
        self.root.geometry("700x500")
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

        self.custbutton = tk.Button(root,text="Customize Spreadsheet", command=self.customization_window)
        self.custbutton.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        self.datecheck()
        watch(globals.today,callback=self.onUpdate)
        schedule.every().minutes.at(":30").do(self.sync)
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
       self.connwin.geometry("500x300")
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
        self.alertwin.geometry("500x300")
        self.toggle = tk.Button(self.alertwin,text="Toggle alerts on/off")
        self.daysUntil = tk.StringVar()
        self.daysUntil.trace_add("write", self.on_thres_change)
        self.thresholdPrompt = tk.Label(self.alertwin,text="Enter alert threshold (Days until due)")
        self.threshold = tk.Entry(self.alertwin, textvariable=self.daysUntil)
        self.toggle.pack(pady=5)
        self.thresholdPrompt.pack(pady=5)
        self.threshold.pack(pady=5)
    
<<<<<<< Updated upstream
    def alarm(self):
        self.popup = tk.Toplevel(root)
=======
    def customization_window(self):
        """Someday, this will allow you to define color coding for the calendar"""
        self.custwin = tk.Toplevel(self.root)
        self.custwin.title("Spreadsheet Customization")
        self.custwin.geometry("500x300")
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
        self.quizprompt.pack(pady=5)
        self.quizentry.pack(pady=0)
        self.optionalprompt = tk.Label(self.custwin,text="Enter a color for optional assignments")
        self.optionalentry = tk.Entry(self.custwin,textvariable=self.optional)
        self.optionalprompt.pack(pady=5)
        self.optionalentry.pack(pady=0)

    def alarm(self, assignment):
        """Cross-platform alarm popup with looping sound."""
        
        win = tk.Toplevel(self.root)
        win.title("Time's running out!")
        win.transient(self.root)
        win.lift()
        win.focus_force()

        msg = f"{assignment[0]} is due in {assignment[1]} days!"
        print(f"ALARM: {msg}")

        label = tk.Label(win, text=msg, padx=20, pady=20)
        label.pack()

        # Load sound
        try:
            sound = pygame.mixer.Sound("alarm.wav")
        except Exception as e:
            print(f"Error loading alarm.wav: {e}")
            sound = None

        def close_alarm():
            # Stop alarm sound
            if sound:
                sound.stop()
            win.destroy()

        btn = tk.Button(win, text="OK", width=10, command=close_alarm)
        btn.pack(pady=10)

        # Loop sound forever until stop() is called
        if sound:
            try:
                sound.play(loops=-1)  # -1 = infinite loop
            except Exception as e:
                print(f"Error playing alarm.wav: {e}")

        # Modal behavior
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", close_alarm)

    def customize(self):
       """Passes rules to sheets_conditional_formatting"""
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

    
    

>>>>>>> Stashed changes

    def APIin(self):
        try: 
            cURL = self.cURL.get()
            DriveFile = self.DriveFile.get()
        except:
            cURL = None
            DriveFile = None
        if cURL is None or DriveFile is None:
            try: 
                 cURL = self.fileFuckery("read","settings.ini","keys","cURL")
                 DriveFile = self.fileFuckery("read","settings.ini","keys","DriveFile")
            except:
                self.connwindow()
        self.reader = parse.Reader(cURL,DriveFile)
        self.fileFuckery("write","settings.ini","keys","cURL",cURL)
        self.fileFuckery("write","settings.ini","keys","DriveFile",DriveFile)
    
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