from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi import UploadFile
from docx import Document
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
from openai import OpenAI
import nltk
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import re
import email
from email_module.nasa_mailbox import mailbox
from email_module.nasa_utils import NASA_UTILS 
from atlassian import Confluence
from markdownify import markdownify as md
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
share_md_folder_name = "share_tmp_md"


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
            return text_file_translate(text, language, file.filename.split(".")[0])

        # # doc, docx
        # elif file_extension in ["doc", "docx"]:
        #     doc = Document(io.BytesIO(file_content))
        #     text = []
        #     for paragraph in doc.paragraphs:
        #         text.append(paragraph.text)
        #     return text

        # pdf
        elif file_extension == "pdf":
            reader = PdfReader(io.BytesIO(file_content))
            result = []
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()

                # 이미지 추출            
                images = page.images
                base64_images = []
                # for idx, image in enumerate(images):
                #     buffered = io.BytesIO()
                #     image.save(buffered, format="JPEG")
                #     img_str = base64.b64encode(buffered.getvalue()).decode()
                #     base64_images.append(img_str)        

                result.append({"text": text, "images": base64_images})

            return pdf_file_tanslate(result, language, file.filename.split(".")[0])

    else:
        return None

def split_text(text):
    sentences = nltk.sent_tokenize(text)
    splitted_sentences = []
    
    for i in range(0, len(sentences), 10):
        text = ' '.join(sentences[i:i+10])  # 10문장씩 묶어서 하나의 문자열로 만듭니다.
        splitted_sentences.append(text)

    return splitted_sentences

def text_file_translate(split, language, filename):
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

    with open(f'download/{filename}_translate.txt','w', encoding='utf-8') as file:
        file.write(result)
    
    download_path = f'download/{filename}_translate.txt'

    print(filename)
    #data_to_return['download_url'] = f'download/{filename}_translate.txt'

    return FileResponse(download_path, media_type='text/plain', filename=f'{filename}_translate.txt')

def pdf_file_tanslate(data, language, filename):
    client = OpenAI(
        api_key=os.environ['OPENAI_API_KEY'],
    )

    current_script_path = os.path.abspath(__file__)
    parent_directory = os.path.dirname(current_script_path)
    os.chdir(parent_directory)

    create_filename = f'download/{filename}_translate.txt'
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

    pdf_path = f'download/{filename}_translate.txt'
    return FileResponse(pdf_path, media_type='application/pdf', filename=f'{filename}_translate.txt')


# md 파일 추출
def read_markdown_tag(path, filename, tag_name):
    os.chdir(path)
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

def read_md_file(file_path):
    title = None
    body = ""

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        if lines:
            title = lines[0].strip()  # 첫 번째 줄을 제목으로 설정
            body = ''.join(lines[1:])  # 나머지 줄을 본문으로 설정

    return title, body

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
def RetrieveConfluencePage(share_link, access_token, account):
    result = []
    path_of_this_file = os.path.dirname(os.path.realpath(__file__))
    os.chdir(path_of_this_file)
    try:
       os.mkdir(share_md_folder_name)
    except:
        os.chdir(share_md_folder_name)
        for file in os.listdir():
            os.remove(file)
        os.chdir(path_of_this_file)
    
    base_url = 'https://share.nice.co.kr'
    my_access_token = access_token
    space=f'~{account}'
    confluence = Confluence(
    url=base_url,
    token=my_access_token
    )
    # 정규 표현식 패턴
    pattern = r"pageId=(\d+)"
    match = re.search(pattern, share_link)
    share_page_id = match.group(1)

    reference_url = []
 
    root_page = confluence.get_page_by_id(share_page_id)

    title = root_page['title']
    result.append({
        "id": share_page_id,
        "title": title,
        "index": -1
    })

    page_content = confluence.get_page_by_id(share_page_id, expand='body.storage')
 
    body_html = page_content['body']['storage']['value']
    reference_url.append(base_url+root_page['_links']['webui'])
    body_markdown = md(body_html)

    with open(f"{share_md_folder_name}/tmp_0.md", 'w', encoding='utf-8') as f:
        f.write(f"# TITLE: {title}\n\n")
        f.write(body_markdown)

    # chile page
    pages = confluence.get_child_pages(share_page_id)
    print(pages)
    
    for i, page in enumerate(pages):
        # 작성한 사용자 관련된 정보도 실을 수 있다면 더 정확해 질 것 같다.
        id = page['id']
        title = page['title']
        result.append({
            "id": id,
            "title": title,
            "index": i
        })
        
        # body 내용 읽어오는 방법 ...
        this_page = confluence.get_page_by_id(id, expand='body.storage')
 
        body_html = this_page['body']['storage']['value']
        reference_url.append(base_url+page['_links']['webui'])
        body_markdown = md(body_html)

        with open(f"{share_md_folder_name}/tmp_{i+1}.md", 'w', encoding='utf-8') as f:
            f.write(f"# TITLE: {title}\n\n")
            f.write(body_markdown)

    return result

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
            print(text)
            add_message_to_conversation(
                {
                    "role":"user",
                    "content":text,
                }
            )
            message = load_conversation()

            headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
            }

            payload = {
                "model": "gpt-3.5-turbo",
                "messages": message,
                "max_tokens": 1000,
            }
            print(payload)

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            
            print(response.json())
            return response.json()['choices'][0]['message']['content'], None


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
async def send_message(request: Request):
    form = await request.form()
    user_text = form['text']

    data_to_return = {}

    t, i = GptMultimodal(user_text)

    data_to_return['message'] = t if t else 'Something wrong...'
    if i:
        data_to_return['image'] = i
    message = {
        "role": "assistant",
        "content": data_to_return['message']
    }
    add_message_to_conversation(message)

    print(data_to_return)

    return data_to_return

@app.post("/translate-document/")
async def translate_document(request: Request):
    form = await request.form()
    uploaded_file = form['file']
    language = form['language']

    return await translate_file(uploaded_file, language)

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
    account = form['loginAccount']
    share_link = form['shareLink']

    data_to_return = {}

    data_to_return = RetrieveConfluencePage(share_link, access_token, account)

    return data_to_return
    
@app.post("/post-calender/")
async def post_calender(request: Request):
    form = await request.form()
    email_index = form['index']
    email_date = form['date']
    email_from = form['from']
    
    filename = f'tmp_{email_index}.md'
    body_content = read_markdown_tag('email_tmp_md', filename, 'body')
    os.chdir(os.path.dirname(os.getcwd()))

    if body_content:
        print()

    response = post_calender_openai(body_content).replace('\n', '').replace(' ','').replace('```json','').replace('```','')
    
    data = json.loads(response)
    print(data)
    make_event(data['summary'], data['location'], data['dateTime'], email_from)

    return data

@app.post("/draft-report")
async def draft_report(request: Request):
    form = await request.form()

    data = []
    files = []

    print(form.keys())
    if 'emailIndex' in form:
        email_index = form['emailIndex']
        title = form['emailTitle']
        filename = f'tmp_{email_index}.md'
        body_content = read_markdown_tag('email_tmp_md', filename, 'body')
        data.append({
            "title": title,
            "body" : body_content,
            "type" : "email"

        })
        files.append(title)
        os.chdir(os.path.dirname(os.getcwd()))

    if 'file' in form:
        file = form['file']
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension in ["txt", "doc", "docx", "pdf"]:
            file_content = await file.read()
            # txt
            if file_extension == "txt":
                text = file_content.decode("utf-8")
                data.append({
                    "title": file.filename.split(".")[0],
                    "body" : text,
                    "type" : "file"
                })        
                files.append(file.filename.split(".")[0])
            #pdf
            elif file_extension == "pdf":
                reader = PdfReader(io.BytesIO(file_content))
                text = ""
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                data.append({
                    "title": file.filename.split(".")[0],
                    "body" : text,
                    "type" : "file"
                })
                files.append(file.filename.split(".")[0])

    if 'share' in form:
        share = int(form['share'])
        print(share)
        for i in range(share):
            filename = f'share_tmp_md/tmp_{i}.md'
            title, body_content = read_md_file(filename) 
            data.append({
                "title" : title,
                "body" : body_content,
                "type" : "share"
            })
            files.append(title)
    response =  json.loads(draft_report_openai(data).replace('\n', '').replace('```json','').replace('```',''))
    print(response["content"])

    # response = {
    #     "title": "OpenAI를 이용한 챗봇 시스템 구축 프로젝트 보고서",
    #     "content": {
    #         "background": "인공지능 기술의 급속한 발전에 힘입어, 자연어 처리 기술을 활용한 챗봇 시스템의 수요가 증가하고 있다. OpenAI는 이러한 수요에 대응하기  위해 다양한 AI 모델을 제공하며, 챗봇 시스템 구축을 위한 핵심 기술로 자리 잡고 있다.",
    #         "status": "본 프로젝트는 OpenAI를 활용한 쳇봇 시스템 구축을 목표로 하여, 다양한 오픈소스 라이브러리와 기술들을 사용하여 시스템을 구축하고 있다. 현재까지는 fastapi, PyPDF2, pandas 등의 라이브러리를 활용하여 웹 서버 및 데이터 처리 부분을 완성하였으며, OpenAI의 GPT 모델을 이용하여 대화형 AI의 기능을 테스트 중에 있다.",
    #         "proposal": "프로젝트의 다음 단계로는 더 정교한 사용자 질의 처리 기능을 개발하고, 새로운 기능이나 모델의 통합을 통해 챗봇 시스템의 성능을 개선하는  작업이 필요하다. 또한, 실 사용자에 의한 시범 운영을 통해 시스템의 안정성과 사용성을 검증하고, 향후 사용자 경험을 높일 수 있는 UI/UX 개선에 주력할 필요가 있 다.",
    #         "conclusion": "OpenAI와 같은 고성능 AI 모델을 활용한 챗봇 시스템은 현대 사회에서 다양한 분야에 적용되며 큰 잠재력을 가지고 있다. 본 프로젝트는 이러 한 기술의 실제 적용 예를 탐색하고, 궁극적으로 사용자 친화적인 대화형 시스템을 구축하는 데 기여하고자 한다."
    #     },
    #     "references": "OpenAI를 이용한 챗봇 시스템 구축 프로젝트"
    # }

    body = ''
    body += f'''
    1) 배경 \n
    {response["content"]["background"]}
    \n\n
    2) 현황\n
    {response["content"]["status"]}
    \n\n
    3) 제안\n
    {response["content"]["proposal"]}
    \n\n
    4) 결론\n
    {response["content"]["conclusion"]}
    
    '''
    #쉐어 페이지 생성
    
    share_link = form['shareLink']
    # 정규 표현식 패턴
    pattern = r"pageId=(\d+)"
    match = re.search(pattern, share_link)
    share_page_id = match.group(1)

    access_token = form['accessToken']

    confluence = Confluence(
        url='https://share.nice.co.kr',
        token=access_token
    )

    status = confluence.update_or_create(parent_id=share_page_id, title=response['title'], body=body,representation='wiki', full_width=False, )
    page_link = 'https://share.nice.co.kr'+status['_links']['webui'] 

    data_to_return = {
        'title' : title,
        'link' : page_link
    }

    return data_to_return

def draft_report_openai(data):
    input_data = ''
    for i, file in enumerate(data):
        title = file['title']
        body = file['body']
        type = file['type']
        input_data += f'{i} -title: {title} -content: {body} -type: {type}'
        input_data += '\n'

    print(input_data)

    content = f'''<Input>
    {input_data}

    <Output>
    - Json format that include below informations
    - Gather data and draft a report
    - Include the title of input file as the source in your content
    - The report contents are written in four parts: background, status, proposal, and conclusion
    - Responses must be written in Korean

    title:
    content:{{
        "background": 
        "status":
        "proposal":
        "conclusion":
    }}
    
    references:
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
