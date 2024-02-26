# TITLE: redis

  


**Window에 redis 설치하기**

**<https://redis.io/docs/install/install-redis/install-redis-on-windows/>**

1. WSL2 설치(Linux용 Windows 하위 시스템)
2. Redis 설치

  


redis 서버 시작하는 법

sudo service redis-server start
```


```
Redis CLI 로 연결하여 서버가 실행 중인지 테스트할 수 있다

redis-cli 
127.0.0.1:6379> ping 
PONG `WSL2로 Redis 서버 실행과 redis-cli 접속한 모습`

  


### **redis-cli** (Redis Command Line Interface)

Redis 데이터 베이스와 상호작용하기 위한 명령 줄 도구

  


**접속**

# localhost:6379접속
redis-cli

# 원격접속
redis-cli -h #{호스트명} -p #{포트번호}

# 정보보기
reids-cli info

# help
redis-cli help

# 모니터링
redis-cli monitor

#redis 서버 종료(cli종료가 아님)
redis-cli shutdown  


호스트명, 포트번호 생략시, [localhost:6379](http://localhost:6379) 로 접속

<다양한 옵션설정>

-n db번호

-a 비밀번호

-s 소켓

-u 서버 url

  


  


CRUD 명령어`keys*`

: 현재의 키값들을 확인.

저장된 키값이 없을 경우, (empty list or set) 출력

\*데이터가 많은 경우 부하가 심할 수 있으므로 주의

  


`get key`

: 주어진 키에 해당하는 값을 조회

키 값이 없을 경우, (nil) 출력

  


`mget key1 key2`

: 여러개의 키에 해당하는 값 조회

  


`set key value`

: 주어진 키와 값을 저장

  


`mset key1 value1 key2 value2`

:여러개의 key / value 형태를 저장

  


`setex key second value`

: 소멸시간 지정해서 저장하기. 시간은 초단위로 입력

  


`del key`

: 주어진 키와 해당하는 값을 삭제

성공 시, (integer) 1

key가 없을 경우, (interger) 0 출력

  


`ttl key` : 타임아웃까지 남은 시간을 초단위로 반환

`pttl key` : 타임아웃까지 남은 시간을 밀리 초단위로 반환

(integer) -2 → key값이 없거나 소멸됨

(integer) -1 → 기한이 없는 key

  


`keys *검색어*`

: key 검색하기. 검색어가 포함된 모든 key검색

  


`rename 기존key 변경할key`

:key 이름을 변경하기, 변경하려는 key 가 이미 있다면, 덮어쓴다.

  


`renamenx 기존key 변경할key`

:key 이름을 변경하기, 변경하려는 key가 이미 있다면, (integer 0) 을 출력하고 변경하지 않는다

  


`flushall`

: 모든 데이터(key와 value)를 삭제

  


  


### 파이썬에서 Redis 사용하기

  


실행 파이썬 코드

호스트와 포트는 기본으로 하여 연결

set 명령어로 하나의 key-value 값 저장 해주기

  


결과

get 명령어를 이용하여 조회

  


파이썬에서 데이터 저장 및 출력

### **백업방식**

Redis는 In Memroy 데이터 구조 저장소 → 메모리는 휘발성이므로, 프로세스를 종료하게 되면 데이터가 유실된다. 따라서, Redis를 캐시용도가 아닌 영구 저장하기 위해 Disk에 백업이 필요하다.

백업에 **AOF**(Append Only File) 와 **RDB**(Snapshot) 기능이 있다.

* AOF :
	+ 전달된 명령어를 파일에 기록. 재기동시 파일에 기록된 명령어를 일괄 수행하여 데이터를 복구하는데 사용된다
	+ 데이터 유실이 발생하지 않지만, 매 명령어마다, file과의 동기화가 필요하여 처리속도가 현격히 줄어든다. → 이를 해소하기위해 동기화 주기를 조절할 수 있으나, 그만큼 데이터 유실위험이 생긴다,
* RDB
	+ 특정 시점의 메모리 내용을 복사하여 파일에 기록하는 방법. 덤프파일에 저장
	+ 부하가 적으며, LZF 압축을 통해 파일 압축이 가능하다.
	+ 덤프 파일을 그대로 메모리에 복원하므로 AOF 보다 빠르다.
	+ 덤프를 기록한 시점 이후의 데이터는 저장되지 않는다.

  


**Redis UI 툴**

[Redis UI 툴 추천](https://thinkandthing.tistory.com/77)

  


Medis 리눅스 환경에 설치하기!

[[Redis] 레디스 GUI Medis 쉽게 설치하는 방법](https://enterone.tistory.com/527)

  


윈도우에 설치

<https://github.com/sinajia/medis/releases/tag/win>

Medis 사용 화면

  


