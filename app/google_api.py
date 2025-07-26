import gspread
from oauth2client.service_account import ServiceAccountCredentials
from app.config import GOOGLE_CREDENTIALS_JSON, GOOGLE_SHEET_ID

# Подключение к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_JSON, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(GOOGLE_SHEET_ID)

# 📌 Получение списка имён менеджеров
def get_manager_names():
    worksheet = sheet.worksheet("Менеджеры")
    return worksheet.col_values(1)[1:]  # пропустить заголовок

# 📌 Получение статистики по username
def get_manager_stats(username: str):
    worksheet = sheet.worksheet("Менеджеры")
    all_data = worksheet.get_all_records()
    for row in all_data:
        if str(row.get("username", "")).strip().lower() == str(username).strip().lower():
            return row
    return None

# 📌 Получение плана продаж
def get_sales_plan():
    worksheet = sheet.worksheet("План")
    return worksheet.get_all_records(expected_headers=["день", "месяц"])

# 📌 Обновление username по имени менеджера
def update_manager_username(name: str, username: str):
    worksheet = sheet.worksheet("Менеджеры")
    all_data = worksheet.get_all_records()

    for idx, row in enumerate(all_data, start=2):  # данные начинаются со 2-й строки
        if str(row.get("Имя")).strip().lower() == str(name).strip().lower():
            col_index = get_column_index("username", worksheet)
            worksheet.update_cell(idx, col_index, username)
            break

# 🔍 Поиск колонки по названию
def get_column_index(header: str, worksheet):
    headers = worksheet.row_values(1)
    for i, h in enumerate(headers, start=1):
        if h.strip().lower() == header.strip().lower():
            return i
    raise ValueError(f"Колонка '{header}' не найдена")
