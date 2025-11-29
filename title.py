import globals
import sheets_update_values
import sheets_conditional_formatting
import sheets_misc
import json
import customizer
def titleinator(driveFile,row,fontsize,merge,bold,data):
        """Create title or subtitle on given row with given formatting

        Args:
            driveFile (string): The Spreadsheet ID for the spreadsheet we wish to modify
            row (int): The row to place the title/subtitle on
            fontsize (int): The size of the text in the title/subtitlt
            merge (bool): Whether or not to merge all the cells in a row
            bold (bool): Whether or not the text should be bold
            data (list): The list of data to place in the row
        """
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