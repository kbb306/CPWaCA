import src.globals as globals
import tkinter as tk
import tkinter.messagebox #Do not remove
import src.parse as parse
import schedule
import configparser
import pygame
import threading
import src.API.sheets_conditional_formatting as sheets_conditional_formatting
import src.customizer as customizer

class Window:
    """The GUI
    """
    def __init__(self,root):
        """Constructor for the Window object

        Args:
            root (tkinter object): The primary window
        """
        self.root = root
        self.root.title("Calendar Parser Without a Cool Acronym")
        root.protocol("WM_DELETE_WINDOW",self.shutdown)
        self.root.geometry("700x500")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        try:
            pygame.mixer.init()
        except:
            sound = None

        self.keybutton = tk.Button(root,text="Connect Accounts",command=self.connwindow)
        self.keybutton.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.syncbutton = tk.Button(root,text="Force Update" ,command=self.sync)
        self.syncbutton.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.alertbutton = tk.Button(root,text="Alert Settings",command=self.alertsettings)
        self.alertbutton.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.custbutton = tk.Button(root,text="Customize Spreadsheet", command=self.customization_window)
        self.custbutton.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        schedule.every().hours.at("00:30").do(self.sync)
        self.run_sched()
        self.root.after(0, self.sync)


    def sync(self):
        """Spawn thread for reader.sync().
        """
        if getattr(self, "_sync_running", False):
            print("Sync already running, skipping.")
            return

        self._sync_running = True
        try:
            self.syncbutton.config(state="disabled")
        except Exception:
            pass

        def worker():
            try:
                self.APIin()
                self.reader.sync()
            except Exception as e:
                tb = parse.traceback.format_exc()
                print(f"Warning sync failed due to {e}. Traceback is {tb}")
            finally:
                self.root.after(0, self._sync_finished)

        threading.Thread(target=worker, daemon=True).start()

    def _sync_finished(self):
        """
        Reset _sync_running and unblock syncbutton, then call syncSettings and daily_check()
        """
        self._sync_running = False

        try:
            self.syncbutton.config(state="normal")
        except Exception:
            pass

        self.syncSettings("read")
        self.daily_check()

       

    def iniBot(self,command,file,section,lookfor,changeTo=None):
         """_Run the given command on the specified field in the given ini file.

        Args:
            command (string): "read" or "write"
            file (string): path to desired ini file
            section (string): Section containing the field you want to access
            lookfor (string): The name of the field you want to access
            changeTo (string, optional): What to change the specified field to (Write mode only). Defaults to None.

        Returns:
            string: The varible you requested (read mode only)
        """
         config = configparser.ConfigParser()
         config.read(f"/data/{file}")
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
        """Bring up confimation dialogue before destroying window
        """
        if tk.messagebox.askokcancel("Quit","Do you want to quit? This will disable alerts!"):
            self.syncSettings("write")
            root.destroy()
   
    def syncSettings(self, command):
        """Read or write all settings to/from Settings.ini"

        Args:
            command (string): "read" or "write"
        """
        if command == "write":
            self.iniBot("write","settings.ini","settings","alarm",globals.Alarm)
            self.iniBot("write", "settings.ini", "settings", "threshold", globals.threshold)
            self.iniBot("write", "settings.ini", "settings", "tooMany", globals.tooMany)
            self.iniBot("write", "settings.ini", "keys", "cURL", self.reader.inURL)
            self.iniBot("write", "settings.ini", "keys", "DriveFile", self.reader.outFile)

        elif command == "read":
            Alarm = self.iniBot("read","settings.ini","settings","Alarm")
            threshold = self.iniBot("read", "settings.ini", "settings", "threshold")
            tooMany = self.iniBot("read","Settings.ini","settings","toomany")
            cURL      = self.iniBot("read", "settings.ini", "keys", "cURL")
            DriveFile = self.iniBot("read", "settings.ini", "keys", "DriveFile")
            if Alarm:
                globals.Alarm = Alarm
                
            if threshold is not None:
                globals.threshold = int(threshold)

            if tooMany:
                globals.tooMany = int(tooMany)

            if cURL:
                self.reader.inURL = cURL

            if DriveFile:
                self.reader.outFile = DriveFile

    def run_sched(self):
        """Loop scheduled events
        """
        try:
            schedule.run_pending()
        except:
            print("Error in scheduler job!")
            parse.traceback.print_exc()
        self.root.after(1000, self.run_sched)

    def connwindow(self):
       """House user inputs for cURL and DriveFile
       """
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
        """Alarm settings panel
        """
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
    
    def alarm(self):
        self.popup = tk.Toplevel(root)
    def customization_window(self):
        """Customization settings (not yet implemented)
        """
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
        """Alarm popup with cross-platform looping sound
        """        
        win = tk.Toplevel(self.root)
        win.title("Time's running out!")
        win.transient(self.root)
        win.lift()
        win.focus_force()

        msg = f"{assignment[0]} is due in {assignment[1]} days!"
        print(f"ALARM: {msg}")

        label = tk.Label(win, text=msg, padx=20, pady=20)
        label.pack()

        try:
            sound = pygame.mixer.Sound("../data/alarm.wav")
        except Exception as e:
            print(f"Error loading alarm.wav: {e}")
            sound = None

        def close_alarm():
            if sound:
                sound.stop()
            win.destroy()

        btn = tk.Button(win, text="OK", width=10, command=close_alarm)
        btn.pack(pady=10)

        if sound:
            try:
                sound.play(loops=-1)  
            except Exception as e:
                print(f"Error playing alarm.wav: {e}")


        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", close_alarm)

    def customize(self):
       """Build json string for sheets_conditional_formatting
       """
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

    
    def APIin(self):
        """Create Reader() object using available cURL and DriveFile settings
        """
        try: 
            cURL = (self.cURL.get() or "").strip()
            DriveFile = (self.DriveFile.get() or "").strip()
        except:
            cURL = ""
            DriveFile = ""
        if not cURL or not DriveFile:
            try: 
                 cURL = self.iniBot("read","settings.ini","keys","cURL")
                 DriveFile = self.iniBot("read","settings.ini","keys","DriveFile")
            except:
                self.connwindow()
        fileid = DriveFile or None
        self.reader = parse.Reader(cURL,fileid)
        DriveFile = self.reader.outFile
        self.iniBot("write","settings.ini","keys","cURL",cURL)
        self.iniBot("write","settings.ini","keys","DriveFile",DriveFile)
        return
    
    def on_thres_change(self, *args):
        """Update globals.threshold on change to threshold entry box in alarm settings
        """
        current = self.daysUntil.get()
        if current.isdigit():
            globals.threshold = int(current)
            self.iniBot("write", "settings.ini", "settings", "threshold", globals.threshold)

    def datecheck(self):
        """Call upDate on each assignment in masterlist. Call alert on each assignment and check output if globals.alarm is true"""
        try:
            for each in self.reader.masterList:
                each.upDate()
                if globals.Alarm:
                    if each.alert() is not None:
                        self.alarm(each.alert())
        except:
            self.APIin()
            self.datecheck()

    def daily_check(self):
        """Update globals.today and call datecheck().
        """
        globals.today = globals.datetime.date.today()
        self.datecheck()
        
    
    

if __name__ == "__main__":
    root = tk.Tk()
    app = Window(root)
    root.mainloop()