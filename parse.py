import globals
import datetime
import sheets_update_values
import sheets_create
import sheets_get_values
import sheets_append_values 
import title
import re
from urllib.request import urlretrieve
import traceback;
from itertools import groupby
class Reader():
    def __init__(self,inURL,outFile=None,):
        self.inURL = inURL
        self.outFile = outFile
        self.masterList = []
        
        if self.outFile is None:
            self.outFile = sheets_create.create("Calendar")
        title.titleinator(self.outFile,0,20,True)
    def _import(self):
        try:
            urlretrieve(self.inURL,"Schedule.ical")
            print("Calendar downloaded!")

        except Exception as e:
            print("Error downloading file:" + e)
        self.parse("Schedule.ical")

    def append_to_sheet(self,assignment, _ignored):
        sheets_append_values.append_values(
            self.outFile,
            "A5:F",
            "USER_ENTERED",
            [[
                assignment.course,
                assignment.name,
                assignment.status,
                assignment.daysLeft,
                assignment.dueDate.isoformat() if hasattr(assignment.dueDate, "isoformat") else assignment.dueDate,
                assignment.uid,
            ]],
        )

    def update_sheet(self,assignment, _ignored):
        rows = 5
        uid = sheets_get_values.get_values(f"F{rows}:F{rows}")
        while uid != assignment.uid:
            uid = sheets_get_values.get_values(f"F{rows}:F{rows}")
            rows += 1
        sheets_update_values.update_values(
            self.outFile,
            f"A{rows}:F",
            "USER_ENTERED",
            [[
                assignment.course,
                assignment.name,
                assignment.status,
                assignment.daysLeft,
                assignment.dueDate.isoformat() if hasattr(assignment.dueDate, "isoformat") else assignment.dueDate,
                assignment.uid,
            ]],
        )

    def export(self):
        sheet_rows = self.readToEnd()
        self.compare(self.masterList,sheet_rows,"uid","uid",True,self.update_sheet)
        self.compare(self.masterList,sheet_rows,"uid","uid",False,self.append_to_sheet)
        



    def add_from_sheet(self,sheet_assignment, _match):
        # sheet_assignment is each1 from sheet_rows
        self.masterList.append(sheet_assignment)  
    
    def sync(self):
        self._import()
        rows = self.readToEnd()
        self.compare(rows,self.masterList,"uid","uid",False,self.add_from_sheet)
        self.export()



    def readToEnd(self):
        results = []
        row = 5  

        while True:
            #
            result = sheets_get_values.get_values(self.outFile, f"A{row}:F{row}")
            rows = result.get("values", [])

            # No data in this row → we're done
            if not rows:
                break

            # rows[0] is the list of cells in that row
            row_values = rows[0]

            # Pad to 6 items so we don't crash if some trailing cells are empty
            while len(row_values) < 6:
                row_values.append(None)

            course, assignment, status, daysLeft, date, uid = row_values[:6]

            new = Assignment(course, assignment, status, daysLeft, date, uid)
            results.append(new)

            row += 1

        return results

    

    def compare(self, list1, list2, attrone, attrtwo, want, func):
       
        for each1 in list1:
            match = None
            for each2 in list2:
                if getattr(each1, attrone) == getattr(each2, attrtwo):
                    match = each2
                    break

            found = match is not None
            if found == want:
                func(each1, match)


    def deduplicate(self):
            todelete =[]
            groups = [list(g) for _, g in groupby(self.masterList, key=lambda x: x.uid)]
            for each in groups:
                if len(each) > globals.tooMany:
                    each.sort(key=lambda x: (x.dueDate))
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
                        half = each.split("&", 1)[0]
                        ID = re.sub(r'[^0-9]', '', half)
                        print("Found course ID:", ID)
                        uid = ID

                    if ":" in each:
                        key, value = each.split(":",1)
                    #print(key)
                    if (key == "END"):
                        if (ID  is not None and date is not None): 
                            if ID == "1193172":
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
            return self.name,self.daysLeft
        else:
            return None

    def upDate(self):
        self.daysLeft = (self.dueDate - globals.today).days