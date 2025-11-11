import tkinter as tk
class mainWindow:
    def __init__(self,root):
        self.root = root
        self.root.title("Calendar Parser Without a Cool Acronym")
        self.root.geometry("400x300")
        self.keybutton = tk.Button(root,text="Connect Accounts",command=self.connwindow())
        self.keybutton.pack(side=tk.RIGHT, padx=5)
        self.syncbutton = tk.Button(root,text="Force Update")
        self.syncbutton.pack(side=tk.RIGHT,padx=5)
        self.alertbutton = tk.Button(root,text="Alert Settings",command=self.alertsettings())
        self.alertbutton.pack(root,pady=5)
        self.custbutton = tk.Button(root,text="Customize Spreadsheet")
        self.custbutton.pack(root,side=tk.LEFT,padx=10)

    def connwindow(self):
       self.connwin = tk.Toplevel(self.root)
       self.connwin.title("Connect Accounts")
       self.Gprompt = tk.Label(self.connwin,text="Enter Google API key:")
       self.Gprompt.pack(pady=5)
       self.Gentry = tk.Entry(self.connwin)
       self.Gentry.pack(pady=5)
       self.Cprompt = tk.Label(self.connwin, text="Enter canvas API key:")
       self.Cprompt.pack(pady=5)
       self.Centry = tk.Entry(self.connwin)
       self.Centry.pack(pady=5)
       tk.Button(self.connwin,text="Submit",command=self.APIin).pack(pady=10)
       tk.Button(self.connwin,text="Close",command=self.connwin.destroy).pack(pady=10)

    def alertsettings(self):
        self.alertwin = tk.Toplevel(self.root)
        self.alertwin.title("Alert Settings")
        self.toggle = tk.Button(self.alertwin,text="Toggle alerts on/off")
        self.thresholdPrompt = tk.Label(self.alertwin,text="Enter alert threshold (Days until due)")
        self.threshold = tk.Entry(self.alertwin)
        self.toggle.pack(pady=5)
        self.thresholdPrompt.pack(pady=5)
        self.threshold.pack(pady=5)
    


if __name__ == "__main__":
    root = tk.Tk()
    app = mainWindow(root)
    root.mainloop()