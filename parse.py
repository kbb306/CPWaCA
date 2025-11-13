import uuid
import datetime
import sheets_update_values
import sheets_get_values
import sheets_append_values
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
        valueFound = False
        for each in self.masterList:
            for each2 in self.readToEnd():
                if each2.uid == each.uid:
                    valueFound = True
                else:
                    valueFound = False
                if not valueFound:
                    sheets_append_values.append_values(self.outFile,"A5:F5","USER_ENTERED",[])
    
    def sync(self):
        self._import()
        self.export()



    def readToEnd(self):
        row = 1
        result = sheets_get_values.get_values(self.outFile,(("A").join(row)))
        value = result.get("values",[])
        results = []
        while (value is not None or value != "" ) or (value or value[0]):
            result = sheets_get_values.get_values(self.outFile,(("A").join(row)))
            value = result.get("values",[])
            row = row + 1
        for i in range(row - 1):
            result = sheets_get_values.get_values(self.outFile,(("A").join(i).join("F").join(i)))
            arglist = result.get("values",[])
            new = Assignment(arglist[0],arglist[1],arglist[4],arglist[5])
            results.append(new)
        return results

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
    def __init__(self,course,assignment,date,uid=uuid.uuid4()):
        self.uid = uid
        self.name = assignment
        self.dueDate = date
        self.course = course
    def alert(self):
        date = datetime.date.today()
        if self.dueDate - date < threshold: #This should be a global variable, probably pulled from a settings file?
            self.playAlarm() # Routine to play alarm noise
    


        
