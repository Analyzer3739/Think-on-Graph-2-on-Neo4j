import json
import time
import openai
#import re
import os
from prompt_list import *
from rank_bm25 import BM25Okapi
from sentence_transformers import util
from openai import OpenAI

def compute_bm25_similarity(query, corpus):

    tokenized_corpus = [doc.split(" ") for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.split(" ")

    doc_scores = bm25.get_scores(tokenized_query)

    return doc_scores

"""def run_llm(prompt, temperature, max_tokens, opeani_api_keys, engine="llama", n=1):

    if "llama" in engine.lower():
        openai_api_key = "EMPTY"
        openai_api_base = "http://127.0.0.1:11434/v1"

        client = OpenAI(
            api_key=openai_api_key,
            base_url=openai_api_base,
        )

        models = client.models.list()
        engine = models.data[0].id
        print(engine)
    else:
        client = openai.OpenAI(api_key=opeani_api_keys, base_url="<your_api_url>")


    sys_prompt = '''你是一个智能助理'''
    messages = [{"role":"system","content":sys_prompt}]
    message_prompt = {"role":"user","content":prompt}
    messages.append(message_prompt)

    f = 4
    while(f > 0):
        if f == 2:
            engine = "llama"    # In case of too long input
        try:
                response = client.chat.completions.create(
                        model=engine,
                        messages = messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        frequency_penalty=0,
                        presence_penalty=0,
                        n=n)
                if n > 1:
                    return response
                else:
                    result = response.choices[0].message.content
                f = -1
                return result
        except Exception as e:
            print(e)
            time.sleep(10)
            f -= 1
    return ''
"""


def run_llm(prompt, temperature, max_tokens, opeani_api_keys, engine="qwen-max", n=1):
    # 通义千问 API 配置
    DASHSCOPE_API_KEY = opeani_api_keys  # 使用传入的 API Key
    BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    print(engine,"\n",prompt)
    # 创建 OpenAI 兼容客户端
    client = OpenAI(
        api_key=DASHSCOPE_API_KEY,
        base_url=BASE_URL,
    )
    
    # 系统提示词
    sys_prompt = '''你是一个智能助理'''
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": prompt}
    ]
    
    # 重试机制
    for _ in range(4):
        try:
            # 调用通义千问 MAX 模型
            response = client.chat.completions.create(
                model=engine,  # 使用 qwen-max
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.8,     # 推荐默认值
                stream=False,   # 非流式输出
                n=n
            )
            
            # 返回格式保持与原始函数一致
            if n > 1:
                return response
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)
    
    return ''  # 所有重试失败后返回空字符串

def generate_only_with_gpt(question, args):
    if 'fever' in args.dataset:
        prompt = fever_s1_prompt_demonstration_6_shot + question + "\nAnswer111:"
    elif "creak" in args.dataset:
        prompt = vanilla_prompt_fact_check_3shot + question + "\nAnswer222:"
    else:
        prompt = cot_prompt + "\nQ:" + question + "\nA:"
    print("prompt:2222222222222222222222222222222222",prompt)
    response = run_llm(prompt, args.temperature_reasoning, args.max_length, args.opeani_api_keys, args.LLM_type)
    return response



def self_consistency(question, data, idx, args):
    def get_s1_prompt(question, args):
        if 'fever' not in args.dataset:
            return hotpotqa_s1_prompt_demonstration + "Q: " + question.strip() + "\nA: "
        else:
            return fever_s1_prompt_demonstration + "Q: " + question.strip() + "\nA: "
    def get_cot_sc_results(data_point, cot_prompt, args, k = 10):
        cot_sc_responses = run_llm(cot_prompt, 0.7, args.max_length, args.opeani_api_keys, args.LLM_type, n=10)

        if cot_sc_responses is not None:
            print(cot_sc_responses)
            all_cot_text_response = [choice.message.content.strip() for choice in cot_sc_responses.choices]
            all_cot_results = []

            for x in all_cot_text_response:
                if "The answer is" in x:
                    all_cot_results.append(x.split("The answer is")[1].strip().lower())
                else:
                    None

            all_cot_results = all_cot_results[:k]
            if len(all_cot_results) > 0:
                most_common_answer = max(set(all_cot_results), key=all_cot_results.count)
                most_common_answer_indices = [i for i, x in enumerate(all_cot_results) if x == most_common_answer]
                sc_score = float(len(most_common_answer_indices)) / k
                cot_answer = all_cot_results[0]
                cot_sc_text_response = all_cot_text_response[most_common_answer_indices[0]]
                cot_sc_answer = most_common_answer
            else:
                cot_sc_answer = ""
                cot_sc_text_response = 'No answer found'
                sc_score = 0

        else:
            raise Exception("Stage 1: OpenAI API call failed")

        data_point["cot_sc_score"] = sc_score
        data_point["cot_sc_response"] = cot_sc_text_response
        data_point["cot_sc_answer"] = cot_sc_answer
        return data_point

    def s1_reasoning_preparation(question, data_point,args):
        print("****************** Start stage 1: reasoning preparation ...")
        print("****** Question:", question)

        cot_prompt = get_s1_prompt(question, args)

        data_point = get_cot_sc_results(data_point, cot_prompt, args)

        print("****** CoT SC score:", data_point["cot_sc_score"])


        return data_point

    data_point = data
    data_point["id"] = idx
    if 'cot_sc_score' not in data_point:
        data_point = s1_reasoning_preparation(question, data_point,args)

        with open(args.output, "w") as f:
            json.dump(data_point, f)
    return data_point

def prepare_dataset(dataset_name):

    if dataset_name == 'cwq':
        with open('../data/cwq.json',encoding='utf-8') as f:
            datas = json.load(f)
        question_string = 'question'
    elif dataset_name == 'hotpot_e':
        with open('/tog2/ToG-2/data/hotpotadv_entities_azure.json',encoding='utf-8') as f:
            datas = json.load(f)
        question_string = 'question'
    elif dataset_name == 'fever':
        with open('../data/fever_1000_entities_azure.json', encoding='utf-8') as f:
            datas = json.load(f)
        question_string = 'claim'
    elif dataset_name == 'webqsp':
        with open('../data/webqsp_test.json', encoding='utf-8') as f:
            datas = json.load(f)
        question_string = 'question'
    elif dataset_name == 'grailqa':
        with open('../data/grailqa.json',encoding='utf-8') as f:
            datas = json.load(f)
        question_string = 'question'
    elif dataset_name == 'simpleqa':
        with open('../data/SimpleQA.json',encoding='utf-8') as f:
            datas = json.load(f)    
        question_string = 'question'
    elif dataset_name == 'qald':
        with open('../data/qald_10-en.json',encoding='utf-8') as f:
            datas = json.load(f) 
        question_string = 'question'   
    elif dataset_name == 'webquestions':
        with open('../data/WebQuestions.json',encoding='utf-8') as f:
            datas = json.load(f)
        question_string = 'question'
    elif dataset_name == 'trex':
        with open('../data/T-REX.json',encoding='utf-8') as f:
            datas = json.load(f)
        question_string = 'input'    
    elif dataset_name == 'zeroshotre':
        with open('../data/Zero_Shot_RE.json',encoding='utf-8') as f:
            datas = json.load(f)
        question_string = 'input'    
    elif dataset_name == 'creak':
        with open('../data/creak.json',encoding='utf-8') as f:
            datas = json.load(f)
        question_string = 'sentence'
    elif dataset_name == 'finkg_qa':
        with open('../data/finkg_qa.json', encoding='utf-8') as f:
            datas = json.load(f)
        question_string = 'question'
    elif dataset_name == 'custom':
        with open('data/custom_questions.json', encoding='utf-8') as f:
            datas = json.load(f)
        question_string = 'question'
    else:
        print("Dataset not found.")
        exit(-1)
    return datas, question_string

def if_finish_list(lst):
    """检查列表中是否所有元素都是 [FINISH_ID]"""
    if all(elem == "[FINISH_ID]" for elem in lst):
        return True, []
    else:
        new_lst = [elem for elem in lst if elem != "[FINISH_ID]"]
        return False, new_lst

def extract_answer(text):
    """从文本中提取大括号内的答案"""
    if not isinstance(text, str):
        return ""
    
    start_index = text.find("{")
    end_index = text.find("}", start_index + 1)  # 从开始位置后开始查找
    
    if start_index != -1 and end_index != -1 and end_index > start_index:
        return text[start_index+1:end_index].strip()
    else:
        return ""
    
def extract_clue(text):
    """从文本中提取clue"""
    if not isinstance(text, str):
        return ""
    
    start_index = text.find("{{")
    end_index = text.find("}}", start_index + 1)  # 从开始位置后开始查找
    
    if start_index != -1 and end_index != -1 and end_index > start_index:
        return text[start_index+2:end_index].strip()
    else:
        return ""
    
def if_true(prompt):
    """检查文本是否表示肯定"""
    if not isinstance(prompt, str):
        return False
    
    # 去除空格并转换为小写
    cleaned = prompt.strip().lower().replace(" ", "")
    
    # 检查多种可能的肯定表示
    return cleaned in {"yes", "true", "correct", "affirmative", "1","是"}