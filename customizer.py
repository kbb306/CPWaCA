import sheets_conditional_formatting
def buildRule(rule,args):
    match rule:
        case "daysLeft":
            notDue, dueSoon, overDue = args
        case "type":
            quizColor, optionalColor, essayColor, finalColor = args