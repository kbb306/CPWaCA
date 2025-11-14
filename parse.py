import globals
import uuid
import datetime
import sheets_update_values
import sheets_get_values
import sheets_append_values #Do not remove, passed as string
import re
from urllib.request import urlretrieve
import traceback;
from itertools import groupby
class Reader():
    def __init__(self,inURL,outFile=None,):
        self.inURL = inURL
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

    def deduplicate(self):
            todelete =[]
            groups = [list(g) for _, g in groupby(self.masterList, key=lambda x: x.uid)]
            for each in groups:
                each.sort(key=lambda x: (x.duedate))
                latest = each[-1].dueDate
                for day in each:
                    if day.dueDate < latest:
                        todelete.append(day)
            for each in todelete:
                ind = self.masterList.index(each)
                del(self.masterList[ind])
                


    
        
        

    def parse(self,file):
        foundEv = False
        with open(file, 'r') as f:
            rows = f.readlines()
        for each in rows:
            try:
                each = each.strip()
                if each == "BEGIN:VEVENT":
                    print("Found event!")
                    foundEv = True
                    date= None
  
                
                
                if foundEv:
                    if "#assignment" in each:
                        half = each.split("&",1)[0]
                        ID = re.sub(r'[^0-9]','',half)
                        print("Found course ID:",ID)
                        uid = each.split("#",1)
                    if ":" in each:
                        key, value = each.split(":",1)
                    #print(key)
                    if (key == "END"):
                        if (ID  is not None and date is not None): 
                            if ID == 1193172:
                                continue
                            print("Adding assignment!")
                            thing = Assignment(course,assignment,status,daysLeft,date,uid)
                            self.masterList.append(thing)
                            foundEv = False
                        
                    if key == "DTSTART;VALUE=DATE;VALUE=DATE":
                        datein = value.strip()
                        print("Found date!")
                        date = (datetime.datetime.strptime(datein,"%Y%m%d")).date()
                        #print((date - globals.today))
                        if (date - globals.today).days < -(globals.threshold):
                            date = None
                            print("Assignment is too overdue, skipping.")
                            foundEv = False
                            continue
                        
                    elif (key == "SUMMARY"):
                        if "[" in value:
                            assignment = value.strip().split("[")[0].strip("[]")
                            print("Found assignment name!")
                            course = value.strip().split("[")[1].strip("[]")
                            print("Found assignment course!")
                        else:
                            print("Not an assignment, skipping")
                            continue
                        
                    status = "Not Started"
                    if date is not None:
                        daysLeft = (date - globals.today).days
                        #print(daysLeft)
            except Exception as e:
                print("Failed to parse", (each.split(":",1)[1]),e,traceback.print_exc())
                break
            self.deduplicate()    
class Assignment():
    def __init__(self,course,assignment,status,daysLeft,date,uid):
        self.uid = uid
        self.course = course
        self.name = assignment
        self.dueDate = date
        self.daysLeft = daysLeft
        self.status = status

    def alert(self):
        if self.daysLeft <= globals.threshold: 
            return self.name
        else:
            return None

    def upDate(self):
        self.daysLeft = (self.dueDate - globals.today).days
    


        
