import json
import csv

# 讀取 .json 檔案
with open('data/processed_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 開啟或建立 .csv 檔案
with open('data/output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['name', 'project_id', 'cert_id']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # 處理每個資料項
    for item in data:
        if item.get('core_or_not'):
            # 提取最後一個 hash（假設是 hash_2，如果沒有則用 hash_1）
            cert_id = item['hash'].get('hash_2', item['hash'].get('hash_1'))
            
            # 寫入 csv
            writer.writerow({
                'name': item['name'],
                'project_id': 'Core Team',
                'cert_id': cert_id
            })

print("CSV 轉換完成！")
