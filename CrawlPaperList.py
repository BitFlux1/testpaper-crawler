from datacrypto import decrypt_request_body, encrypt_request_body
from CrawlPaperDetail import crawl_paperdetail
import requests
import uuid
import time
import json
import pickle
import os
import random

def generate_uuid_without_hyphens():
    # 生成随机UUID
    random_uuid = uuid.uuid4()
    # 将UUID转换为字符串并去除减号
    uuid_without_hyphens = str(random_uuid).replace("-", "")
    return uuid_without_hyphens

# 调用函数并打印结果

def crawl(page,provinceID):
    timestamp = int(time.time() * 1000)
    TraceId = generate_uuid_without_hyphens()
    body = f'''
    {{

    }}
    '''

    header = {
        "Content-Type": "application/json",
        "Content-Length": "536",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }
    url = f""

    encoded_body = encrypt_request_body(body.encode('utf-8')).decode('utf-8')
    response = requests.post(url = url, headers =header, data = encoded_body)
    print(response)

    if response.status_code == 200:
        decoded_response = decrypt_request_body(response.content).decode('utf-8')

        # 将 JSON 字符串解析为 Python 字典
        data_dict = json.loads(decoded_response)

        # 提取 "data" 字段中的每个对象的 "paperTitle" 和 "paperId" 字段
        new_paper_info = [(item["paperTitle"], item["paperId"]) for item in data_dict["data"]]

        pickle_file_path = 'paper_list.pkl'
        if os.path.exists(pickle_file_path):
            with open(pickle_file_path, 'rb') as f:
                paper_info = pickle.load(f)
        else:
            paper_info = []

        # 将新的数据添加到已有数据中
        paper_info.extend(new_paper_info)

        # 将合并后的数据重新写入 pickle 文件
        with open(pickle_file_path, 'wb') as f:
            pickle.dump(paper_info, f)

        print(f"新的信息已追加并保存到 {pickle_file_path} 中")

        time.sleep(random.randint(10,30))
        crawl_paperdetail()

crawl(2,440000)