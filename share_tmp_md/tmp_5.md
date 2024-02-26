# TITLE: 유사도 검사 및 OpenAI 호출 실습

### 1) 유사도가 높은 데이터 조각

search

py# 쿼리문과 코사인 유사도가 높은 상위 n개의 조각을 데이터프레임에서 얻습니다
def search(df, query, n=1, pprint=True):
 query\_embedding = get\_embedding(query, engine="text-embedding-ada-002")
 df['similarity'] = df.embedding.apply(lambda x: cosine\_similarity(x, query\_embedding))

 results = df.sort\_values("similarity", ascending=False, ignore\_index=True)
 results = results.head(n)
 sources = []
 
 for i in range(n):
 # 유사도가 크다고 나온 데이터에 대한 정보
 sources.append({"Page " + str(results.iloc[i]["page"]): results.iloc[i]["text"][:150] + "..."})
 
 return {"results": results, "sources": sources}  


코사인 유사도 계산 : openai api -cosine\_similiary()호출

질의과 유사도가 높은 상위 n개의 데이터프레임 반환

매우 작은 pdf를 활용하여 실습중이였기 때문에 코사인 유사도가 가장 높은 1개의 리스트만을 반환하도록 하였습니다.

  


### 2) **프롬프트 작성**

create\_prompt

pydef create\_prompt(df, user\_input):
 print('Creating prompt')

 result = search(df, user\_input, n=1)
 data = result['results']
 sources = result['sources']
 system\_role = """Your role is ..."""
 user\_input = user\_input + """
 Here are the embeddings:

 1.""" + str(data.iloc[0]['text']) + """
 """

 history = [
 {"role": "system", "content": system\_role},
 {"role": "user", "content": str(user\_input)}]

 print('Done creating prompt')

 return {'messages': history, 'sources': sources}  


system\_role : AI에게 적절하고 구체적인 역할을 부여해준다.

  


### 3) **api 호출함 및 결과**

gpt

pydef gpt(context, sources):
 print('Sending request to OpenAI')
 openai.api\_key = OPENAI\_API\_KEY
 r = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=context)
 answer = r.choices[0]["message"]["content"]
 print('Done sending request to OpenAI')
 response = {'answer': answer, 'sources': sources}
 return response  


**호출 결과**  
  
1)

pyquery : 교수님 성함이랑 이메일 알려줘
answer :
{'answer': '교수님 성함은 김상욱이며 교수님의 이메일은 wook@hanyang.ac.kr입니다.', 
 'sources': [{'Page 1': ' 프로젝트 1: 요구사항 분석 2021년 9월 30일 과목명: 데이터베이스 시 스템 및 응용 교수: 김상욱 (이메일: wook@hanyang.ac.kr ) 조교: 서동혁 (이메일: hyuk125@agape.hanyang.ac.kr ), 손지원 (이메일: ...'}]}  
2)

pyquery : 조교님은 몇분 계셔? 성함이랑 이메일도 알려줘
answer :
{'answer': '저는 AI 조교이기 때문에 실제 조교님이 몇 분 계시는지 알 수 없습니다. 또한, 프로젝트 제목, 날짜, 교수님의 성함과 이메일 주소, 그리고 조교님들의 성함과 이메일 주소도 알려드릴 수는 없습니다. 제가 도움을 드릴 수 있는 부분이 있다면 다른 질문을 주시면 성심성의껏 도움을 드리겠습니다.', 
 'sources': [{'Page 1': ' 프로젝트 1: 요구사항 분석 2021년 9월 30일 과목명: 데이터베이스 시스템 및 응용 교수: 김상욱 (이메일: wook@hanyang.ac.kr ) 조교: 서동혁 (이메일: hyuk125@agape.hanyang.ac.kr ), 손지원 (이메일: ...'}]} system\_role에 AI assistant라고 설명을해서, 해당 답변을 준 것 같다.

 system\_role 수정후

pyquery : 조교님은 몇명이야? 성함이랑 이메일도 알려줘
answer :
{'answer': '조교님은 2명이며, 성함은 서동혁과 손지원입니다. 이메일은 서동혁의 이메일은 hyuk125@agape.hanyang.ac.kr, 손지원의 이메일은 taerik@agape.hanyang.ac.kr 입니다.', 
 'sources': [{'Page 1': ' 프로젝트 1: 요구사항 분석 2021년 9월 30일 과목명: 데이터베이스 시스템 및 응용 교수: 김상욱 (이메일: wook@hanyang.ac.kr ) 조교: 서동혁 (이메일: hyuk125@agape.hanyang.ac.kr ), 손지원 (이메일: ...'}]}  


3)

pyquery : 페널티에 대해 알려줘
answer : 
{'answer': '박탈,벌금,벌점 또는 제재로 인한 불이익을 의미하는 페널티에 대해 설명해 드리겠습니다. 페널티는 행동의 부정적인 결과로 인해 부과되며, 이때 일정 비율의 벌칙으로 표현될 수 있습니다. 예를 들어, 1주 초과하는 경우에는 30%의 벌칙이 부과될 수 있습니다.'
, 'sources': [{'Page 1': ' \uf0b7 페널티 \uf0fc 1주 초과: 30%...'}]}페널티에 대한 사전적 의미를 알려준다.

추가로, 페널티에 관한 부분이 page 1-2에 걸쳐있기 때문에, 정보가 분리되어있다.

유사도가 높은 블록 1개만을 찾았기 때문에, 정보가 누락되었다.

  


블록 2개로 검색 + pdf에 대한 내용만 언급하도록 지정 + 구체적인 질문

pyquery : 프로젝트 기간이 초과된 경우의 페널티에 대해 알려줘
answer : 
{'answer': '프로젝트의 제출 기한은 2020년 10월 11일 23:59입니다. 제출 기한을 초과하게 되면 페널티가 부과됩니다. 아쉽게도 페널티에 대한 구체적인 내용은 제공되지 않았습니다.',
 'sources': [{'Page 1': ' 3. 요구사항 분석 문서 제출 문서는 HY-IN의 프로젝트1 과제페이지에 제출하며, 보고서의 파일명은 다음 규칙을 지켜야 한다. \uf0b7 {학번}\_{이름}\_P{프로젝트 번 호}.pdf \uf0b7 예: 1234567890\_홍길동\_P1.pdf 해당프로젝트의 제출기한과 제출 기한...'}, {'Page 1': ' \uf0b7 페널티 \uf0fc 1주 초과: 30%...'}]}정보들이 너무 잘게 쪼개져 있어, 잘 찾지 못한다.

  


4)

pyquery : 프로젝트의 목표에 대해 알려줘
answer :
{'answer': '프로젝트의 목표는 사용자가 자신의 계좌에서 돈을 출금할 수 있는 DBMS 활용 서비스를 개발하는 것입니다. 이를 위해 잘 설계된 entity와 attribute를 사용하고 구체적이며 풍 부한 요구사항을 추가해야 합니다. 이 프로젝트는 프로젝트1부터 4까지 진행되며, 수강생들은 본인이 설계한 요구사항을 바탕으로 개발 작업을 진행하게 됩니다.',
 'sources': [{'Page 1': ' \uf0fc 사용자는 자신의 계좌에서 돈을 출금할 수 있다. 위 사항들 외의 다른 개체와 요구사항을 추가할 수 있다. 잘 설계된 entity 및 attribute와 구체적이고 풍부한 요구 사항에는 더 높은 점수가 부여된다. 수강생들은 프로젝트1부터 4까지 진행하며 최종적...'}, {'Page 1': ' 3. 요구사항 분석 문서 제출 문서는 HY-IN의 프로젝트1 과제페이지에 제출하며, 보고서의 파 일명은 다음 규칙을 지켜야 한다. \uf0b7 {학번}\_{이름}\_P{프로젝트 번호}.pdf \uf0b7 예: 1234567890\_홍길동\_P1.pdf 해당프로젝트의 제출기한과 제출 기한...'}]}  


5)

pyquery : 과목 이름을 알려줘
answer :
{'answer': '과목 이름은 HY-IN의 프로젝트1입니다.',
 'sources': [{'Page 1': ' 3. 요구사항 분석 문서 제출 문서는 HY-IN의 프로젝트1 과제페이지에 제출하며, 보고서의 파일명은 다음 규칙을 지켜야 한다. \uf0b7 {학번}\_{이름}\_P{프로젝트 번호}.pdf \uf0b7 예: 1234567890\_홍길동\_P1.pdf 해당프로젝트의 제출기한과 제출 기한...'}, {'Page 1': ' 프로젝트 1: 요구사항 분석 2021년 9월 30일 과목명: 데이터베이스 시스템 및 응용 교수: 김상욱 (이메일: wook@hanyang.ac.kr ) 조교: 서동혁 (이메일: hyuk125@agape.hanyang.ac.kr ), 손지원 (이메일: ...'}]}  


pyquery : 과목 이름이 뭐야?
answer :
{'answer': '과목 이름은 "데이터베이스 시스템 및 응용"입니다.',
 'sources': [{'Page 1': ' 프로젝트 1: 요구사항 분석 2021년 9월 30일 과목명: 데이터베이스 시스템 및 응용 교수: 김상욱 (이메일: wook@hanyang.ac.kr ) 조교: 서동혁 (이메일: hyuk125@agape.hanyang.ac.kr ), 손지원 (이메일: ...'}, {'Page 1': ' 3. 요구사항 분석 문서 제출 문서는 HY-IN의 프 로젝트1 과제페이지에 제출하며, 보고서의 파일명은 다음 규칙을 지켜야 한다. \uf0b7 {학번}\_{이름}\_P{프로젝트 번호}.pdf \uf0b7 예: 1234567890\_홍길동\_P1.pdf 해당프로젝트의 제출기 한과 제출 기한...'}]}거의 같은 질문인데도, 답변이 제각각이다.

  


