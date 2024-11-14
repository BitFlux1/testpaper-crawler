import pickle
import os
from datacrypto import encrypt_request_body,decrypt_request_body
from dataclean import clean_html


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
def crawl(paperID):
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

    print(f"get response {response.status_code}")
    decoded_response = decrypt_request_body(response.content).decode('utf-8')
    return decoded_response


# 处理JSON数据的函数
def validate_json_structure(input_json):
    """
    验证输入的 JSON 是否具有预期的结构，并输出具体的错误位置。
    """
    try:
        # 检查 'data' 是否存在且为字典
        if not isinstance(input_json.get("data"), dict):
            return False, "'data' is missing or not a dictionary."

        # 检查 'paperSections' 是否为列表
        paper_sections = input_json["data"].get("paperSections", [])
        if not isinstance(paper_sections, list):
            return False, "'paperSections' is missing or not a list."

        for section in paper_sections:
            if not isinstance(section, dict):
                return False, "A section in 'paperSections' is not a dictionary."

            # 检查 'sectionName' 是否为字符串且值为 "解答题"
            if section.get("sectionName") == "解答题":
                # 检查 'questionSections' 是否为列表
                question_sections = section.get("questionSections", [])
                if not isinstance(question_sections, list):
                    return False, "'questionSections' is missing or not a list."

                for question_section in question_sections:
                    if not isinstance(question_section, dict):
                        return False, "A question_section in 'questionSections' is not a dictionary."

                    # 检查 'question' 是否为字典
                    question = question_section.get("question", {})
                    if not isinstance(question, dict):
                        return False, "'question' is missing or not a dictionary."

                    # 检查 'question' 内部字段是否存在且类型正确
                    if not isinstance(question.get("id"), (str, int)):
                        return False, "'id' in 'question' is missing or not a string or integer."
                    if not isinstance(question.get("knowledge"), list):
                        return False, "'knowledge' in 'question' is missing or not a list."
                    # if not isinstance(question.get("labelFields", {}).get("topicclass"), list):
                    #     return False, "'topicclass' in 'labelFields' is missing or not a list."
                    if not isinstance(question.get("difficulty"), dict):
                        return False, "'difficulty' in 'question' is missing or not a dictionary."
                    if not isinstance(question.get("answerWithStyle"), str):
                        return False, "'answerWithStyle' in 'question' is missing or not a string."
                    if not isinstance(question.get("contentWithStyle"), str):
                        return False, "'contentWithStyle' in 'question' is missing or not a string."
                    if not isinstance(question.get("analysisWithStyle"), str):
                        return False, "'analysisWithStyle' in 'question' is missing or not a string."

        return True, "JSON structure is valid."
    except Exception as e:
        return False, f"Error validating JSON structure: {e}"


def process_json(input_json):
    # 首先检查 JSON 结构是否正确
    is_valid, message = validate_json_structure(input_json)
    if not is_valid:
        print(f"Invalid JSON structure: {message}")
        return []

    # 初始化结果列表
    result = []

    # 直接处理，因为我们已经确认结构是完整的
    paper_sections = input_json["data"]["paperSections"]

    # 遍历所有的一级对象
    for section in paper_sections:
        if section["sectionName"] == "解答题":
            # 遍历["questionSections"]字段中的所有对象
            question_sections = section["questionSections"]
            for question_section in question_sections:
                question = question_section["question"]

                # 构建新的 JSON 对象
                new_json_obj = {
                    "id": str(question["id"]),  # 确认字段存在后直接使用
                    "knowledge": question["knowledge"],
                    #"topicclass": question["labelFields"]["topicclass"],
                    "difficulty": question["difficulty"],
                    "answerWithStyle": clean_html(question["answerWithStyle"],keep_newlines=False, keep_images=False),
                    "contentWithStyle": clean_html(question["contentWithStyle"],keep_newlines=False, keep_images=False),
                    "analysisWithStyle": clean_html(question["analysisWithStyle"],keep_newlines=False, keep_images=False)
                }

                # 将新的 JSON 对象加入到结果列表
                result.append(new_json_obj)

    return result


def process_paperID(paperTitle,paperID):

    decoded_response = json.loads(crawl(paperID))
    Readable_filepath = f"./readable/{paperTitle}.json"

    os.makedirs("./readable",exist_ok= True)
    with open(Readable_filepath,"w",encoding='utf-8') as file:
        json.dump(decoded_response["data"],file,ensure_ascii=False,indent=4)

    filepath = f"./normalpaper/{paperID}.json"
    os.makedirs("./normalpaper",exist_ok=True)
    with open(filepath,"w",encoding='utf-8') as file:
        json.dump(decoded_response["data"],file,ensure_ascii=False,indent=4)

    # 处理JSON数据
    processed_data = process_json(decoded_response)
    base_filepath = "QuestionList.json"
    if not os.path.exists(base_filepath):
        # 如果文件不存在，创建一个空文件或写入一些初始内容
        with open(base_filepath, "w", encoding='utf-8') as file:
            file.write('[]')  # 初始化文件内容，例如空列表

    with open(base_filepath,"r",encoding='utf-8') as file:
        base = json.load(file)

    base = base + processed_data

    with open(base_filepath,"w",encoding= 'utf-8') as file:
        json.dump(base,file,ensure_ascii=False,indent=4)

    return True
    # 将结果转为JSON字符串，方便查看
    # output_json = json.dumps(processed_data, ensure_ascii=False, indent=4)
    # print(output_json)

def crawl_paperdetail():
    while os.path.exists('paper_list.pkl'):
        with open('paper_list.pkl', 'rb') as f:
            try:
                paper_info = pickle.load(f)
            except EOFError:
                print("pickle 文件为空或读取错误")
                break

        if paper_info:
            # 提取最上端的一组数据
            first_paper = paper_info[0]

            # 执行占位符函数
            success = process_paperID(first_paper[0], first_paper[1])

            time.sleep(random.randint(20,120))
            if success:
                # 删除已处理的数据
                paper_info.pop(0)

                # 将剩余数据重新写入 pickle 文件
                with open('paper_list.pkl', 'wb') as f:
                    pickle.dump(paper_info, f)

                print("已处理的第一条数据已删除并更新到 pickle 文件中")

                # 如果处理完所有数据，则结束循环
                if not paper_info:
                    print("所有数据已处理完毕")
                    break
            else:
                print("占位符函数执行失败，数据未删除")
                break  # 如果函数执行失败，退出循环
        else:
            print("pickle 文件为空，未找到数据")
            break  # 文件中无数据时退出循环
