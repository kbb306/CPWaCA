import parse
Wyatt = parse.Reader("https://suu.instructure.com/feeds/calendars/user_MY3O6WwP5ysxV4URUoOTK03GYdmmfe4BVSOjhZcg.ics","ABCDGH")
Wyatt._import()

for each in Wyatt.masterList:
    print (each.course,each.name,each.dueDate,each.daysLeft)