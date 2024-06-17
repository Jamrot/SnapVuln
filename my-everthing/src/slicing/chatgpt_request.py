import openai
import json
import os
import logging
from tqdm import tqdm
import requests
import time
from dotenv import load_dotenv

from patch_analyzer import PatchAnalyzer
import config
from get_prompts import *

load_dotenv()

def chatgpt_request(
    request_url: str,
    api_key: str, 
    model: str ='gpt-3.5-turbo', 
    max_token: int =8000, 
    max_attempts: int =10,
    temperature: float = 0,
    choices: int = 1,
    messages: list = [],
):
    request_header = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    request_json = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": 1,
        "n": choices,
        "stream": False,
        "stop": '',
        "logit_bias": {},
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "seed":0,
    }

    attempt = 0
    while attempt < max_attempts:
        try:
            # response = requests.post(
            #     url=request_url, headers=request_header, json=request_json
            # ).json()
            request = requests.Request(
                "POST",
                url=request_url,
                headers=request_header,
                json=request_json
            )
            prepared_request = request.prepare()
            request_content = prepared_request.body
            if isinstance(request_content, bytes):
                request_content = request_content.decode('utf-8')
                request_content = json.loads(request_content)

            # Send the request
            session = requests.Session()
            response = session.send(prepared_request).json()
            return response, request_content
        except Exception as e:
            logging.error(f"Request failed: {e}")
            attempt += 1
            if attempt == max_attempts:
                logging.error("Max attempts reached. Exiting.")
                return None


"""parse"""
def read_single_response(response_filepath):
    with open(response_filepath, 'r') as f:
        response_json = json.load(f)
    
    response = response_json['response']['choices'][0]['message']['content']
    return response


def get_response_content(response_info):
    response_content = response_info['choices'][0]['message']['content']
    return response_content


def parse_PA_response(response):
    response_dict = json.loads(response)
    patch_summary = response_dict.get("patch_summary", "")
    vulnerability_type = response_dict.get("vulnerability_type", "")
    vulnerability_summary = response_dict.get("vulnerability_summary", "")

    if not patch_summary:
        logging.error("Failed to get patch summary from response.")
    if not vulnerability_type:
        logging.error("Failed to get vulnerability type from response.")
    if not vulnerability_summary:
        logging.error("Failed to get vulnerability summary from response.")

    return patch_summary, vulnerability_type, vulnerability_summary


def save_response(response, response_filepath, request_content=""):
    save_content = {
        "request": request_content,
        "response": response        
    }
    save_dir = os.path.dirname(response_filepath)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    with open(response_filepath, 'w') as f:
        json.dump(save_content, f, indent=2)


def test():
    request_url = "https://api.openai.com/v1/chat/completions"
    api_key = os.getenv("OPENAI_API_KEY")

    commit_id = "a282a2f10539dce2aa619e71e1817570d557fc97"
    patch_desc, patch_diff_code, patch_info = get_patch(commit_id)

    prompt_filepath = "my-everthing/prompts/prompt.json"
    patch = patch_desc+'\n'+patch_diff_code
    messages = get_PA_prompts(prompt_filepath=prompt_filepath, patch=patch)

    response_info, request_content = chatgpt_request(
        request_url=request_url,
        api_key=api_key,
        model="gpt-4o",
        messages=messages
    )

    # response file with timestamp
    response_filepath = f"my-everthing/responses/response_{time.time()}.json"
    save_response(response_info, response_filepath, request_content=request_content)

    if response_info:
        print("Response:", json.dumps(response_info, indent=2))
    else:
        logging.error("Failed to get response.")
    
    response_PA = get_response_content(response_info)
    


def test_SE():
    response_PA_filepath = "my-everthing/responses/response_1718006229.2723458.json"
    response_PA = read_single_response(response_PA_filepath)
    
    commit_id = "a282a2f10539dce2aa619e71e1817570d557fc97"
    patch_desc, patch_diff_code, patch_info = get_patch(commit_id)
    messages = get_SE_prompts("my-everthing/prompts/prompt.json", response_PA, patch_info)

    request_url = "https://api.openai.com/v1/chat/completions"
    api_key = os.getenv("OPENAI_API_KEY")

    response_info, request_content = chatgpt_request(
        request_url=request_url,
        api_key=api_key,
        model="gpt-4o",
        messages=messages
    )

    response_filepath = f"my-everthing/responses/SE/response_{time.time()}.json"
    save_response(response_info, response_filepath, request_content=request_content)

    if response_info:
        print("Response:", json.dumps(response_info, indent=2))
    else:
        logging.error("Failed to get response.")

    # TODO: parse response


def test_SS():
    response_PA_filepath = "my-everthing/responses/response_1718006229.2723458.json"
    response_PA = read_single_response(response_PA_filepath)
    
    commit_id = "a282a2f10539dce2aa619e71e1817570d557fc97"
    patch_desc, patch_diff_code, patch_info = get_patch(commit_id)
    messages = get_SS_prompts("my-everthing/prompts/prompt.json", response_PA, patch_diff_code)

    # print(messages)

    request_url = "https://api.openai.com/v1/chat/completions"
    api_key = os.getenv("OPENAI_API_KEY")

    response_info, request_content = chatgpt_request(
        request_url=request_url,
        api_key=api_key,
        model="gpt-4o",
        messages=messages
    )

    response_filepath = f"my-everthing/responses/SS/response_{time.time()}.json"
    save_response(response_info, response_filepath, request_content=request_content)

    if response_info:
        print("Response:", json.dumps(response_info, indent=2))
    else:
        logging.error("Failed to get response.")
    
    # TODO: parse response


def test_read_response():
    response_filepath = "my-everthing/responses/SE/response_1718012712.632313.json"
    response = read_single_response(response_filepath)
    print(response)

if __name__ == "__main__":
    test_SS()
    # test_read_response()
