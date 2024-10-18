## SpreadSheet-IPMonitor


## 準備

### 1. Get certification json
https://console.cloud.google.com/

認証情報jsonを生成して、.cert.jsonにして保存


### 2. 共有設定
スプレッドシートを作り、共有設定をして、上記json内にある[client_email]のアドレスに共有招待を送る

## 開発環境の構築 
Python 3.9

### 1. Install 
```
conda env create -f environment.yml

or

pip install python-dotenv google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client requests

```

### 2. .envの作成
```
DEVICE_ID=test
SPREADSHEET_ID=********** ※https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]
SHEET_NAME=**********
GOOGLE_APPLICATION_CREDENTIALS_PATH=./**********.cert.json
``` 

## 実行
```
python main.py
```

