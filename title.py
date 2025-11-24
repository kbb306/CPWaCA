import globals
import sheets_update_values
import sheets_conditional_formatting
import sheets_misc
import json
import customizer
def titleinator(driveFile,row,fontsize,bold):
        formatting = customizer.Rule("title",[row,fontsize,bold])
        command_payload = {
                "mergeCells" : {
                        "range" : {
                                "sheetID" : 0,
                                "startRowIndex" : row,
                                "endRowIndex" : row + 1,
                                "startColumnIndex" : 0,
                                "endColumnIndex" : 5,
                        },
                        "mergeType" : "MERGE_ALL"
                }
        }
        command = json.dumps(command_payload)
        sheets_misc.run(command)
        sheets_conditional_formatting.conditional_formatting(formatting.jsonobj)
        sheets_update_values.update_values(driveFile,f"A{row+1}:F",[["CPWaCA Assignment Tracker"]])