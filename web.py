
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from openai import OpenAI
import os
import re
import requests


# def LoadApiKey():
#     # get parent dir
#     path_of_this_file = os.path.dirname(os.path.realpath(__file__))
#     os.chdir(os.path.join(path_of_this_file, os.pardir))

#     # get my api key from text file
#     # 이 소스코드가 저장된 폴더의 상위 경로에 openai_api_key.txt 파일을 만들고
#     # openai에서 발급밭은 api key를 텍스트 파일에 저장하면 됩니다.
#     with open("openai_api_key.txt") as f:
#         data = f.read()

#     os.environ["OPENAI_API_KEY"] = data

def find_urls_in_text(text):
    # Regular expression pattern for matching URLs
    # This pattern is quite simplistic and can be made more sophisticated to accurately match URLs
    url_pattern = r'https?://[^\s]+'

    # Find all instances of the pattern in the text
    urls = re.findall(url_pattern, text)

    # Optionally, separate image URLs from other URLs
    image_urls = [url for url in urls if url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg'))]
    other_urls = [url for url in urls if url not in image_urls]

    return urls, image_urls, other_urls

def base64_data_in_text(text):
    data_pattern = r'data:image/[^\s]+'
    data = re.findall(data_pattern, text)
    return data

def GptMultimodal(text):     
    data_base64 = base64_data_in_text(text)
    if data_base64:
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
        }

        payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": text.replace(data_base64[0], '')
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"{data_base64[0]}"
                }
                }
            ]
            }
        ],
        "max_tokens": 1000
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        
        return response.json()['choices'][0]['message']['content'], data_base64


    else:
        all_urls, image_urls, other_urls = find_urls_in_text(text)

        if all_urls:
            text = text.replace(all_urls[0], '')
        
            client = OpenAI(
                api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
            )

            response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": all_urls[0],
                    },
                    },
                ],
                }
            ],
            max_tokens=300,
            )

            return response.choices[0].message.content, all_urls[0]
        
        else:
            client = OpenAI(
                api_key=os.environ['OPENAI_API_KEY'],
            )

            chat_completion = client.chat.completions.create(
                messages = [{
                    "role":"user",
                    "content":text,
                }],
                model="gpt-4-1106-preview",
            )

            return chat_completion.choices[0].message.content, None

origins = [
    "http://localhost",
    "http://localhost:3000",
]

class Message(BaseModel):
    user_input: str

#LoadApiKey()
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

path_of_this_file = os.path.dirname(os.path.realpath(__file__))
os.chdir(path_of_this_file)

app.mount("/static", StaticFiles(directory="static"), name="static")

# fastapi
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/send-message/")
async def send_message(request: Request, message: Message):
    user_text = message.user_input

    data_to_return = {}

    t, i = GptMultimodal(user_text)

    data_to_return['message'] = t if t else 'Something wrong...'
    if i:
        data_to_return['image'] = i
    return data_to_return


@app.post("/check-message/")
async def check_message(message: Message):
    user_text = message.text

    data_to_return = {}

    data_base64 = base64_data_in_text(user_text)
    all_urls, image_urls, other_urls = find_urls_in_text(user_text)

    if data_base64:
        data_to_return['image'] = data_base64[0]
        user_text = user_text.replace(data_base64[0], '')
    elif all_urls:
        data_to_return['image'] = all_urls[0]
        user_text = user_text.replace(all_urls[0], '')

    data_to_return ['message'] = user_text

    return data_to_return
