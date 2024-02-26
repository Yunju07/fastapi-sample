# TITLE: pdf 추출 실습 (파이썬 라이브러리 활용)

  


PDF 에서 텍스트를 추출하는 라이브러리 → PyMuPDF, PyPDF2, pdfminer.six, pdfplumber

PDF 파일의 표 데이터를 판다스 데이터프레임 객체로 조회 → tabula

  


### 1) PyMuPDF

* PyMuPDF 라이브러리 설치
* fitz 모듈 임포트

py import fitz

# 실습 pdf 파일 경로
PDF\_FILE\_PATH = "./pdf/2021 DB 프로젝트 1.pdf"

doc = fitz.open(PDF\_FILE\_PATH)
for page in doc:
 text = page.get\_text()
 print(text)
   


text 프로젝트 1: 요구사항 분석 
2021년 9월 30일
과목명: 데이터베이스 시스템 및 응용
교수: 김상욱 (이메일: wook@hanyang.ac.kr)
조교: 서동혁 (이메일: hyuk125@agape.hanyang.ac.kr), 
 손지원 (이메일: taerik@agape.hanyang.ac.kr)

1. 목표
DBMS를 활용하는 서비스 개발에 필요한 요구사항 분석 및 문서화
2. 제약 사항
서비스 요구사항은 다음과 같은 entity와 요구 사항을 반드시 포함해야 한다.

[은행 서비스 DBMS 개발]

Entity: 관리자, 사용자, 계좌

요구사항
 관리자는 각 사용자의 계좌 입출금 내역을 관리한다. 
 사용자는 자신의 계좌를 n개까지 개설하거나 삭제한다. 
 사용자는 자신의 계좌에 돈을 입금할 수 있다.
 사용자는 자신의 계좌에서 돈을 출금할 수 있다.

위 사항들 외의 다른 개체와 요구사항을 추가할 수 있다. 잘 설계된 entity 및 attribute와 구체적이고 풍부한 요구 
사항에는 더 높은 점수가 부여된다. 수강생들은 프로젝트1부터 4까지 진행하며 최종적으로 본인이 설계한 요구
사항을 바탕으로 한 DBMS 활용 서비스를 개발하게 될 것이다. 
3. 요구사항 분석 문서 제출
문서는 HY-IN의 프로젝트1 과제페이지에 제출하며, 보고서의 파일명은 다음 규칙을 지켜야 한다.

{학번}\_{이름}\_P{프로젝트 번호}.pdf

예: 1234567890\_홍길동\_P1.pdf
해당프로젝트의 제출기한과 제출 기한이 지난 후 제출했을 때 의 페널티는 다음과 같다.

제출 기한: 2020년 10월 11일 23:59

페널티
 1주 초과: 30%

 2주 초과: 50%
 3주 초과: 70%

그 외: 100%
   



```
2) PyPDF2
```
* PyPDF2 라이브러리 설치 - `pip install PyPDF2`
* `from PyPDF2 import PdfReader`

  


  


  


pyimport fitz
from PyPDF2 import PdfReader

# 실습 pdf 파일 경로
PDF\_FILE\_PATH = "./pdf/2021 DB 프로젝트 1.pdf"

# PyMuPDF 
# doc = fitz.open(PDF\_FILE\_PATH)
# for page in doc:
# text = page.get\_text()
# print(text)

# PyPDF2 
reader = PdfReader(PDF\_FILE\_PATH)
pages = reader.pages
text = ""
for page in pages:
 sub = page.extract\_text()
 text += sub
print(text)  


  


text 프로젝트 1: 요구사항 분석 
2021년 9월 30일
과목명: 데이터베이스 시스템 및 응용
교수: 김상욱 (이메일: wook@hanyang.ac.kr )
조교: 서동혁 (이메일: hyuk125@agape.hanyang.ac.kr ), 
 손지원 (이메일: taerik@agape.hanyang.ac.kr )

1. 목표
DBMS를 활용하는 서비스 개발에 필요한 요구사항 분석 및 문서화
2. 제약 사항
서비스 요구사항은 다음과 같은 entity와 요구 사항을 반드시 포함해야 한다.
 [은행 서비스 DBMS 개발]
 Entity: 관리자, 사용자, 계좌
 요구사항
 관리자는 각 사용자의 계좌 입출금 내역을 관리한다. 
 사용자는 자신의 계좌를 n개까지 개설하거나 삭제한다. 
 사용자는 자신의 계좌에 돈을 입금할 수 있다.
 사용자는 자신의 계좌에서 돈을 출금할 수 있다.

위 사항들 외의 다른 개체와 요구사항을 추가할 수 있다. 잘 설계된 entity 및 attribute와 구체적이고 풍부한 요구 
사항에는 더 높은 점수가 부여된다. 수강생들은 프로젝트1부터 4까지 진행하며 최종적으로 본인이 설계한 요구
사항을 바탕으로 한 DBMS 활용 서비스를 개발하게 될 것이다. 
3. 요구사항 분석 문서 제출
문서는 HY-IN의 프로젝트1 과제페이지에 제출하며, 보고서의 파일명은 다음 규칙을 지켜야 한다.
 {학번}\_{이름}\_P{프로젝트 번호}.pdf
 예: 1234567890\_홍길동\_P1.pdf
해당프로젝트의 제출기한과 제출 기한이 지난 후 제출했을 때 의 페널티는 다음과 같다.
 제출 기한: 2020년 10월 11일 23:59
 페널티
 1주 초과: 30%  2주 초과: 50%
 3주 초과: 70%
 그 외: 100%
   


  


  


**3) tabula**
-------------

* 표 데이터 추출 & 판다스 데이터 프레임으로 저장

표데이터

  


py import tabula

# 실습 pdf 파일 경로
PDF\_FILE\_PATH = "./pdf/chart\_test.pdf"

# tabula
dfs = tabula.read\_pdf(PDF\_FILE\_PATH, pages="all", encoding='CP949')
print(len(dfs))
print(dfs[0])
   


text 1 # 표의 개수
 0 1 2 3
0 A A1 A2 A3
1 B B1 B2 B3
2 C C1 C2 C3
3 D D1 D2 D3

  



```
첫번째 줄을 column 명으로 설정해주고,
```
index (row명) 은 0부터 인덱싱을 해준다.

  


  


  


