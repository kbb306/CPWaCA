import tkinter as tk
class mainWindow:
    def __init__(self,root):
        self.root = root
        self.root.title("Calendar Parser Without a Cool Acronym")
        self.root.geometry("400x300")
        self.keybutton = tk.Button(root,text="Connect Accounts")
        self.keybutton.pack(side=tk.RIGHT, padx=5)
        self.syncbutton = tk.Button(root,text="Force Update")
        self.syncbutton.pack(side=tk.RIGHT,padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = mainWindow(root)
    root.mainloop()