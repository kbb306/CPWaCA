import uuid
import datetime
import sheets_update_values
import sheets_get_values
import re
# Note: Do we need tkinter imported here to create a window,or can we get it from the gui.py file that imports this one?
class Reader():
    def __init__(self,inAPI,outAPI,outFile=None,):
        self.inAPI = inAPI
        self.outAPI = outAPI
        self.outFile = outFile
        self.masterList = []
        if outFile is None:
            pass #Use horrible Goggle APIs to create a new Sheets file
    def _import(self):
         #This is where I need your Canvas API wizardry
         self.parse(inFile)

    def export(self):
        #Google API wizardry goes here
        pass
    
    def sync(self):
        self._import()
        self.export()

    def parse(self,file):
        with open(file, 'r') as f:
            rows = f.readlines()
        for each in rows:
            if each == "BEGIN:VEVENT":
                for key,value in each.split(":",1):
                    if (key == "END"):
                        thing = Assignment(course,ID,assignment,date)
                        self.masterList.append(thing)
                    if key == "DTSTAMP":
                        date = value.strip()
                    elif (key == "SUMMARY"):
                        assignment = value.strip().split("[")[0].strip("[]")
                        course = value.strip().split("[")[1].strip("[]")
                    elif key == "URL;VALUE=URI":
                        backhalf  = value.split("_")[2].split("&")[0]
                        ID = re.sub(r'[^0-9]','',backhalf)


                
class Assignment():
    def __init__(self,course,ID,assignment,date):
        self.uid = uuid.uuid4()
        self.name = assignment
        self.dueDate = date
    def alert(self):
        date = datetime.date.today()
        if self.dueDate - date < threshold: #This should be a global variable, probably pulled from a settings file?
            self.playAlarm() # Routine to play alarm noise



        
