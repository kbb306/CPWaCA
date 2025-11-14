import globals
import uuid
import datetime
import sheets_update_values
import sheets_get_values
import sheets_append_values #Do not remove, passed as string
import re
from urllib.request import urlretrieve
class Reader():
    def __init__(self,inURL,outAPI,outFile=None,):
        self.inURL = inURL
        self.outAPI = outAPI
        self.outFile = outFile
        self.masterList = []
        
        if outFile is None:
            pass #Use horrible Goggle APIs to create a new Sheets file
    def _import(self):
        try:
            urlretrieve(self.inURL,"Schedule.ical")
            print("Calendar downloaded!")

        except Exception as e:
            print("Error downloading file:" + e)

        self.parse("Schedule.ical")
    def export(self):
        self.compare(self.masterList,self.readToEnd(),"uid","uid",False,
                     """sheets_append_values.append_values(self.outFile,"A5:F5","USER_ENTERED",[each.course,each.assignment,each.status,each.daysLeft,each.date]""")

        
    
    def sync(self):
        self._import()
        self.compare(self.readToEnd(),self.masterList,"uid","uid",False,
                     "self.masterList.append(each2)")
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
            new = Assignment(arglist[0],arglist[1],arglist[2],arglist[3],arglist[4],arglist[5])
            results.append(new)
        return results
    
    

    def compare(self,list1,list2,attrone,attrtwo,want,func):
        valueFound = False
        for each1 in list1:
            for each2 in list2:
                attr1 = getattr(each1, attrone)
                attr2 = getattr(each2, attrtwo)
                if attr2 == attr1:
                    valueFound = True
                else:
                    valueFound = False
                if valueFound == want:
                    exec(func)



    def parse(self,file):
        with open(file, 'r') as f:
            rows = f.readlines()
        for each in rows:
            each = each.strip()
            if each == "BEGIN:VEVENT":
                print("Found event!")
                foundEv = True
            else:
                foundEv = False
                print(each.split(":",1))
            for key,value in each.split(":",1):
                if foundEv:
                    if (key == "END"):
                        if ID and date:
                            print("Adding assignment!")
                            thing = Assignment(course,assignment,status,daysLeft,date)
                            self.masterList.append(thing)
                        else: print("Event is not assignment, skipping.")
                    if key == "DTSTAMP":
                        date = value.strip()
                        print("Found date!")
                        if date - globals.today < -(globals.threshold):
                            date = None
                            print("Assignment is too overdue, skipping.")
                    elif (key == "SUMMARY"):
                        assignment = value.strip().split("[")[0].strip("[]")
                        print("Found assignment name!")
                        course = value.strip().split("[")[1].strip("[]")
                        print("Foud assignment course!")
                    elif key == "URL;VALUE=URI":
                        backhalf  = value.split("_")[2].split("&")[0]
                        ID = re.sub(r'[^0-9]','',backhalf)
                        if ID is not None:
                            print("Found course code!")
                    status = "Not Started"
                    daysLeft = datetime.datetime.fromtimestamp(date).day() - globals.today

                
class Assignment():
    def __init__(self,course,assignment,status,daysLeft,date,uid=uuid.uuid4()):
        self.uid = uid
        self.course = course
        self.name = assignment
        self.dueDate = datetime.datetime.fromtimestamp(date)
        self.daysLeft = daysLeft
        self.status = status

    def alert(self):
        if self.daysLeft < globals.threshold: 
            return self.name
        else:
            return None

    def upDate(self):
        self.daysLeft = self.dueDate.day() - globals.today
    


        
