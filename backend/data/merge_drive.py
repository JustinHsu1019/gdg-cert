import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 使用 service account 進行驗證
SERVICE_ACCOUNT_FILE = 'backend/cred.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

# 設定你的 Google Drive 資料夾 ID
FOLDER_ID = "YOUR_FOLDER_ID"

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)

def list_pdfs_in_folder(drive_service, folder_id):
    query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    return items

def get_shareable_link(drive_service, file_id):
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    drive_service.permissions().create(fileId=file_id, body=permission).execute()
    link = f"https://drive.google.com/file/d/{file_id}/view"
    return link

def save_json_to_file(json_data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    output_json_file = "data/id_url.json"
    
    drive_service = get_drive_service()
    pdf_files = list_pdfs_in_folder(drive_service, FOLDER_ID)
    
    pdf_links = []
    for file in pdf_files:
        file_id = file['id']
        link = get_shareable_link(drive_service, file_id)
        pdf_links.append({"filename": file['name'], "link": link})
    
    save_json_to_file(pdf_links, output_json_file)
    
    print(f"PDF 檔案及共用連結已儲存到 {output_json_file}")
