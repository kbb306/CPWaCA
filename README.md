# CPWaCA
The Calendar Parser Without a Cool Acronym, a homemade tool for exporting calendar files to the universal language of Google Sheets

Created by:

Kyler Belshaw

Designed by: 

Abbie Pitts

In order to connect to a google spreadsheet, you need a credentials.json file. To get one, follow the instructions [here](https://support.google.com/cloud/answer/15549257?visit_id=639005005852003510-446992105&rd=1#service-web-app&zippy=%2Cnative-applications%2Cnative-applications-android-ios-desktop-uwp-chrome-extensions-tv-and-limited-input%2Cdesktop-apps). You will neet to enable google sheets and google drive APIs Place the credentials.json file in the /data folder. 

The first time the program runs, you will be prompted for the iCal download URL and the Google Spreadsheet ID. The iCal download link can be found on your Canvas calendar tab here:
<img width="470" height="502" alt="Screenshot 2025-12-04 201415" src="https://github.com/user-attachments/assets/99e0df58-4665-4bd2-943d-ceababe82bc0" />


The Spreadsheet ID is the portion of the spreadsheet URL between d/ and /edit. If you leave this field blank when clicking submit, the program will automatically create a new spreadsheet.


Please note that the customization button is currently non-functional.
