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
    """Creates Assignment objects using data pulled from a downloaded iCal file, and reads/writes them to a spreadsheet
    """
    def __init__(self,inURL,outFile=None,):
        """Constructor for Reader class

        Args:
            inURL (string): download URL for iCal file
            outFile (string, optional): Spreadsheet ID for the spreadsheet we are outputting to. if not provided, Reader will create a new Google Spreadsheet. Defaults to None.
        """
        self.inURL = inURL
        self.outFile = outFile
        self.masterList = []
        
        if self.outFile is None:
            self.outFile = sheets_create.create("Calendar")
        title.titleinator(self.outFile,1,20,True,True,["CPWaCA Assignment Tracker"])
        title.titleinator(self.outFile,4,14,False,False,["Course","Assignment","Status","Days Left", "Due Date", "Assignment ID"])
    
    def _import(self):
        """Download the iCal file
           Attributes Used: self.inURL
           Creates: Schedule.ical
           Raises: URLError if download fails"""
        try:
            urlretrieve(self.inURL,"Schedule.ical")
            print("Calendar downloaded!")

        except Exception as e:
            raise e
        self.parse("Schedule.ical")

    def append_to_sheet(self,assignment, _ignored):
        """Append the data in an Assignment object to the spreadsheet as a new row

        Args:
            assignment (Assignment): An assignment in the masterlist that does not have a match in the spreadsheet. 
                passed from compare().
            _ignored (Assignment): Placeholder for uniform call structure in compare()
        """
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
        """Updates a row in the spreadsheet with the latest version of the assignment

        Args:
            assignment (Assignment): An Assignment present in the masterlist AND the spreadsheet. Passed from compare()
            _ignored (Assignment): Placeholder for uniform call structure in compare()
        """
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
        """Call compare to determine correct action for each assignment in masterlist.
        """

        sheet_rows = self.readToEnd()
        self.compare(self.masterList,sheet_rows,"uid","uid",True,self.update_sheet)
        self.compare(self.masterList,sheet_rows,"uid","uid",False,self.append_to_sheet)
        

    def add_from_sheet(self,sheet_assignment, _match):
        """Add assignment from sheet to masterlist

        Args:
            sheet_assignment (Assignment): An Assignment object generated from the sheet. Passed from compare()
            _match (Assignment): Placeholder for uniform call structure in compare()
        """
        try:
            sheet_assignment.upDate()
        except Exception as e:
            print(f"Warning, could not update days left for assignment {sheet_assignment.uid}: {e}")
        self.masterList.append(sheet_assignment)  

    
    def sync(self):
        """Synchronize google spreadsheet and masterlist
        """
        rows = self.readToEnd()
        self.compare(rows,self.masterList,"uid","uid",False,self.add_from_sheet)
        self._import()
        self.export()


    def readToEnd(self):
        """
        Read spreadsheet (starting at row 5) until a blank row. Create Assignment objects for each and return them in a list.
        """
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
        """Compares lists according to given attributes, calls function when given condition is met.

        Args:
            list1 (list): The list to compare against
            list2 (list): The list being compared
            attrone (any): The attribute to compare for each object in list1
            attrtwo (any): The attribute to compare for each object in list2
            want (bool): The condition on which func() executes. If set to false, function will execute when comparison test fails
            func (function): The function called when the match test returns a bool matching want
        """
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
            """Locate duplicate assignments above a user defined threshold. Keep those with later due dates and delete the rest
            """
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
        """Read iCal file and parse out events and their attributes. Creates Assignment objects.
            If any attributes known to occur in assignments are missing, object creation is aborted.

        Args:
            file (str): The path to an iCal file, passed from _import()
        """
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
                    skip = False
  
                if foundEv:
                    if "#assignment" in each:
                        m = re.search(r'assignment_(\d+)', each)
                        if m:
                            ID = m.group(1)          
                            uid = ID                 
                            print("Found assignment ID:", ID)
                        else:
                            print("Could not find assignment_... in line:", each)
                            ID = None
                            uid = None


                    if ":" in each:
                        key, value = each.split(":",1)
                    if (key == "END"):
                        if (ID  is not None and date is not None): 
                            if ID == "1193172":
                                continue
                            for each in self.masterList:
                                if uid == each.uid:
                                    skip = True
                            if not skip:
                                print("Adding assignment!")
                                thing = Assignment(course,assignment,status,daysLeft,date,uid)
                                self.masterList.append(thing)
                            else:
                                print("Assignment already in masterlist")
                            foundEv = False
                            skip = False
                        
                    if key == "DTSTART;VALUE=DATE;VALUE=DATE":
                        datein = value.strip()
                        print("Found date!")
                        date = (datetime.datetime.strptime(datein,"%Y%m%d")).date()
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
        """Constructor for Assignment class

        Args:
            course (string): The course that gave this assignment
            assignment (string): Assignment name and/or description
            status (string): "Not Started," "In Progress," or "Done"
            daysLeft (int): Days until the assignment is due
            date (date): Assignment due date
            uid (int): Unique assignment ID, found at the end of the URL in the iCal event.
        """
        self.uid = uid
        self.course = course
        self.name = assignment
        self.dueDate = date
        self.daysLeft = daysLeft
        self.status = status

    def alert(self):
        """Check daysLeft against globals.threshold. If the difference is within |threshold|, return name and daysLeft

        Returns:
            tuple: (self.name,self.daysleft)
        """
        if (self.daysLeft <= globals.threshold and self.daysLeft >= -(globals.threshold) and self.status != "Done"): 
            return self.name,self.daysLeft
        else:
            return None

    def upDate(self):
        """Subtract globals.today from self.dueDate
        """
        self.daysLeft = (self.dueDate - globals.today).days
