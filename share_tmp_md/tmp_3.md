# TITLE: pdf 추출, dataframe 생성, 임베딩 계산 실습

실습 pdf

[2021 DB 프로젝트 1.pdf](https://prod-files-secure.s3.us-west-2.amazonaws.com/219708d0-aa4c-4dbe-bd71-5414478fbae3/026791d9-e477-46f7-823f-b550b1559166/2021_DB_%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8_1.pdf) 

  


실습내용

제가 학교에서 들었던 수업의 과제 명세서 pdf를 실습 pdf 로 선정하여 진행하였습니다.

해당 pdf에는 과목명, 교수님과 조교님의 이메일, 과제의 요구사항, 패널티 등의 정보가 있습니다.

해당 pdf를 활용하여, 데이터 추출, 데이터프레임 생성, 임베딩 계산의 실습 을 진행하였습니다.

  


추후 해당 데이터를 가지고, 임의의 질문(문장)과 코사인 유사도를 구하고,

이를 바탕으로 openai의 챗지피티 모델에게 답변을 요청하는 실습을 진행할 예정입니다.

  


### 1) pdf 에서 텍스트 추출하기

  
-extract\_pdf()

pydef extract\_pdf(pdf):
 print("Parsing paper")
 number\_of\_pages = len(pdf.pages)
 print(f"Total number of pages: {number\_of\_pages}")
 paper\_text = []
 for i in range(number\_of\_pages):
 page = pdf.pages[i]
 page\_text = []

 text = page.extract\_text().strip()
 page\_text = text.split('\\n')
 
 blob\_text = ""
 processed\_text = []

 for t in page\_text:
 blob\_text += f" {t}"
 if len(blob\_text) >= 200 or (page\_text.index(t) == len(page\_text)-1):
 processed\_text.append({"text": blob\_text, "page": i})
 blob\_text = ""
 paper\_text += processed\_text
 print("Done parsing paper")
 return paper\_text

extract\_pdf 메소드

* pdf의 텍스트를 추출하고, 문장 단위(’\n’기준)로 나눈다
* 문장의 내용을 “text” 라는 키로, pdf에서의 페이지를 “page”라는 키로 딕셔너리를 만듭니다.
* **if len(blob\_text) >= 200 or (page\_text.index(t) == len(page\_text)-1):**

→ 모든 문장을 딕셔너리로 만들어 저장하는 것이 아닌, 여러 문장을 더해서 만듭니다.

위의 조건문은 문장들을 더해가다 길이가 200이 넘게되거나, 해당 문장이 페이지의 마지막 문장일 경우, 하나의 딕셔너리로 만들기 위함입니다.

여기에서 데이터프레임의 한 조각 될 텍스트의 길이를 조절할 수 있습니다.

  


py from PyPDF2 import PdfReader

def extract\_pdf(pdf):
...
 return paper\_text

# file processing 
pdf = PdfReader("./pdf/2021 DB 프로젝트 1.pdf")
paper\_text = extract\_pdf(pdf)

# 원소 한개씩 출력
for text in paper\_text:
 print(text)

  


결과

text {'text': ' 프로젝트 1: 요구사항 분석 2021년 9월 30일 과목명: 데이터베이스 시스템 및 응용 교수: 김상욱 (이메일: wook@hanyang.ac.kr ) 조교: 서동혁 (이메일: hyuk125@agape.hanyang.ac.kr ), 손지원 (이메일: taerik@agape.hanyang.ac.kr ) 1. 목표 DBMS를 활용하는 서비스 개발에 필요한 요구사항 분석 및 문서화 ', 'page': 0}
{'text': ' 2. 제약 사항 서비스 요구사항은 다음과 같은 entity와 요구 사항을 반드시 포함해야 한다. [은행 서비스 DBMS 개발] \\uf0b7 Entity: 관리자, 사용자, 계좌 \\uf0b7 요구사항 \\uf0fc 관리자는 각 사용자의 계좌 입출금 내역을 관리한다. \\uf0fc 사용자는 자신의 계좌를 n개까지 개설하거나 삭제한다. \\uf0fc 사용자는 자신의 계좌에 돈을 입금할 수 있다. ', 'page': 0}
{'text': ' \\uf0fc 사용자는 자신의 계좌에서 돈을 출금할 수 있다. 위 사항들 외의 다른 개체와 요구사항을 추가할 수 있다. 잘 설계된 entity 및 attribute와 구체적이고 풍부한 요구 사항에는 더 높은 점수가 부여된다. 수강생들은 프로젝트1부터 4까지 진행하며 최종적으로 본인이 설계한 요구 사항을 바탕으로 한 DBMS 활용 서비스를 개발하게 될 것이다. ', 'page': 0}
{'text': ' 3. 요구사항 분석 문서 제출 문서는 HY-IN의 프로젝트1 과제페이지에 제출하며, 보고서의 파일명은 다음 규칙을 지켜야 한다. \\uf0b7 {학번}\_{이름}\_P{프로젝트 번호}.pdf \\uf0b7 예: 1234567890\_홍길동\_P1.pdf 해당프로 젝트의 제출기한과 제출 기한이 지난 후 제출했을 때의 페널티는 다음과 같다. \\uf0b7 제출 기한: 2020년 10월 11일 23:59 ', 'page': 0}
{'text': ' \\uf0b7 페널티 \\uf0fc 1주 초과: 30%', 'page': 0}
{'text': ' \\uf0fc 2주 초과: 50% \\uf0fc 3주 초과: 70% \\uf0fc 그 외: 100%', 'page': 1}
   



```
paper_text 의 타입 : 딕셔너리 데이터를 저장한 리스트  
  

```
### 2) **텍스트 데이터프레임에 저장하기**

-create\_df

py def create\_df(data):

 if type(data) == list:
 print("Extracting text from pdf")
 print("Creating dataframe")
 filtered\_pdf = []
 # print(pdf.pages[0].extract\_text())
 for row in data:
 filtered\_pdf.append(row)
 df = pd.DataFrame(filtered\_pdf)
 # remove elements with identical df[text] and df[page] values
 df = df.drop\_duplicates(subset=["text", "page"], keep="first")
 # df['length'] = df['text'].apply(lambda x: len(x))
 print("Done creating dataframe")

 elif type(data) == str:
 print("Extracting text from txt")
 print("Creating dataframe")
 # Parse the text and add each paragraph to a column 'text' in a dataframe
 df = pd.DataFrame(data.split("\\n"), columns=["text"])

 return df

def extract\_pdf(pdf):
...
 return paper\_text

# file processing 
pdf = PdfReader("./pdf/2021 DB 프로젝트 1.pdf")
paper\_text = extract\_pdf(pdf)

# 데이터프레임으로 변환
df = create\_df(paper\_text)
print(df)
   
결과

  


  


  


textParsing paper
Total number of pages: 2
Done parsing paper
Extracting text from pdf
Creating dataframe
Done creating dataframe
 text page
0 프로젝트 1: 요구사항 분석 2021년 9월 30일 과목명: 데이터베이스 시... 1
1 2. 제약 사항 서비스 요구사항은 다음과 같은 entity와 요구 사항을 반드시... 1
2  사용자는 자신의 계좌에서 돈을 출금할 수 있다. 위 사항들 외의 다른 개... 1
3 3. 요구사항 분석 문서 제출 문서는 HY-IN의 프로젝트1 과제페이지에 제출하... 1
4  페널티  1주 초과: 30% 1
5  2주 초과: 50%  3주 초과: 70%  그 외: 100% 2### **3) 텍스트 임베딩 계산**

-embeddings

py import openai
from openai.embeddings\_utils import get\_embedding

def embeddings(df):
 print("Calculating embeddings")
 openai.api\_key = OPENAI\_API\_KEY
 embedding\_model = "text-embedding-ada-002"
 embeddings = df.text.apply([lambda x: get\_embedding(x, engine=embedding\_model)])
 df["embeddings"] = embeddings
 print("Done calculating embeddings")
 return df

# process start
# file processing 
pdf = PdfReader("./pdf/2021 DB 프로젝트 1.pdf")
paper\_text = extract\_pdf(pdf)

# dataframe 
df = create\_df(paper\_text)

# embeddings
df = embeddings(df)
print(df)
   



```
openai.embeddings_utils 의 get_embedding을 활용하여 임베딩 계산을 진행해보았습니다.
```
임베딩 모델은 `"text-embedding-ada-002"` 로 했습니다.

  


결과

textExtracting text from pdf
Creating dataframe
Done creating dataframe
Calculating embeddings
Done calculating embeddings
 text page embeddings
0 프로젝트 1: 요구사항 분석 2021년 9월 30일 과목명: 데이터베이스 시... 1 [-0.016610940918326378, -0.014788423664867878,...
1 2. 제약 사항 서비스 요구사항은 다음과 같은 entity와 요구 사항을 반드시... 1 [-0.0019020343897864223, -0.0229952335357666, ...
2  사용자는 자신의 계좌에서 돈을 출금할 수 있다. 위 사항들 외의 다른 개... 1 [0.0006928570219315588, -0.021132981404662132,...
3 3. 요구사항 분석 문서 제출 문서는 HY-IN의 프로젝트1 과제페이지에 제출하... 1 [-0.011420967057347298, -0.010231013409793377,...
4  페널티  1주 초과: 30% 1 [-0.00863182358443737, -0.007522017695009708, ...
5  2주 초과: 50%  3주 초과: 70%  그 외: 100% 2 [-0.011074927635490894, -0.025525201112031937,...  


  


