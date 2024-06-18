import openai
import json
import os
import logging
from tqdm import tqdm
import requests
import time
from dotenv import load_dotenv

import logging
logger = logging.getLogger(__name__)
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
