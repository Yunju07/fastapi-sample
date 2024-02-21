from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi import UploadFile
from docx import Document
from PyPDF2 import PdfFileReader
from pdf2image import convert_from_bytes
from openai import OpenAI
import nltk
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import email
from email_module.nasa_mailbox import mailbox
from email_module.nasa_utils import NASA_UTILS 

from calender_module.make_event import make_event

import io
import os
import re
import requests
import json

# 각종 파일경로 및 폴더
CONVERSATION_FILE_PATH = "conversation.json"

TRANSLATE_TEXT_FILE = "/download/translated_file.txt"

email_md_folder_name = "email_tmp_md"

###########################
## 대화 history 관련 함수 ##
###########################

def save_conversation(conversation):
    # 대화 내용을 JSON 파일에 저장합니다.
    with open(CONVERSATION_FILE_PATH, "w") as file:
        json.dump(conversation, file)

def load_conversation():
    #JSON 파일에서 대화 내용을 읽어옵니다.
    try:
        with open(CONVERSATION_FILE_PATH, "r") as file:
            conversation = json.load(file)
    except FileNotFoundError:
        # 파일이 없을 경우 빈 리스트 반환
        conversation = []
    return conversation

def add_message_to_conversation(message):
    #사용자 입력과 봇 응답을 대화 내용에 추가합니다.
    conversation = load_conversation()
    conversation.append(message)
    save_conversation(conversation)

# 대화 내용 초기화
def clear_conversation():
    save_conversation([])


###################
## 파일 처리 함수 ##
###################
    
async def translate_file(file: UploadFile, language) :
    """
    업로드된 파일에서 텍스트를 추출하는 함수
    :param file: 업로드된 파일 객체
    """
    # 파일 확장자 확인
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension in ["txt", "doc", "docx", "pdf"]:
        file_content = await file.read()

        # txt
        if file_extension == "txt":
            file_content = file_content.decode("utf-8")
            text = split_text(file_content)
            return text_file_translate(text, language)

        # # doc, docx
        # elif file_extension in ["doc", "docx"]:
        #     doc = Document(io.BytesIO(file_content))
        #     text = []
        #     for paragraph in doc.paragraphs:
        #         text.append(paragraph.text)
        #     return text

        # pdf
        elif file_extension == "pdf":
            reader = PdfFileReader(io.BytesIO(file_content))
            result = []
            for page_num in range(reader.numPages):
                page = reader.getPage(page_num)
                text = page.extractText()

                # 이미지 추출            
                images = convert_from_bytes(page)
                base64_images = []
                for idx, image in enumerate(images):
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    base64_images.append(img_str)        

                result.append({"text": text, "images": images})

            return pdf_file_tanslate(result, language)

    else:
        return None

def split_text(text):
    sentences = nltk.sent_tokenize(text)
    splitted_sentences = []
    
    for i in range(0, len(sentences), 5):
        text = ' '.join(sentences[i:i+5])  # 5문장씩 묶어서 하나의 문자열로 만듭니다.
        splitted_sentences.append(text)

    return splitted_sentences

def text_file_translate(split, language):
    client = OpenAI(
        api_key=os.environ['OPENAI_API_KEY'],
    )
    result = ""
    for text in split:
        message = "text:"+text +"\n"
        message += "language:"+language+"\n"
        message += "message: Translate the provided text into the provided language. The tone is plain." 
        print(message)

        chat_completion = client.chat.completions.create(
            messages = [{
                "role":"user",
                "content": message
            }],
            model="gpt-4-1106-preview",
        )
        result += chat_completion.choices[0].message.content
        result += "\n"
        
    data_to_return = {}
    data_to_return['language'] = language

    # 번역 결과 파일로 저장
    current_script_path = os.path.abspath(__file__)
    parent_directory = os.path.dirname(current_script_path)
    os.chdir(parent_directory)

    with open("download/translated_textfile.txt",'w', encoding='utf-8') as file:
        file.write(result)

    data_to_return['download_url'] = "../download/translated_textfile.txt";

    return data_to_return

def pdf_file_tanslate(data, language):
    client = OpenAI(
        api_key=os.environ['OPENAI_API_KEY'],
    )

    current_script_path = os.path.abspath(__file__)
    parent_directory = os.path.dirname(current_script_path)
    os.chdir(parent_directory)

    create_filename = "/download/translated_pdffile.pdf"
    c = canvas.Canvas(create_filename, pagesize=letter)

    for page in data:
        text = page['text']
        images = page['images']

        image_data = {}
        for idx, image in enumerate(images):
            key = f"image{idx+1}"
            image_data[key] = image

        # 번역
        response = client.chat.completions.create(
            messages=[
                {
                "role": "user",
                "content": [
                    {
                        "type": "request",
                        "message" : "Translate the provided text into the provided language. The tone is plain. Images will help you understand the text."
                    },
                    {
                        "type": "text",
                        "text": text
                    },
                    {
                        "type" : "language",
                        "language" : language  
                    },
                    {
                        "type": "image",
                        "image": image_data
                    }
                ]
                }
            ],
            model="gpt-4-1106-preview",
            max_tokens=1000
        )
        result = response.choices[0].message.content
        
        c.drawString(100,700,result)
        c.showPage()
    
    c.save()

    data_to_return = {}
    data_to_return['language'] = language
    data_to_return['download_url'] = get_file_url(parent_directory+r"\download\translated_pdffile.txt")

    return data_to_return

# 파일의 URL을 생성하는 함수
def get_file_url(file_path: str):
    # 파일의 절대 경로를 상대 경로로 변환
    relative_path = os.path.relpath(file_path, os.getcwd())
    
    # URL 생성
    file_url = f"/{relative_path}"

    return file_url

# md 파일 추출
def read_markdown_tag(filename, tag_name):
    os.chdir('email_tmp_md')
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                if f"<{tag_name}>" in line:
                    # 태그가 시작되는 줄을 찾으면 다음 줄부터 해당 태그의 내용을 읽음
                    content = []
                    for line in file:
                        if f"-----end of a email-----" in line:
                            break
                        content.append(line.strip())
                    return '\n'.join(content)
    except FileNotFoundError:
        print(f"파일 '{filename}'을(를) 찾을 수 없습니다.")
    except Exception as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")

######################
## e-mail 관련 함수 ##
######################

def clean_markup(data):
    from bs4 import BeautifulSoup
    return BeautifulSoup(data, "lxml").text

def get_markup_tag(data):
    if not data:
        return

    set_data = set()

    for item in data.split(' '):
        a = re.search('<(.+?)>', item)
        if a:
            set_data.add(a.group(1))
    return set_data

def remove_multiple_spaces(string):
    return re.sub(r'\s+', ' ', string)


## 기타 함수
def post_calender_openai(body):
    formatted_date = datetime.now().strftime('%Y-%m-%d')
    content = f'''<Input>
    {body}

    <Output>
    - Json format that include below informations
    - Make summary as short as possible
    - dateTime format: '2024-02-10T00:00:00+09:00'
    - Summary in Korean
    - Today is {formatted_date}

    summary:
    location:
    dateTime:
    '''

    client = OpenAI(
        api_key=os.environ['OPENAI_API_KEY'],
    )

    chat_completion = client.chat.completions.create(
        messages = [{
            "role": "user", 
            "content": content
        }],
        model="gpt-4-1106-preview",
    )

    return chat_completion.choices[0].message.content
  
def LoadApiKey():
    current_script_path = os.path.abspath(__file__)
    os.chdir(os.path.dirname(current_script_path))

    with open("openai_api_key.txt") as f:
        data = f.read()

    os.environ["OPENAI_API_KEY"] = data

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
    LoadApiKey()    
    data_base64 = base64_data_in_text(text)
    
    if data_base64:
        add_message_to_conversation(
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
        )
        message = load_conversation()
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": message,
            "max_tokens": 1000,
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        
        return response.json()['choices'][0]['message']['content'], data_base64

    else:
        all_urls, image_urls, other_urls = find_urls_in_text(text)
        
        if all_urls:
            text = text.replace(all_urls[0], '')
            add_message_to_conversation(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                        {
                        "type": "image_url",
                        "image_url": {
                            "url": all_urls[0],
                        }
                        }
                    ]
                }
            )
            message = load_conversation()
        
            client = OpenAI(
                api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
            )

            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=message,
                max_tokens=300,
            )

            return response.choices[0].message.content, all_urls[0]
        
        else:
            add_message_to_conversation(
                {
                    "role":"user",
                    "content":text,
                }
            )
            message = load_conversation()

            client = OpenAI(
                api_key=os.environ['OPENAI_API_KEY'],
            )

            chat_completion = client.chat.completions.create(
                messages = message,
                model="gpt-4-1106-preview",
            )

            return chat_completion.choices[0].message.content, None

origins = [
    "http://localhost",
    "http://localhost:3000",
]

class Message(BaseModel):
    text: str

LoadApiKey()
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
    user_text = message.text

    data_to_return = {}

    t, i = GptMultimodal(user_text)

    data_to_return['message'] = t if t else 'Something wrong...'
    if i:
        data_to_return['image'] = i
    add_message_to_conversation("assistant", data_to_return['message'])

    return data_to_return

@app.post("/translate-document/")
async def translate_document(request: Request):
    form = await request.form()
    uploaded_file = form['file']
    language = form['language']
    
    data_to_return = await translate_file(uploaded_file, language)

    return data_to_return

@app.post("/load-emails/")
async def load_emails(request: Request):
    form = await request.form()
    email_id = form['id']
    email_pw = form['password']

    path_of_this_file = os.path.dirname(os.path.realpath(__file__))
    os.chdir(path_of_this_file)
    # try:
    #     os.mkdir(email_md_folder_name)
    # except:
    #     os.chdir(email_md_folder_name)
    #     for file in os.listdir():
    #         os.remove(file)
    #         os.removedirs(email_md_folder_name)
    #         os.mkdir(email_md_folder_name)

    # NASA_UTILS.print_log("init pop3 connection")  
    mail = mailbox(email_id, email_pw)

    mail.pop3_connected = False
    mail.__connect_pop3__()
    all_mail_list = mail.conn_pop3.list()[1]

    # 조회할 최근 메세지 수
    TOP_N_MESSAGE = 50
   
    # 메일 가져오기를 스킵할 송신인
    pass_list = ['security@aptmail.nice.co.kr']

    data_to_return = []

    for i, bb in enumerate([int(aa.decode('ASCII').split(' ')[0]) for aa in all_mail_list[-1*TOP_N_MESSAGE:]]):
            # list 에서 나오는 id는 index 로 uniqueness 를 보장하지 않음
            # 따라서 최근 N개를 가져온 이후 UID 대조 필요

            with open(f"{email_md_folder_name}/tmp_{i}.md", 'w', encoding='utf-8') as f:
        
                (server_msg, body, octets) = mail.conn_pop3.retr(bb)

                msg = email.message_from_bytes(b'\n'.join(body))

                re_parsed = {}

                re_parsed['subject'] = NASA_UTILS.try_decode(msg['subject'])
                re_parsed['from'] = get_markup_tag(msg['FROM'])
                re_parsed['to'] = get_markup_tag(msg['TO'])
                re_parsed['cc'] = get_markup_tag(msg['CC'])
                re_parsed['date'] = msg['Date']
                re_parsed['body'] = remove_multiple_spaces(clean_markup(NASA_UTILS.parse_orig_text(msg, google=True)).replace('> ', ''))

                data_to_return.insert(0, {
                    "subject" : re_parsed['subject'],
                    "from" : re_parsed['from'],
                    "date" : re_parsed['date']
                })

                f.write("-----start of a email-----")
                if re_parsed['from'] not in pass_list:
                    for k in ['subject', 'from', 'to', 'cc', 'date', 'body']:
                        f.write(f"<{k}>\n{re_parsed[k]}\n\n\n")
                f.write("-----end of a email-----")

    mail.conn_pop3.close()
        
    return data_to_return

@app.post("/load-share/")
async def load_share(request: Request):
    form = await request.form()
    access_token = form['accessToken']
    login_id = form['loginId']

    data_to_return = {}
    return data_to_return
    
@app.post("/post-calender/")
async def post_calender(request: Request):
    form = await request.form()
    email_index = form['index']
    email_date = form['date']
    email_from = form['from']
    
    filename = f'tmp_{email_index}.md'
    body_content = read_markdown_tag(filename, 'body')
    os.chdir(os.path.dirname(os.getcwd()))

    if body_content:
        print()

    response = post_calender_openai(body_content).replace('\n', '').replace(' ','').replace('```json','').replace('```','')
    
    data = json.loads(response)
    print(data)
    make_event(data['summary'], data['location'], data['dateTime'], email_from)

    return data

