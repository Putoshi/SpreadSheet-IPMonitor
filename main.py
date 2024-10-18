import os
import requests
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from dotenv import load_dotenv

# .envファイルが存在する場合、それを読み込む
if os.path.exists('.env'):
    load_dotenv()

# スプレッドシートのIDと範囲
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
RANGE_NAME = f'{os.getenv("SHEET_NAME")}!A:C'  # 送り主ID、更新時間、IPアドレスを記録するための3列指定

# サービスアカウントのキーを使ってGoogle Sheets APIを認証
def get_sheets_service():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_PATH')
    if not creds_path or not os.path.exists(creds_path):
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_PATHが正しく設定されていないか、ファイルが存在しません")
    
    with open(creds_path, 'r') as f:
        creds_json = json.load(f)
    
    creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

# グローバルIPを取得
def get_global_ip():
    response = requests.get('https://api.ipify.org?format=json')
    return response.json()['ip']

# 現在の時間を取得
def get_current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 送り主ID（ラズベリーパイのホスト名）を取得
def get_sender_id():
    return os.getenv('DEVICE_ID')

# IP、時間、送り主IDをスプレッドシートに書き込み
def update_spreadsheet(ip_address, current_time, sender_id):
    service = get_sheets_service()
    
    # 既存のデータを取得
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()
    values = result.get('values', [])
    
    # sender_idが一致する行を探す
    row_index = None
    for i, row in enumerate(values):
        if row and row[0] == sender_id:
            row_index = i
            break
    
    if row_index is not None:
        # 既存の行を更新
        update_range = f'{RANGE_NAME.split("!")[0]}!A{row_index+1}:C{row_index+1}'
        body = {
            'values': [[sender_id, current_time, ip_address]]
        }
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=update_range,
            valueInputOption='RAW',
            body=body
        ).execute()
        print(f'既存の行を更新しました: {sender_id}')
    else:
        # 新しい行を追加
        body = {
            'values': [[sender_id, current_time, ip_address]]
        }
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            body=body
        ).execute()
        print(f'新しい行を追加しました: {sender_id}')

# メインの関数
if __name__ == '__main__':
    if not SPREADSHEET_ID:
        raise ValueError("SPREADSHEET_ID環境変数が設定されていません")
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS_PATH'):
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_PATH環境変数が設定されていません")

    ip_address = get_global_ip()
    current_time = get_current_time()
    sender_id = get_sender_id()
    print(f'送信者ID {sender_id}、時間 {current_time}、IPアドレス {ip_address} がスプレッドシートに書き込みます。')
    update_spreadsheet(ip_address, current_time, sender_id)
    print(f'書き込み完了')