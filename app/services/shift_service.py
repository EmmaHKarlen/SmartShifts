from calendar import monthrange
from fastapi import HTTPException
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import sys
from models.employee import Employee
from models.shift import WeekDayNightShift, WeekDayShift, WeekendShift
from models.time_models import ShiftDate
from models.shift_preferences import EmployeePreferences, Preference

sys.path.append('c:/Users/User/Desktop/smartShifts/SmartShifts/app')

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
        self.employee_url_map = self._parse_manager_google_sheet()
        self.employee_preferences_map = None
        self.shift_counts = {}
        self.standby_counts = {}

    def create_monthly_shifts(self, month: int):
        self._create_employee_preference_dict(month)
        shifts = []
        current_date = datetime(datetime.now().year, month, 1)

        while current_date.month == month:
            weekday = self._isr_weekday(current_date)
            shift_date = ShiftDate(day=current_date.day, month=month, year=current_date.year)

            # Weekday Shifts
            if weekday < 6:
                self._assign_weekday_shifts(shift_date, shifts)
            # Weekend Shifts
            else:
                self._assign_weekend_shift(shift_date, shifts)
            
            # Assign Standby Shift (Separate from Day/Night/Weekend)
            self._assign_standby_shift(shift_date, shifts)

            # Move to the next day
            current_date += timedelta(days=1)

        return shifts


    def _assign_weekday_shifts(self, shift_date: ShiftDate, shifts):
        try:
            day_shift = self._create_shift(shift_date, "Day", 3)
            if day_shift:
                shifts.append(day_shift)
            night_shift = self._create_shift(shift_date, "Night", 2)
            if night_shift:
                shifts.append(night_shift)
        except HTTPException as e:
            print(e.detail)


    def _assign_weekend_shift(self, shift_date, shifts):
        try:
            weekend_shift = self._create_shift(shift_date, "Weekend", 2, is_weekend=True)
            if weekend_shift:
                shifts.append(weekend_shift)
        except HTTPException as e:
            print(e.detail)


    def _assign_standby_shift(self, shift_date, shifts):
        try:
            standby_shift = self._create_shift(shift_date, "Standby", 1)
            if standby_shift:
                shifts.append(standby_shift)
        except HTTPException as e:
            print(e.detail)


    def _create_shift(self, shift_date: ShiftDate, shift_type: str, num_employees: int, is_weekend: bool = False):
        selected_employees = []
        potential_managers = []

        for employee_name, preferences in self.employee_preferences_map.items():
            for pref in preferences.preferences:
                if pref.start_date == shift_date and pref.shift_type.value == shift_type and pref.availability:
                    if shift_type == "Standby" and employee_name in self.shift_counts:
                        if "Night" in self.shift_counts[employee_name]:
                            continue
                    if not self._has_consecutive_shift(employee_name, shift_date):
                        selected_employees.append(preferences.employee_obj)
                        self._increment_shift_count(employee_name, shift_type)
                        
                        if preferences.employee_obj.is_shift_manager:
                            potential_managers.append(preferences.employee_obj)

                        if len(selected_employees) >= num_employees:
                            break

        if shift_type == "Standby" and not potential_managers:
            raise HTTPException(
                status_code=400,
                detail=f"No manager available for Standby shift on {shift_date.day}/{shift_date.month}/{shift_date.year}"
            )
        
        shift_manager = potential_managers[0] if potential_managers else None
        
        # Create the shift object
        shift_class = {
        "Day": WeekDayShift,
        "Night": WeekDayNightShift,
        "Weekend": WeekendShift
        }.get(shift_type)

        if shift_class is None:
            raise ValueError(f"Invalid shift type: {shift_type}")

        return shift_class(
            start_shift_date=shift_date,
            end_shift_date=shift_date,
            employees_list=selected_employees,
            shift_manager=shift_manager
        )


    def _has_consecutive_shift(self, employee_name: str, shift_date: ShiftDate):
        weekday = self._isr_weekday(shift_date)
        prev_day = shift_date.day - 1
        prev_month = shift_date.month
        prev_year = shift_date.year
        
        if prev_day == 0:  # Start of month
            prev_month -= 1
            if prev_month == 0:
                prev_month = 12
                prev_year -= 1
            prev_day = monthrange(prev_year, prev_month)[1]  # Get the last day of the previous month    
        
            
        prev_shift_date = ShiftDate(day=prev_day, month=prev_month, year=prev_year)

        if weekday == 6:       
            if "Night" in self.shift_counts.get(employee_name, []):
                return True
            
        if weekday == 1:  # Sunday morning
            if "Weekend" in self.shift_counts.get(employee_name, []):
                return True

        return False


    def _increment_shift_count(self, employee_name, shift_type):
        if employee_name not in self.shift_counts:
            self.shift_counts[employee_name] = []

        self.shift_counts[employee_name].append(shift_type)


    def _isr_weekday(self, shift_date: ShiftDate):
        date_obj = datetime(year=shift_date.year, month=shift_date.month, day=shift_date.day)
        return (date_obj.weekday() + 1) % 7 + 1


    def _create_employee_preference_dict(self, month: int):
        self.employee_preferences_map = {}
        for employee_name, url in self.employee_url_map.items():
            try:
                self.employee_preferences_map[employee_name] = self._parse_employee_preference_google_sheet(url, month)
            except Exception as e:
                print(f"Error parsing sheet for {employee_name}: {str(e)}")

    def _parse_manager_google_sheet(self):
        client = gspread.authorize(credentials)
        sheet_id = MANAGER_SHEET_URL.split('/d/')[1].split('/')[0]
        sheet = client.open_by_key(sheet_id)
        data = sheet.sheet1.get_all_values()
        return {row[0]: row[1] for row in data if len(row) == 2}


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