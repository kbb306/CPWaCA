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
    """Takes in iCal URL and parses out assignments, creating an Assignment object for each of them and adding them to a master list. 
    Updates/appends the google spreadsheet with those assignments """
    def __init__(self,inURL,outFile=None,):
        self.inURL = inURL
        self.outFile = outFile
        self.masterList = []
        
        if self.outFile is None:
            self.outFile = sheets_create.create("Calendar")
        title.titleinator(self.outFile,1,20,True,True,["CPWaCA Assignment Tracker"])
        title.titleinator(self.outFile,4,14,False,False,["Course","Assignment","Status","Days Left", "Due Date", "Assignment ID"])
    def _import(self):
        """Downloads the iCal file"""
        try:
            urlretrieve(self.inURL,"Schedule.ical")
            print("Calendar downloaded!")

        except Exception as e:
            print("Error downloading file:" + e)
        self.parse("Schedule.ical")

    def append_to_sheet(self,assignment, _ignored):
        """Called by compare() when an assignment in the masterlist does NOT have a match in the current spreadsheet,
        appends that assignment to the end of it."""
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
                str(assignment.uid),
            ]],
        )

    def update_sheet(self,assignment, _ignored):
        """Called by compare() when an assignment in the masterlist DOES have a match in the current spreadsheet, 
        updates that entry with the lastest data."""
        print(f"Updating assignment {assignment.uid}")
        row = 5
        while True:
            result = sheets_get_values.get_values(self.outFile,f"C{row}:F{row}")
            rows = result.get("values",[])

            if not rows:
                return
            status = rows[0][0]
            uid = rows[0][3]
            if uid == assignment.uid:
                break
            row += 1

        sheets_update_values.update_values(
            self.outFile,
            f"A{row}:F",
            "USER_ENTERED",
            [[
                assignment.course,
                assignment.name,
                status,
                assignment.daysLeft,
                assignment.dueDate.isoformat() if hasattr(assignment.dueDate, "isoformat") else assignment.dueDate,
                str(assignment.uid),
            ]],
        )

    def export(self):
        """Gets each assignment in the masterlist and asks compare() what to do with it"""
        for each in self.masterList:
            try:
                each.upDate()
            except Exception as e:
                print(f"Warning, could not update days left for assignment {each.uid}: {e}")
            print(f"Now exporting {each.name, each.uid} date {each.dueDate}. {each.daysLeft} days until due.")

        sheet_rows = self.readToEnd()
        self.compare(self.masterList,sheet_rows,"uid","uid",True,self.update_sheet)
        self.compare(self.masterList,sheet_rows,"uid","uid",False,self.append_to_sheet)
        



    def add_from_sheet(self,sheet_assignment, _match):
        """Called by compare() when an assignment is found in the spreadsheet but NOT the internal masterlist, eg, when the program restarts"""
        try:
            sheet_assignment.upDate()
        except Exception as e:
            print(f"Warning, could not update days left for assignment {sheet_assignment.uid}: {e}")
        self.masterList.append(sheet_assignment)  

    
    def sync(self):
        """Wrapper for import and export, plus a compare() call controlling add_from_sheet()"""
        rows = self.readToEnd()
        self.compare(rows,self.masterList,"uid","uid",False,self.add_from_sheet)
        self._import()
        self.export()



    def readToEnd(self):
        """Reads the spreadsheet until a blank row is found, then returns the list of entries to export()"""
        results = []
        row = 5  

        while True:
            #
            result = sheets_get_values.get_values(self.outFile, f"A{row}:F{row}")
            rows = result.get("values", [])

            if not rows:
                break

            row_values = rows[0]

            while len(row_values) < 6:
                row_values.append(None)

            course, assignment, status, daysLeft, date, uid = row_values[:6]
            uid = str(uid).strip() if uid is not None else None


            if isinstance(date,str) and date:
                try:
                    date = datetime.date.fromisoformat(date)
                except ValueError:
                    pass
            
            if uid is not None:
                uid = str(uid).strip()

            new = Assignment(course, assignment, status, daysLeft, date, uid)
            results.append(new)

            row += 1

        return results

    

    def compare(self, list1, list2, attrone, attrtwo, want, func):
        """Calls a function when a match is/is not found between two lists. Used to ensure the spreadsheet and masterlist stay in sync"""
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
            """For assignments with multiple entries in the calendar. Deletes dupes past a user-defined limit"""
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
        """The core function of the CPwACA. Reads the iCal file and creates an Assignment object for each valid assignment"""
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
                    ID = None
                    uid = None
  
                if foundEv:
                    if "#assignment" in each:
                        # Look specifically for "...assignment_12345678"
                        m = re.search(r'assignment_(\d+)', each)
                        if m:
                            ID = m.group(1)          # e.g. "17159689"
                            uid = ID                 # keep as string
                            print("Found assignment ID:", ID)
                        else:
                            # Fallback if for some reason the pattern isn't there
                            print("Could not find assignment_... in line:", each)
                            ID = None
                            uid = None


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
    """The internal representation of an assignment. Stores unique assignment ID, the course name, the name/title,
    the due date, and the days from today until the due date."""
    def __init__(self,course,assignment,status,daysLeft,date,uid):
        self.uid = uid
        self.course = course
        self.name = assignment
        self.dueDate = date
        self.daysLeft = daysLeft
        self.status = status

    def alert(self):
        """Called by the gui's dateCheck function. Returns the assignment's name and daysLeft if more than x days overdue"""
        if (self.daysLeft <= globals.threshold and self.daysLeft >= -(globals.threshold) and self.status != "Done"): 
            return self.name,self.daysLeft
        else:
            return None

    def upDate(self):
        """Called by multiple functions in the gui. Updates the days left until the due date."""
        self.daysLeft = (self.dueDate - globals.today).days