"""
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


"""

# [START sheets_merge]
import authorize
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def run(spreadsheet_id,command):
  """
  Creates the batch_update the user has access to.
  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.

  Reference for range:

   my_range = {
        "sheetId": 0,
        "startRowIndex": 1,
        "endRowIndex": 11,
        "startColumnIndex": 0,
        "endColumnIndex": 4,
    }
  """
  creds, _ = authorize.authcheck()
  # pylint: disable=maybe-no-member
  try:
    service = build("sheets", "v4", credentials=creds)

    
    requests = [command]
    body = {"requests": requests}
    response = (
        service.spreadsheets()
        .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
        .execute()
    )
    print(f"{(len(response.get('replies')))} cells updated.")
    return response

  except HttpError as error:
    print(f"An error occurred: {error}")
    return error


if __name__ == "__main__":
  # Pass: spreadsheet_id
  merge("1CM29gwKIzeXsAppeNwrc8lbYaVMmUclprLuLYuHog4k")
  # [END sheets_merge]
