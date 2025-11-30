import unittest
from parse import Reader, Assignment, sheets_get_values
from io import StringIO
import sys
import os
import datetime
import random
import sheets_clear_values

class testReader(unittest.TestCase):

    def test_init(self):
        Wyatt = Reader("https://suu.instructure.com/feeds/calendars/user_MY3O6WwP5ysxV4URUoOTK03GYdmmfe4BVSOjhZcg.ics","1IY3A-mZwVB94UFqShO-QZuYDGYZaYPLcLbVfHv7Txt8")
        empty = []
        self.assertEqual(len(Wyatt.masterList),len(empty))
    
    def test_import(self):
        Wyatt = Reader("https://suu.instructure.com/feeds/calendars/user_MY3O6WwP5ysxV4URUoOTK03GYdmmfe4BVSOjhZcg.ics","1IY3A-mZwVB94UFqShO-QZuYDGYZaYPLcLbVfHv7Txt8")
        Wyatt._import()
        self.assertTrue(os.path.exists("Schedule.ical"))

    def test_append_to_sheet(self):
        Bob = Assignment("Standing Up Class","Stand Up for 5 Seconds","Not Started",5,(datetime.datetime.date.today()+datetime.timedelta(days=5)),random.randint(10000000,99999999))
        Wyatt = Reader("https://suu.instructure.com/feeds/calendars/user_MY3O6WwP5ysxV4URUoOTK03GYdmmfe4BVSOjhZcg.ics","1IY3A-mZwVB94UFqShO-QZuYDGYZaYPLcLbVfHv7Txt8")
        Wyatt.append_to_sheet(Bob)
        result = sheets_get_values(Wyatt.outFile,"A5:F")
        rows = result.get("values",[])
        row = rows[0]
        course, assignment, status, daysleft, date, uid = row[:6] 
        self.assertEqual(Bob.course,course)
        self.assertEqual(Bob.name,assignment)
        self.assertEqual(Bob.status,status)
        self.assertEqual(Bob.daysLeft,daysleft)
        self.assertEqual(Bob.dueDate,date)
        self.assertEqual(Bob.uid,uid)


        sheets_clear_values(Wyatt.outFile,"A1:Z")

    def test_update_sheet(self):
        Wyatt = Reader("https://suu.instructure.com/feeds/calendars/user_MY3O6WwP5ysxV4URUoOTK03GYdmmfe4BVSOjhZcg.ics","1IY3A-mZwVB94UFqShO-QZuYDGYZaYPLcLbVfHv7Txt8")
        Bob = Assignment("Standing Up Class","Stand Up for 5 Seconds","Not Started",5,(datetime.datetime.date.today()+datetime.timedelta(days=5)),random.randint(10000000,99999999))
        Wyatt.append_to_sheet(Bob)
        Bob.daysLeft = 4
        Wyatt.update_sheet(Bob)
        self.assertEqual(Bob.daysLeft,4)

    def test_compare(self):

        def CheckSame(thing1,thing2):
            self.assertEqual(thing1,thing2)

        def CheckDiff(thing1, thing2):
            self.assertNotEqual(thing1,thing2)
        

        class Dummy():
            def __init__(self,foo,bar):
                self.foo = foo
                self.bar = bar

        Wyatt = Reader("https://suu.instructure.com/feeds/calendars/user_MY3O6WwP5ysxV4URUoOTK03GYdmmfe4BVSOjhZcg.ics","1IY3A-mZwVB94UFqShO-QZuYDGYZaYPLcLbVfHv7Txt8")
        
        Alice = Dummy(1,0)
        Bob = Dummy(0,1)

        list1 = [Bob]
        list2 = [Alice]
        list3 = [Alice, Bob]
        list4 = [Bob, Alice]

        Wyatt.compare(list1,list1,"foo","foo",True,CheckSame)
        Wyatt.compare(list1,list1,"bar","bar",True,CheckSame)
        Wyatt.compare(list2,list2,"foo","foo",True,CheckSame)
        Wyatt.compare(list2,list2,"bar","bar",True,CheckSame)

        Wyatt.compare(list1,list2,"foo","bar",True,CheckSame)
        Wyatt.compare(list1,list2,"bar","foo",True,CheckSame)
        Wyatt.compare(list2,list1,"foo","bar",True,CheckSame)
        Wyatt.compare(list2,list1,"bar","foo",True,CheckSame)

        Wyatt.compare(list1,list2,"foo","foo",False,CheckDiff)
        Wyatt.compare(list1,list2,"bar","bar",False,CheckDiff)
        Wyatt.compare(list2,list1,"foo","foo",False,CheckDiff)
        Wyatt.compare(list2,list1,"bar","bar",False,CheckDiff)

        Wyatt.compare(list3,list3,"foo","foo",True,CheckSame)
        Wyatt.compare(list3,list3,"bar","bar",True,CheckSame)
        Wyatt.compare(list4,list4,"foo","foo",True,CheckSame)
        Wyatt.compare(list4,list4,"bar","bar",True,CheckSame)

        Wyatt.compare(list3,list4,"foo","bar",True,CheckSame)
        Wyatt.compare(list3,list4,"bar","foo",True,CheckSame)
        Wyatt.compare(list4,list3,"foo","bar",True,CheckSame)
        Wyatt.compare(list4,list3,"bar","foo",True,CheckSame)

        Wyatt.compare(list3,list4,"foo","foo",False,CheckDiff)
        Wyatt.compare(list3,list4,"bar","bar",False,CheckDiff)
        Wyatt.compare(list4,list3,"foo","foo",False,CheckDiff)
        Wyatt.compare(list4,list3,"bar","bar",False,CheckDiff)

        Wyatt.compare(list1,list4,"foo","bar",True,CheckSame)
        Wyatt.compare(list1,list4,"bar","foo",True,CheckSame)
        Wyatt.compare(list4,list1,"foo","bar",True,CheckSame)
        Wyatt.compare(list4,list1,"bar","foo",True,CheckSame)

        Wyatt.compare(list1,list4,"foo","foo",False,CheckDiff)
        Wyatt.compare(list1,list4,"bar","bar",False,CheckDiff)
        Wyatt.compare(list4,list1,"foo","foo",False,CheckDiff)
        Wyatt.compare(list4,list1,"bar","bar",False,CheckDiff)

        Wyatt.compare(list2,list3,"foo","bar",True,CheckSame)
        Wyatt.compare(list2,list3,"bar","foo",True,CheckSame)
        Wyatt.compare(list3,list2,"foo","bar",True,CheckSame)
        Wyatt.compare(list3,list2,"bar","foo",True,CheckSame)

        Wyatt.compare(list2,list3,"foo","foo",False,CheckDiff)
        Wyatt.compare(list2,list3,"bar","bar",False,CheckDiff)
        Wyatt.compare(list3,list2,"foo","foo",False,CheckDiff)
        Wyatt.compare(list3,list2,"bar","bar",False,CheckDiff)

        Wyatt.compare(list1,list3,"foo","bar",True,CheckSame)
        Wyatt.compare(list1,list3,"bar","foo",True,CheckSame)
        Wyatt.compare(list3,list1,"foo","bar",True,CheckSame)
        Wyatt.compare(list3,list1,"bar","foo",True,CheckSame)

        Wyatt.compare(list1,list3,"foo","foo",False,CheckDiff)
        Wyatt.compare(list1,list3,"bar","bar",False,CheckDiff)
        Wyatt.compare(list3,list1,"foo","foo",False,CheckDiff)
        Wyatt.compare(list3,list1,"bar","bar",False,CheckDiff)

        Wyatt.compare(list2,list4,"foo","bar",True,CheckSame)
        Wyatt.compare(list2,list4,"bar","foo",True,CheckSame)
        Wyatt.compare(list4,list2,"foo","bar",True,CheckSame)
        Wyatt.compare(list4,list2,"bar","foo",True,CheckSame)

        Wyatt.compare(list2,list4,"foo","foo",False,CheckDiff)
        Wyatt.compare(list2,list4,"bar","bar",False,CheckDiff)
        Wyatt.compare(list4,list2,"foo","foo",False,CheckDiff)
        Wyatt.compare(list4,list2,"bar","bar",False,CheckDiff)


    def test_readToEnd(self):
        Wyatt = Reader("https://suu.instructure.com/feeds/calendars/user_MY3O6WwP5ysxV4URUoOTK03GYdmmfe4BVSOjhZcg.ics","1IY3A-mZwVB94UFqShO-QZuYDGYZaYPLcLbVfHv7Txt8")
        Bob = Assignment("Standing Up Class","Stand Up for 5 Seconds","Not Started",5,(datetime.datetime.date.today()+datetime.timedelta(days=5)),random.randint(10000000,99999999))
        Alice = Assignment("Breathing 101","Breathe In","Not Started",5,(datetime.datetime.date.today()+datetime.timedelta(days=5)),random.randint(10000000,99999999))

        Wyatt.append_to_sheet(Bob)
        Wyatt.append_to_sheet(Alice)
        toTest = Wyatt.readToEnd()
        result = sheets_get_values.get_values(Wyatt.outFile,"A5:F6")
        rows = result.get("values",[])
        for i in len(rows):
            row = rows[i]
            if len(row) < 6:
                row.append(None)
            course, assignment, status, daysleft, date, uid = row[:6] 
            matching = False
            for each in toTest:
                if (each.course == course and each.name == assignment and each.status == status and each.daysleft == daysleft and each.date == date and each.uid == uid):
                    matching = True
                else: 
                    matching = False
        self.assertTrue(matching)
                
            

    def test_export(self):
        Wyatt = Reader("https://suu.instructure.com/feeds/calendars/user_MY3O6WwP5ysxV4URUoOTK03GYdmmfe4BVSOjhZcg.ics","1IY3A-mZwVB94UFqShO-QZuYDGYZaYPLcLbVfHv7Txt8")
        Bob = Assignment("Standing Up Class","Stand Up for 5 Seconds","Not Started",5,(datetime.datetime.date.today()+datetime.timedelta(days=5)),random.randint(10000000,99999999))
        Alice = Assignment("Breathing 101","Breathe In","Not Started",7,(datetime.datetime.date.today()+datetime.timedelta(days=7)))
        Wyatt.masterList.append(Bob)
        Wyatt.masterList.append(Alice)
        Wyatt.export()
        
    
    def test_add_from_sheet(self):
        Wyatt = Reader("https://suu.instructure.com/feeds/calendars/user_MY3O6WwP5ysxV4URUoOTK03GYdmmfe4BVSOjhZcg.ics","1IY3A-mZwVB94UFqShO-QZuYDGYZaYPLcLbVfHv7Txt8")
        Bob = Assignment("Standing Up Class","Stand Up for 5 Seconds","Not Started",5,(datetime.datetime.date.today()+datetime.timedelta(days=5)),random.randint(10000000,99999999))
        Alice = Assignment("Breathing 101","Breathe In","Not Started",7,(datetime.datetime.date.today()+datetime.timedelta(days=7)))
        Wyatt.masterList.append(Bob)
        Wyatt.masterList.append(Alice)
        Wyatt.export()
        Red = Reader("https://suu.instructure.com/feeds/calendars/user_MY3O6WwP5ysxV4URUoOTK03GYdmmfe4BVSOjhZcg.ics","1IY3A-mZwVB94UFqShO-QZuYDGYZaYPLcLbVfHv7Txt8")
        for each in Wyatt.masterList:
            Red.add_from_sheet(each)
        Equal = False
        for each in Red.masterList:
            for each2 in Wyatt.masterList:
                if each2.uid == each.uid:
                    if each2.name == each.name:
                        if each2.course == each.course:
                            if each2.dueDate == each.dueDate:
                                if each2.daysLeft == each.daysLeft:
                                    Equal = True
                                    break
                else: 
                    Equal = False
        self.assertTrue(Equal)
               
    def test_deduplicate(self):
        Wyatt = Reader("https://suu.instructure.com/feeds/calendars/user_MY3O6WwP5ysxV4URUoOTK03GYdmmfe4BVSOjhZcg.ics","1IY3A-mZwVB94UFqShO-QZuYDGYZaYPLcLbVfHv7Txt8")
        Bob = Assignment("Standing Up Class","Stand Up for 5 Seconds","Not Started",5,(datetime.datetime.date.today()+datetime.timedelta(days=5)),random.randint(10000000,99999999))
        Alice = Assignment("Standing Up Class","Stand Up for 5 Seconds","Not Started",6,(datetime.datetime.date.today()+datetime.timedelta(days=6)),Bob.uid)
        Jane = Assignment("Standing Up Class","Stand Up for 5 Seconds","Not Started",7,(datetime.datetime.date.today()+datetime.timedelta(days=7)),Bob.uid)
        Janet = Assignment("Standing Up Class","Stand Up for 5 Seconds","Not Started",8,(datetime.datetime.date.today()+datetime.timedelta(days=8)),Bob.uid)
        Judy = Assignment("Standing Up Class","Stand Up for 5 Seconds","Not Started",9,(datetime.datetime.date.today()+datetime.timedelta(days=9)),Bob.uid)


        Wyatt.masterList.append(Bob)
        Wyatt.masterList.append(Alice)
        Wyatt.masterList.append(Jane)
        Wyatt.deduplicate()
        for each in Wyatt.masterList:
            if each.daysLeft == 9:
                check = True
            else:
                check = False
        self.assertTrue(check)

        


    def test_parse(self):
        pass



