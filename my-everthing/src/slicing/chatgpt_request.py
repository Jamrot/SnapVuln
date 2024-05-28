import openai
import json
import os
import logging
from tqdm import tqdm
import requests

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
    }

    attempt = 0
    while attempt < max_attempts:
        try:
            response = requests.post(
                url=request_url, headers=request_header, json=request_json
            ).json()
            return response
        except Exception as e:
            logging.error(f"Request failed: {e}")
            attempt += 1
            if attempt == max_attempts:
                logging.error("Max attempts reached. Exiting.")
                return None


def get_prompts():
    patch = """tipc: fix a possible memleak in tipc_buf_append

    __skb_linearize() doesn't free the skb when it fails, so move
    '*buf = NULL' after __skb_linearize(), so that the skb can be
    freed on the err path.

diff --git a/net/tipc/msg.c b/net/tipc/msg.c
index 9a6e9bcbf694..76284fc538eb 100644
--- a/net/tipc/msg.c
+++ b/net/tipc/msg.c
@@ -142,9 +142,9 @@ int tipc_buf_append(struct sk_buff **headbuf, struct sk_buff **buf)
        if (fragid == FIRST_FRAGMENT) {
                if (unlikely(head))
                        goto err;
-               *buf = NULL;
                if (skb_has_frag_list(frag) && __skb_linearize(frag))
                        goto err;
+               *buf = NULL;
                frag = skb_unshare(frag, GFP_ATOMIC);
                if (unlikely(!frag))
                        goto err;"""
    messages = [
        {"role": "system", "content": "You are an expert in patch analyzes. I will give you a patch, and you will analyze it to determine the best slicing method (slicing direction and slicing graph) for the corresponding codes. The best slicing method is the one that can extract the most relevant code for the given patch."},
        {"role": "user", "content": "Patch: {}".format(patch)},
        # {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        # {"role": "user", "content": "Where was it played?"}
    ]
    return messages


def test():
    request_url = "https://api.openai.com/v1/chat/completions"
    

    # messages = [
    #     {"role": "system", "content": "You are a helpful assistant."},
    #     {"role": "user", "content": "Who won the world series in 2020?"},
    #     {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
    #     {"role": "user", "content": "Where was it played?"}
    # ]

    messages = get_prompts()

    response = chatgpt_request(
        request_url=request_url,
        api_key=api_key,
        model="gpt-4o",
        messages=messages
    )

    if response:
        print("Response:", json.dumps(response, indent=2))
    else:
        print("Failed to get a response from ChatGPT 4o.")

if __name__ == "__main__":
    test()
