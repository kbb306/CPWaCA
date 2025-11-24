import json
class Color:
    def __init__(self,red,green,blue,alpha):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha
        
class Rule:
    def __init__(self,rule,args):
        match rule:
            case "daysLeft":
                later = Color(args[0][0],args[0][1],args[0][2],1)
                soon = Color(args[1][0],args[1][1],args[1][2],1)
                now = Color(args[2][0],args[2][1],args[2][2],1)
                self.jsonobj = {
                    "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": 0,
                                "startRowIndex": 4,  
                                "startColumnIndex": 2, 
                                "endColumnIndex": 3    
                            }
                        ],
                        "gradientRule": {
                            "minpoint": {
                                "type": "MIN",
                                "color": {
                                    "red": later.red,
                                    "green": later.green,
                                    "blue": later.blue
                                }
                            },
                            "midpoint": {
                                "type": "PERCENTILE",
                                "value": "50",
                                "color": {
                                    "red": soon.red,
                                    "green": soon.green,
                                    "blue": soon.blue
                                }
                            },
                            "maxpoint": {
                                "type": "MAX",
                                "color": {
                                    "red": now.red,
                                    "green": now.green,
                                    "blue": now.blue
                                }
                            }
                        }
                    },
                    "index": 0
                }
            }
                
                
                
            case "type":
                exam = Color(args[0,0],args[0,1],args[0,2],args[0,3])
                optional = Color(args[1,0],args[1,1],args[1,2],args[1,3])
                essay = Color(args[2,0],args[2,1],args[2,2],args[2,3])
                project = Color(args[3,0],args[3,1],args[3,2],args[3,3])
                final = Color(args[4,0],args[4,1],args[4,2],args[4,3])
                self.jsonobj = {} # Not finished

            case "title":
                row = args[0]
                fontsize = args[1]
                bold = args[2]
                self.jsonobj = {
                    "repeatCell" : {
                        "range" : {
                            "sheetId" : 0,
                            "startRowIndex" : row,
                            "endRowIndex" : row + 1,
                            "startColumnIndex" : 0,
                            "endColumnIndex" : 5,
 
                        },
                        "cell" : {
                            "userEnteredFormat" : {
                                "horizontalAlignment" : "CENTER",
                                "textFormat" : {
                                    "bold" : bold,
                                    "fontSize" : fontsize
                                }
                            }
                        },
                        "fields" : "userEnteredFormat(horizontalAlignment,textFormat)"
                    }
                }
                
    