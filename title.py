import globals
import sheets_update_values
import sheets_conditional_formatting
import sheets_misc
import json
import customizer
def titleinator(driveFile,row,fontsize,merge,bold,data):
        formatting = customizer.Rule("title",[row,fontsize,bold])
        if merge:
                command  = {
                        "mergeCells" : {
                                "range" : {
                                        "sheetId" : 0,
                                        "startRowIndex" : row - 1,
                                        "endRowIndex" : row,
                                        "startColumnIndex" : 0,
                                        "endColumnIndex" : 6,
                                },
                                "mergeType" : "MERGE_ALL"
                        }
                }
                
                sheets_misc.run(driveFile,command)
        sheets_conditional_formatting.conditional_formatting(driveFile,formatting.jsonobj)
        sheets_update_values.update_values(driveFile,f"A{row}:F","USER_ENTERED",[data])