# TITLE: dara : researchgpt 프로젝트

깃허브 오픈소스

  


소스 분석

>static : css 및 js 스크립트

>templates : 웹 프론트 템플릿

**requirements.txt**
--------------------

프로젝트에 필요한 각종 소프트웨어 라이브러리와 기술들

`pip install -r requirements.txt` 명령어를 이용해, 아래 문서의 라이브러리를 설치한다.

  


textfastapi
PyPDF2
pandas
openai
requests
matplotlib
scipy
plotly
gunicorn==20.1.0
scikit-learn==0.24.1
redis
jinja2  


  


라이브러리에 대한 정리
```
fastapi : 파이썬 3.6부터 제공되는 트랜디하고 높은 성능을 가진 파이썬 프레임워크
대중적으로 알려진 파이썬 프레임 워크로 Django, Flask 가 있다.

PyPDF : Python으로 PDF 문서를 다룰 수 있게 해주는 라이브러리

Pandas : 데이터 조작 및 분석을 위한 파이썬 언어용으로 작성된 소프트웨어 라이브러리
⇒ 데이터프레임 생성에 사용. sort_values, head 등 데이터프레임을 쉽게 조작

openai : 인공지능 연구소. 해당 기업의 오픈ai인 챗지피티를 사용

requests : Python 프로그래밍 언어용 HTTP 클라이언트 라이브러리

matplotlib : Python 프로그래밍 언어 및 수학적 확장 NumPy 라이브러리를 활용한 플로팅 라이브러리

scipy : 과학 컴퓨팅과 기술 컴퓨팅에 사용되는 자유-오픈 소스 파이썬 라이브러리

plotly : 인터렉티브한 시각화가 가능한 파이썬 그래픽 라이브러리
(인터렉티브 시각화 → 마우스의 움직임, 클릭 등에 반응. 쉽게 줌인, 줌아웃 활용)

gunicorn : 파이썬 웹 서버 게이트웨이 인터페이스 http 서버. 수많은 웹 프레임 워크와 드넓게 호환된다.(fastapi와 호환)

scikit-learn : 파이썬 프로그래밍 언어용 자유 소프트웨어 기계학습 라이브러리
⇒ cosine_similarity( ) API 제공

redis : Remote Dictionary Server 의 약자, “키-값” 구조의 비정형 데이터를 저장하고 관리하기 위한 오픈 소스 기반의 비관계형 데이터베이스 관리 시스템이다.

jinja2 : 진자는 파이썬용 웹 템플릿 엔진이다.

```
  


  


-내부망에 파이썬 패키지 설치하기

<https://finai.tistory.com/6>

  


-쳇지피티 임베딩 가이드 

<https://wikidocs.net/200485>

  


  


**main.py**
-----------

### **1) const**

pyfrom fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import redis
...

#FastAPI()모듈을 할당한 객체
app = FastAPI()

#템플릿 지정
templates = Jinja2Templates(directory="templates")

#컨테이너 엘리먼트에 앱 인스턴스를 마운트
app.mount("/static", StaticFiles(directory="static"), name="static")

#데이터베이스 연결
db = redis.StrictRedis(host='localhost', port=6379, db=0)  


* middleware-  CORSMiddleware 모듈

pyfrom fastapi.middleware.cors import CORSMiddleware

origins = [
 "http://localhost",
 "http://localhost:3000",
]

app.add\_middleware(
 CORSMiddleware,
 allow\_origins=origins,
 allow\_credentials=True,
 allow\_methods=["\*"],
 allow\_headers=["\*"],
)미들웨어 - 컴퓨터 제작 회사가 사용자의 특정한 요구대로 만들어 제공하는 프로그램. 운영체제와 응용 소프트웨어의 중간에서 조정과 중개의 역할을 수행하는 소프트웨어

CORS란?-Origin

Protocol, Domain, Port 묶음을 이르는 말. (path와 쿼리 스트링은 해당되지 않음)

-SOP (Same-Origin Policy)

SOP는 같은 Origin에서만 Resource를 공유할 수 있는 원칙

단, CORS 정책을 지킨 리소스 요청에 한해서는 다른 Origin간 공유하는 것을 허용

-CORS (Cross-Origin Resource Sharing)

HTTP 헤더를 통해 한 Origin에서 실행 중인 웹 어플리케이션이 다른 Origin의 리소스에 접근할 수 있도록 브라우저에 권한을 부여하는 정책이다.

  


FastAPI의 CORSMiddleware 모듈 사용하기1. `CORSMiddleware` import
2. Resource 요청을 허용할 Origin을 적어주기
3. add\_middleware → 미들웨어 등록
	* allow\_origins=origins
		+ 정의한 origin으로 설정
	* allow\_credentials
		+ cross-origin request에서 cookie를 포함할 것인지 나타냄
		+ 기본값 - False
	* allow\_methods
		+ cross-origin request로 허용할 method들을 나타냄
		+ 기본값 - [’GET’]
	* allow-headers
		+ cross-origin request로 허용할 HTTP Header의 목록
### 2) class Chatbot

  


**`func`** extract\_txt : 입력 텍스트 추출

  


**`func`** extract\_pdf : 입력 pdf 추출

  


**`func`** create\_df : 데이터프레임 df 생성하고, 추출된 pdf 정보를 df[’text’]열에 저장

  


**`func`** embeddings : df[‘text’] 열에 대한 임베딩을 계산하는 역할, df[‘embeddings’] 열에 저장

  


**`func`** search : 사용자의 질문과 데이터프레임 간의 유사도를 계산, 반환하는 함수

pydef search(self, df, query, n=3, pprint=True):
 query\_embedding = get\_embedding(query, engine="text-embedding-ada-002")
 df["similarity"] = df.embeddings.apply(lambda x: cosine\_similarity(x, query\_embedding))

 results = df.sort\_values("similarity", ascending=False, ignore\_index=True)
 # make a dictionary of the the first three results with the page number as the key and the text as the value. The page number is a column in the dataframe.
 results = results.head(n)
 sources = []
 for i in range(n):
 # append the page number and the text as a dict to the sources list
 sources.append({"Page " + str(results.iloc[i]["page"]): results.iloc[i]["text"][:150] + "..."})
 return {"results": results, "sources": sources}-query(사용자 질문) 의 임베딩을 계산합니다. - `query_embedding`

-DataFrame `df`의 "embeddings" 열에 저장된 각 텍스트에 대한 임베딩과 계산한 **`query_embedding`** 간의 코사인 유사도를 계산하여 "similarity" 열을 추가

-데이터프레임을 similartiy로 descending 정렬 (유사도가 높은 순으로 정렬)

-상위 3개에 대해 결과 및 소스 정보가 담긴 딕셔너리를 반환

* cosine\_similarity(vect1, vect2) 함수

사이킷런에서 제공하는 코사인 유사도 측정 API

첫번째 인자는 비교 기준이 되는 문서의 행렬(혹은 배열, 벡터)

두번째 인자는 비교 대상이 되는 문서의 행렬(혹은 배열, 벡터)

  


  


iloc()`iloc`은 Pandas 라이브러리에서 제공하는 DataFrame의 행과 열을 인덱스를 기반으로 선택하기 위한 메서드입니다. "iloc"은 "integer location"의 약자로, 정수 위치를 기반으로 데이터에 접근하는데 사용됩니다.

일반적으로 `iloc`은 다음과 같이 사용됩니다:


```
  
data.iloc[row_index, column_index]

```
  


여기서 `row_index`는 행을 선택하는 데 사용되는 정수 혹은 정수 범위이고, `column_index`는 열을 선택하는 데 사용되는 정수 혹은 정수 범위입니다.

예를 들어, `data.iloc[0, 2]`는 첫 번째 행과 세 번째 열의 원소를 선택합니다. 또한, `data.iloc[:, 1:4]`는 모든 행과 두 번째부터 네 번째 열까지의 데이터를 선택합니다.

이러한 방식으로 `iloc`은 정수 위치를 사용하여 데이터에 접근하므로, 행과 열의 순서에 따라 데이터를 선택할 수 있습니다.

  


  


**`func`** create\_prompt : 대화형 프롬프트 생성 함수

pydef create\_prompt(self, df, user\_input):
 print('Creating prompt')
 print(user\_input)

 result = self.search(df, user\_input, n=3)
 data = result['results']
 sources = result['sources']
 system\_role = """You are a AI assistant whose expertise is reading and summarizing scientific papers. You are given a query, 
 a series of text embeddings and the title from a paper in order of their cosine similarity to the query. 
 You must take the given embeddings and return a very detailed summary of the paper in the languange of the query:
 """

 user\_input = user\_input + """
 Here are the embeddings:

 1.""" + str(data.iloc[0]['text']) + """
 2.""" + str(data.iloc[1]['text']) + """
 3.""" + str(data.iloc[2]['text']) + """
 """

 history = [
 {"role": "system", "content": system\_role},
 {"role": "user", "content": str(user\_input)}]

 print('Done creating prompt')
 return {'messages': history, 'sources': sources}1. search 함수를 사용하여 주어진 user\_input에 대한 검색 결과를 얻음
2. 시스템 역할 및 사용자 입력에 대한 초기 내용을 정의
3. 사용자 입력에 검색 결과의 일부를 추가
4. 대화 히스토리를 리스트로 정의
5. 최종적으로 함수는 대화 히스토리와 검색 결과 소스를 포함하는 딕셔너리를 반환합니다.

system\_role을 적절히 수정하여, 챗지피티에게 원하는 역할을 부여하자

  


  


**`func`** gpt

pydef gpt(self, context, source):
 print('Sending request to OpenAI')
 openai.api\_key = os.getenv('OPENAI\_API\_KEY')

 r = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=context)
 answer = r.choices[0]["message"]["content"]

 print('Done sending request to OpenAI')
 response = {'answer': answer, 'sources': source}

 return response1. OpenAI API 키를 설정
2. openai.ChatCompletion.create를 사용하여 GPT-3.5-turbo 모델에 대한 요청을 보냄
3. 응답에서 획득한 답변 내용을 추출
4. 결과를 딕셔너리로 반환

  


**3)**
------

  


**`func`** index : FastAPI 프레임워크를 사용하여 루트 엔드포인트에 대한 HTML 응답을 생성

  


pyapp = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response\_class=HTMLResponse)
async def index(request: Request):
 return templates.TemplateResponse("index.html", {"request": request})* `app = FastAPI()`: FastAPI 애플리케이션을 생성합니다.
* `templates = Jinja2Templates(directory="templates")`: Jinja2Templates를 사용하여 HTML 템플릿을 저장하는 디렉토리를 설정합니다. 여기서는 "templates" 디렉토리를 사용하고 있습니다.
* `@app.get("/", response_class=HTMLResponse)`: HTTP GET 요청을 처리하는 핸들러를 정의합니다. 이 핸들러는 "/" 경로에 대한 것으로 설정되어 있습니다. `response_class=HTMLResponse`는 이 엔드포인트가 HTML 응답을 반환할 것임을 나타냅니다.
* `async def index(request: Request)`: "index" 함수는 `Request` 객체를 매개변수로 받습니다. 이 함수는 HTML 템플릿을 렌더링하고 응답을 반환합니다.
* `return templates.TemplateResponse("index.html", {"request": request})`: `TemplateResponse`를 사용하여 "index.html" 템플릿을 렌더링하고, "request" 매개변수를 템플릿에 전달합니다. 최종적으로 이 템플릿 렌더링 결과가 클라이언트로 응답됩니다.

  


  


**`func`** process\_pdf :  FastAPI를 사용하여 HTTP POST 요청을 처리하며, **PDF 파일을 처리**하고 해당 내용을 데이터베이스에 저장

  


pyapp = FastAPI()

@app.post("/process\_pdf")
async def process\_pdf(request: Request):
 print("Processing pdf")

 # HTTP 요청에서 바디를 읽어와서 MD5 해시값을 키로 사용
 body = await request.body()
 key = md5(body).hexdigest()
 print(key)

 # 이미 처리된 PDF인지 확인
 if db.get(key) is not None:
 print("Already processed pdf")
 return JSONResponse({"key": key})

 # PDF 파일을 읽어오고 Chatbot을 초기화하여 사용
 file = body
 pdf = PdfReader(BytesIO(file))

 chatbot = Chatbot()

 # Chatbot을 사용하여 PDF에서 텍스트 추출 및 DataFrame 생성 및 임베딩 계산
 paper\_text = chatbot.extract\_pdf(pdf)
 df = chatbot.create\_df(paper\_text)
 df = chatbot.embeddings(df)

 # 데이터베이스에 결과를 저장
 if db.get(key) is None:
 db.set(key, df.to\_json())

 print("Done processing pdf")
 return JSONResponse({"key": key})* `@app.post("/process_pdf")`: HTTP POST 요청을 처리하는 핸들러를 정의합니다. 이 핸들러는 "/process\_pdf" 경로에 대한 것입니다.
* `body = await request.body()`: HTTP 요청의 바디를 비동기 방식으로 읽어옵니다.
* `key = md5(body).hexdigest()`: 읽어온 바디의 MD5 해시값을 계산하여 키로 사용합니다.
* `if db.get(key) is not None:`: 데이터베이스에 해당 키가 이미 존재하면 이미 처리된 PDF로 간주하고 종료합니다.
* `pdf = PdfReader(BytesIO(file))`: BytesIO를 사용하여 PDF 파일을 읽어옵니다.
* `chatbot = Chatbot()`: Chatbot 객체를 생성하여 사용할 준비를 합니다.
* `paper_text = chatbot.extract_pdf(pdf)`: Chatbot을 사용하여 PDF에서 텍스트를 추출합니다.
* `df = chatbot.create_df(paper_text)`: 추출된 텍스트를 사용하여 DataFrame을 생성합니다.
* `df = chatbot.embeddings(df)`: DataFrame에 대한 임베딩을 계산합니다.
* `if db.get(key) is None: db.set(key, df.to_json())`: 데이터베이스에 해당 키가 없으면 계산된 결과를 데이터베이스에 저장합니다.
* `return JSONResponse({"key": key})`: 처리가 완료된 후에는 결과 키를 반환합니다.

  


  


**`func`** download\_pdf : 주어진 URL에서 **PDF를 다운로드하여 처리**하고, 처리된 내용을 데이터베이스에 저장

  


py@app.post("/download\_pdf")
async def download\_pdf(url: str):
 chatbot = Chatbot()

 # 주어진 URL에서 PDF 다운로드
 r = requests.get(str(url))
 key = md5(r.content).hexdigest()

 # 이미 처리된 PDF인지 확인
 if db.get(key) is not None:
 return JSONResponse({"key": key})

 # 다운로드한 PDF를 읽어와서 Chatbot을 사용하여 처리
 pdf = PdfReader(BytesIO(r.content))
 paper\_text = chatbot.extract\_pdf(pdf)
 df = chatbot.create\_df(paper\_text)
 df = chatbot.embeddings(df)

 # 처리된 결과를 데이터베이스에 저장
 if db.get(key) is None:
 db.set(key, df.to\_json())

 print("Done processing pdf")
 return JSONResponse({"key": key})

* `@app.post("/download_pdf")`: HTTP POST 요청을 처리하는 핸들러를 정의합니다. 이 핸들러는 "/download\_pdf" 경로에 대한 것입니다.
* `r = requests.get(str(url))`: 주어진 URL에서 PDF를 다운로드합니다.
* `key = md5(r.content).hexdigest()`: 다운로드한 PDF의 내용을 MD5 해시값으로 변환하여 키로 사용합니다.
* `if db.get(key) is not None:`: 데이터베이스에 해당 키가 이미 존재하면 이미 처리된 PDF로 간주하고 종료합니다.
* `pdf = PdfReader(BytesIO(r.content))`: BytesIO를 사용하여 다운로드한 PDF 파일을 읽어옵니다.
* `paper_text = chatbot.extract_pdf(pdf)`: Chatbot을 사용하여 PDF에서 텍스트를 추출합니다.
* `df = chatbot.create_df(paper_text)`: 추출된 텍스트를 사용하여 DataFrame을 생성합니다.
* `df = chatbot.embeddings(df)`: DataFrame에 대한 임베딩을 계산합니다.
* `if db.get(key) is None: db.set(key, df.to_json())`: 데이터베이스에 해당 키가 없으면 계산된 결과를 데이터베이스에 저장합니다.
* `return JSONResponse({"key": key})`: 처리가 완료된 후에는 결과 키를 반환합니다.

  


  


**`func`** reply ; HTTP POST 요청을 처리하고, 이전에 처리된 PDF에 대한 정보를 사용하여 **GPT-3.5-turbo 모델에 대한 대화를 생성하고 응답을 반환**

  


py@app.post("/reply")
async def reply(request: Request):
 data = await request.json()
 key = data.get('key')
 query = data.get('query')

 chatbot = Chatbot()
 query = str(query)

 # 데이터베이스에서 해당 키에 대한 정보를 가져와 DataFrame으로 변환
 df = pd.read\_json(BytesIO(db.get(key)))

 # Chatbot을 사용하여 적절한 프롬프트 생성
 prompt = chatbot.create\_prompt(df, query)

 chat = []
 chat.extend(prompt['messages'])

 # Chatbot을 사용하여 GPT-3.5-turbo 모델에 대한 응답 생성
 response = chatbot.gpt(chat, prompt['sources'])

 return JSONResponse(content=response, status\_code=200)

* `data = await request.json()`: HTTP POST 요청에서 JSON 데이터를 읽어옵니다.
* `key = data.get('key')`, `query = data.get('query')`: JSON 데이터에서 'key' 및 'query' 키를 사용하여 정보를 추출합니다.
* `df = pd.read_json(BytesIO(db.get(key)))`: 데이터베이스에서 해당 키에 대한 정보를 가져와 Pandas DataFrame으로 변환합니다.
* `prompt = chatbot.create_prompt(df, query)`: Chatbot을 사용하여 주어진 DataFrame과 쿼리에 대한 프롬프트를 생성합니다.
* `chat.extend(prompt['messages'])`: 생성된 프롬프트 메시지를 'chat' 리스트에 추가합니다.
* `response = chatbot.gpt(chat, prompt['sources'])`: Chatbot을 사용하여 GPT-3.5-turbo 모델에 대한 응답을 생성합니다.
* `return JSONResponse(content=response, status_code=200)`: 생성된 응답을 JSON 형태로 반환합니다.

  


  


  


