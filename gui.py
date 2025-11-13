import tkinter as tk
import parse
class mainWindow:
    def __init__(self,root):
        self.root = root
        self.root.title("Calendar Parser Without a Cool Acronym")
        self.root.geometry("400x300")
        self.keybutton = tk.Button(root,text="Connect Accounts",command=self.connwindow())
        self.keybutton.pack(side=tk.RIGHT, padx=5)
        self.syncbutton = tk.Button(root,text="Force Update" ,command=self.reader.sync())
        self.syncbutton.pack(side=tk.RIGHT,padx=5)
        self.alertbutton = tk.Button(root,text="Alert Settings",command=self.alertsettings())
        self.alertbutton.pack(root,pady=5)
        self.custbutton = tk.Button(root,text="Customize Spreadsheet")
        self.custbutton.pack(root,side=tk.LEFT,padx=10)

    def connwindow(self):
       self.connwin = tk.Toplevel(self.root)
       self.connwin.title("Connect Accounts")
       self.gAPI = tk.StringVar()
       self.cURL = tk.StringVar()
       self.DriveFile = tk.StringVar()
       self.Gprompt = tk.Label(self.connwin,text="Enter Google API key:")
       self.Gprompt.pack(pady=5)
       self.Gentry = tk.Entry(self.connwin,textvariable=self.gAPI)
       self.Gentry.pack(pady=5)
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
    
    def APIin(self):
        self.reader = parse.Reader(self.cURL,self.gAPI,self.DriveFile)
    
    def on_thres_change(sv):
        current = sv.get()
        #This is where I would put the function to change the threshold, IF I HAD ONE!

    def alert():
        pass
    


if __name__ == "__main__":
    root = tk.Tk()
    app = mainWindow(root)
    root.mainloop()