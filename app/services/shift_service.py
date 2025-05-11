import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import sys

sys.path.append('c:/Users/User/Desktop/smartShifts/SmartShifts/app')

from models.employee import Employee
from models.time_models import ShiftDate
from models.shift_preferences import EmployeePreferences, Preference

MANAGER_SHEET_URL = "https://docs.google.com/spreadsheets/d/18uF9Q4RNBgvyM7OtA5AWHaPfbUGzFOGkbcIA_JxTbSs/edit?gid=0#gid=0"
# Define the scope for accessing Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Authorize the client using the credentials JSON file
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'c:/Users/User/Desktop/credentials.json', 
    scope
)

class ShiftService:
    def __init__(self):
        self.manager_worksheet = None
        self.employee_url_map = self._parse_manager_google_sheet()
        self.employee_preferences_map = None


    def create_monthly_shifts(self, month: int):
        self._create_employee_preference_dict(month)
        print("Hi")


    def _create_employee_preference_dict(self, month: int):
        self.employee_preferences_map = {}
        for employee_name, url in self.employee_url_map.items():
            self.employee_preferences_map[employee_name] = self._parse_employee_preference_google_sheet(url, month)


    def _parse_manager_google_sheet(self):
        client = gspread.authorize(credentials)
        sheet_id = MANAGER_SHEET_URL.split('/d/')[1].split('/')[0]
        sheet = client.open_by_key(sheet_id)
        self.manager_worksheet = sheet.worksheets()[0]
        data = self.manager_worksheet.get_all_values()
        employee_url_map = {}
        for i in data:
            employee_url_map[i[0]] = i[1]
        return employee_url_map


    def _parse_employee_preference_google_sheet(self, google_link: str, month: int):
        client = gspread.authorize(credentials)
        sheet_id = google_link.split('/d/')[1].split('/')[0]
        sheet = client.open_by_key(sheet_id)
        worksheets = sheet.worksheets()
        emp_worksheet = None
        employee_data = None
        for worksheet in worksheets:
            if worksheet.title == "general":
                general_data = worksheet.get_all_values()
                employee_name = general_data[0][1]
                employee_email = general_data[1][1]
                employee_is_manager = general_data[2][1]
                employee_data = Employee(employee_name = employee_name, email = employee_email, is_shift_manager = employee_is_manager)
                continue
            worksheet_month, _ = self._parse_sheet_name_to_ints(worksheet.title)
            if worksheet_month == month:
                emp_worksheet = worksheet
                break

        data = emp_worksheet.get_all_values()
        employee_preferences = EmployeePreferences(employee_obj = employee_data, 
                                                   preferences = self._get_preferences_from_data_table(data, emp_worksheet.title))
        
        return employee_preferences

    def _parse_sheet_name_to_ints(self, sheet_name: str):
        parts = sheet_name.split(" ")
        if len(parts) == 2:
            month_str, year_str = parts[0], parts[1]
            month = datetime.strptime(month_str, "%B").month
            year = int(year_str)
            return month, year
        else:
            raise ValueError("Sheet name format is invalid. Expected format: 'Month Year'.")

    def _get_preferences_from_data_table(self, data_table: list, sheet_name: str):
        preferences_list = []
        self.month, self.year = self._parse_sheet_name_to_ints(sheet_name)
        for i in range(1, len(data_table)):
            for j in range(1, len(data_table[i])):
                if data_table[i][0] == 'Date':
                    week_date_list = data_table[i]
                    break
                if data_table[i][0] == '' or week_date_list[j] == '':
                    break
                shift_date = ShiftDate(day=int(week_date_list[j]), month = self.month, year = self.year)
                shift_type = data_table[i][0]
                shift_preference = bool(int(data_table[i][j]))

                preferences_list.append(Preference(start_date = shift_date, shift_type = shift_type, availability = shift_preference))
        return preferences_list            
    
if __name__ == "__main__":
    emmaz = ShiftService()
    tomerz = emmaz._parse_employee_preference_google_sheet("https://docs.google.com/spreadsheets/d/1iCGT15DFkr7W93_pfUWME4yUO_byj18N1hZ9zmnGAMA/edit?gid=0#gid=0", 6)
    print(tomerz)