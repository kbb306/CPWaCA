import globals
import sheets_update_values
import sheets_conditional_formatting
import sheets_misc
import json
import customizer
def titleinator(driveFile,row,fontsize,bold):
        formatting = customizer.Rule("title",[row,fontsize,bold])
        command  = {
                "mergeCells" : {
                        "range" : {
                                "sheetId" : 0,
                                "startRowIndex" : row,
                                "endRowIndex" : row + 1,
                                "startColumnIndex" : 0,
                                "endColumnIndex" : 6,
                        },
                        "mergeType" : "MERGE_ALL"
                }
        }
        
        sheets_misc.run(driveFile,command)
        sheets_conditional_formatting.conditional_formatting(driveFile,formatting.jsonobj)
        sheets_update_values.update_values(driveFile,f"A{row+1}:F","USER_ENTERED",[["CPWaCA Assignment Tracker"]])