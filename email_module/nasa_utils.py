import datetime
import sqlite3
import re
import smtplib
import base64
import pandas as pd
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path


class NASA_UTILS:
    @staticmethod
    def print_log(text:str, logs:list=None):
        tz = datetime.timezone(datetime.timedelta(hours=9))
        now = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")    
        output = f"[{now}] {text}"
        print(output)

        if logs is not None:
            logs.append(output)

    @staticmethod
    def current_dt():
        tz = datetime.timezone(datetime.timedelta(hours=9))
        now = datetime.datetime.now(tz).strftime("%Y%m%d%H%M%S")
        return now

    @staticmethod
    def is_db_created(DB_PATH: str, debug=False):

        # 메일 원장
        query = "select count(*) from nasa_mail"
        if NASA_UTILS.show_sql(query, DB_PATH, debug=debug, check_existance=False) is None:
            create_db_query = """
            create table nasa_mail (
                  id                  varchar(40)
                , sender              text
                , subject             text
                , received_dt         varchar(14)
                , msg                 text
                , work_dt             varchar(14)
                , PRIMARY KEY (id)
            )
            """
            NASA_UTILS.exec_sql(create_db_query, DB_PATH, debug=debug, check_existance=False)

        # 메일 내 첨부파일
        query = "select count(*) from nasa_submits"
        if NASA_UTILS.show_sql(query, DB_PATH, debug=debug, check_existance=False) is None:
            create_db_query = """
            create table nasa_submits (
                  id                  varchar(40)
                , seq                 integer
                , filename            text
                , filename_converted  text
                , challange_gb        varchar(5)
                , team_id             varchar(10)
                , reply_to            text
                , msg                 text
                , work_dt             varchar(14)
                , PRIMARY KEY (id, seq)
            )
            """
            NASA_UTILS.exec_sql(create_db_query, DB_PATH, debug=debug, check_existance=False)

        # 첨부파일 별 산출 스코어
        query = "select count(*) from nasa_leaderboard"
        if NASA_UTILS.show_sql(query, DB_PATH, debug=debug, check_existance=False) is None:
            create_db_query = """
            create table nasa_leaderboard (
                  round_id            varchar(10)
                , challange_gb        varchar(5)
                , id                  varchar(40)
                , seq                 integer                
                , score1              real
                , score2              integer
                , msg                 text
                , PRIMARY KEY (round_id, challange_gb, id, seq)
            )
            """
            NASA_UTILS.exec_sql(create_db_query, DB_PATH, debug=debug, check_existance=False)

        # 산출 round 별 시간
        query = "select count(*) from nasa_round"
        if NASA_UTILS.show_sql(query, DB_PATH, debug=debug, check_existance=False) is None:
            create_db_query = """
            create table nasa_round (
                  round_id varchar(10)
                , challange_gb varchar(5)
                , round_dt varchar(14)                
                , PRIMARY KEY (round_id, challange_gb)
            )
            """
            NASA_UTILS.exec_sql(create_db_query, DB_PATH, debug=debug, check_existance=False)

        # 산출 round 별 시간
        query = "select count(*) from nasa_team"
        if NASA_UTILS.show_sql(query, DB_PATH, debug=debug, check_existance=False) is None:
            create_db_query = """
            create table nasa_team (
                  team_id varchar(10)
                , gb varchar(5)
                , team_nm text
            )
            """
            NASA_UTILS.exec_sql(create_db_query, DB_PATH, debug=debug, check_existance=False)
        return
        
    @staticmethod
    def exec_sql(sql: str, DB_PATH: str, debug=False, check_existance=True):
        if check_existance:
            NASA_UTILS.is_db_created(DB_PATH, debug)

        conn = sqlite3.connect(DB_PATH)
        _cur = conn.cursor()
        
        try:
            if debug == True:
                NASA_UTILS.print_log(sql)
                
            _cur.execute(sql)        
            
            NASA_UTILS.print_log(_cur.rowcount)

        except Exception as e:
            NASA_UTILS.print_log(e)
            conn.rollback()
            return False
        else:
            conn.commit()
        
        if debug == True:
            NASA_UTILS.print_log("sql done")
        _cur.close()
        conn.close()

        return True
    

    @staticmethod
    def show_sql(sql: str, DB_PATH: str, debug=False, check_existance=True):
        if check_existance:
            NASA_UTILS.is_db_created(DB_PATH, debug)

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        _data_ = None
        _columns_ = None
        # _cur = conn.cursor()
        
        try:
            if debug == True:
                NASA_UTILS.print_log(sql)
                
            # _data_ = conn.execute(sql)

            rows = conn.execute(sql).fetchall()

            if rows:        
                # 첫번째 데이터에서 컬럼명을 가져와야 함
                _columns_ = rows[0].keys() 
                _data_ = [list(row) for row in rows]
            
            # print_log(_cur.rowcount)

        except Exception as e:
            NASA_UTILS.print_log(e)
            conn.rollback()
        else:
            conn.commit()
        
        if debug == True:
            NASA_UTILS.print_log("sql done")
        conn.close()
        
        # 데이터가 있을때만 dataframe 반환
        if _data_:
            df = pd.DataFrame(_data_, columns = _columns_)
            return df    
        
        return None
    
    @staticmethod
    def df_to_db(DB_PATH: str, df:pd.DataFrame, tablename:str, debug=False, check_existance=True, if_exists="append"):
        if check_existance:
            NASA_UTILS.is_db_created(DB_PATH, debug)

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        _data_ = None
        _columns_ = None
        # _cur = conn.cursor()
        
        try:
            if debug == True:
                NASA_UTILS.print_log(f"[df_to_db] {tablename}")
                
            df.to_sql(tablename, con=conn, if_exists=if_exists, index=False)

        except Exception as e:
            NASA_UTILS.print_log(e)
            conn.rollback()
            return False
        else:
            conn.commit()
        
        if debug == True:
            NASA_UTILS.print_log("sql done")
        conn.close()
                
        return True

    @staticmethod
    def validate_email(email:str):
        """
        Validates an email address.

        Args:
        email: The email address to validate.

        Returns:
        True if the email address is valid, False otherwise.
        """
        # Regular expression to match a valid email address.
        regex = r"^([\w\-_\.\+]+@[\w\-_\.]+\.[a-zA-Z]{2,4})([,;][ ]{0,1}[\w\-_\.\+]+@[\w\-_.]+\.[a-zA-Z]{2,4})*$"

        #마지막 세미콜론은 삭제
        if email.strip()[-1] == ';':
            email = email.strip()[:-1]

        # Check if the email address matches the regular expression.
        if re.match(regex, email):
            return True
        else:
            return False

    @staticmethod
    def extract_email(text:str):
        """Extracts email addresses from a string.

        Args:
            text: The string to extract email addresses from.

        Returns:
            A list of email addresses.
        """

        # Create a regular expression to match email addresses.
        email_regex = re.compile(r'[\w\-_\.\+]+@[\w\-_\.]+\.[a-zA-Z]{2,4}')

        # Find all matches for the regular expression in the text.
        matches = email_regex.findall(text)

        # Return a list of the email addresses.
        return matches


    @staticmethod
    def validate_pipe_delimetered(text:bytes):
        """
        파이프 구분자로, 두 개 값이 들어와있으면 정상, 아니면 오류
        """
        if (text is not None) and len(text) >= 3 and len(text.split(b'|')) == 2:
            return True
        return False

    @staticmethod
    def validate_population(full_path:Path, challenge_gb:str, target:dict, pop_dir:str):
        """
        모수 일치여부 확인
        """

        # population 파일 경로 확인
        population_filename = [aa['name'] for aa in target['settings']['population_filenames'] if aa['challenge_gb'] == challenge_gb][0]
        population_path = Path(pop_dir) / population_filename

        file_enc = NASA_UTILS.infer_hangul_encoding_by_file(full_path)

        if challenge_gb == 'c2':
            # Read the answer data
            answer_df = pd.read_csv(population_path.as_posix(), sep='|', names=['biz_desc'], dtype='str')

            # Read the submitted data
            submit_df = pd.read_csv(full_path.as_posix(), sep='|', skiprows=1, names=['biz_desc', 'goods_cd'], dtype='str', encoding=file_enc)
            
            # # Compare the join keys in the answer and submitted data
            if not set(answer_df['biz_desc']) == set(submit_df['biz_desc']):
                raise Exception('정답 모수 불일치')

        elif challenge_gb in ['c1_1', 'c1_2']:
            # Read the answer data
            answer_df = pd.read_csv(population_path.as_posix(), sep='|', names=['shop_key'], dtype='str')

            # Read the submitted data
            submit_df = pd.read_csv(full_path.as_posix(), sep='|', skiprows=1, names=['shop_key', 'y_submit'], dtype='str', encoding=file_enc)
                        
            # # Compare the join keys in the answer and submitted data
            if not set(answer_df['shop_key']) == set(submit_df['shop_key']):
                raise Exception('정답 모수 불일치')
            
        else:
            raise Exception('challange_gb 오류')
        return None






        # filename_part = full_path.name
        # target_filenames = target["target_filenames"]

        # # 입수된 파일명을 기준으로 prefix로 탐색하여 challenge_gb을 가져옴
        # target_file_matched = [names['challenge_gb'] for names in target_filenames if filename_part.startswith(names['name_prefix'])]

        # if len(target_file_matched) == 1: # 1개가 아닐때는 정상이 아니다...
        #     # population 비교
        #     challenge_gb = target_file_matched[0]


        # return None


    @staticmethod
    def infer_challange_gb(filename:str, target:dict):
        target_file_matched = [names['challenge_gb'] for names in target['target_filenames'] if filename.startswith(names['name_prefix'])]
        if len(target_file_matched) == 1:
            return target_file_matched[0]
        return None

    @staticmethod
    def infer_hangul_encoding(text:bytes):
        encoding = ""
        if len(text) > 0:
            try:                
                if text.decode("utf-8-sig") == text.decode("utf-8"):
                    encoding = "utf-8"
                else:
                    encoding = "utf-8-sig"
            except Exception as e:
                try:
                    encoding = "cp949"
                    text.decode(encoding)
                except Exception as e:
                    try:                        
                        encoding = "ascii"
                        text.decode(encoding)
                    except Exception as e:
                        encoding = None

        return encoding

    @staticmethod
    def infer_hangul_encoding_by_file(full_path:Path):
        if full_path.is_file():
            with open(full_path.as_posix(), "rb") as fp:
                lines = fp.readlines()[:2]

            return NASA_UTILS.infer_hangul_encoding(lines[1])
        
        return None

    @staticmethod
    def validate_file_format(filename:Path, all_ids:list):
        # filename = Path('./nasa23_c2_submit_enc.csv')
        if filename.is_file():
            with open(filename.as_posix(), "rb") as fp:
                lines = fp.readlines()[:2]

            # validate id & email
            try: 
                enc = NASA_UTILS.infer_hangul_encoding(lines[0])
                if enc:
                    first_line = lines[0].decode(enc).strip()
                else:
                    first_line = lines[0].decode('ascii').strip()
            except Exception as e:
                raise Exception("헤더 인코딩 오류")
            
            if len(first_line.split('|')) == 2:
                v1 = NASA_UTILS.validate_email(first_line.split('|')[1])
                v3 = first_line.split('|')[0] in all_ids
            else:
                v1 = False
                v3 = False

            # validate text format
            v2 = NASA_UTILS.validate_pipe_delimetered(lines[1])

            if not NASA_UTILS.infer_hangul_encoding(lines[1]):
                raise Exception("본문 인코딩 오류")                

            if v1 and v2 and v3:
                return True
            elif not v1 and not v3:
                raise Exception("헤더 오류")
            elif not v2:
                raise Exception("정답 형식 오류")
            elif not v1:
                raise Exception("이메일 형식 오류")
            elif not v3:
                raise Exception("아이디 검증 오류")
        else:
            raise Exception("파일 없음")
        
        return False
                
    @staticmethod
    def create_msg(sender:str, recipient:str, subject:str, body:str):
        # Create a MIMEMultipart object
        msg = MIMEMultipart()

        # Set the subject and body of the email
        msg['From'] = sender
        msg['Sender'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(body, "plain"))

        return msg

    @staticmethod
    def sendmail(sender, sender_pw, recipient, msg:MIMEMultipart):
        smtp = smtplib.SMTP("smtp.nice.co.kr", 25)
        smtp.ehlo()

        id_b64 = base64.b64encode(sender.encode()).decode('ascii')
        pass_b64 = base64.b64encode(sender_pw.encode()).decode('ascii')

        smtp.docmd("AUTH LOGIN")
        smtp.docmd(id_b64)
        smtp.docmd(pass_b64)
        
        smtp.sendmail(sender, recipient, msg.as_string())
        smtp.quit()
        return True

    @staticmethod
    def send_email_with_file(filename:Path, target:dict):
        NASA_UTILS.print_log(f"이메일 발송! [{filename.as_posix()}]")
        
        # Get the current date and time
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")    
        
        # 메세지 내용
        body = f"{filename} 에서 읽은 파일입니다. 작업일시 : {now}"

        # nasa 계정으로 발송하고, 수신은 nasa_submit 으로 -> 별도의 프로세스로 nasa_submit으로 수신된 메일을 처리하여 리더보드는 첨부파일 내 포함된 첫번째 라인의 메일로 발송
        # Set the subject and body of the email
        msg = NASA_UTILS.create_msg(target['sender'], target['recipient'], subject=f"{target['settings']['mail_prefix']} {filename}", body=body)

        # Add the attachment
        with open(filename.as_posix(), "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={filename.name.replace(' ','_')}")

        # Attach the attachment to the email
        msg.attach(part)
        

        # Send the email
        NASA_UTILS.sendmail(target['sender'], target['sender_pw'], target['recipient'], msg)

        return True
    
    @staticmethod
    def parse_orig_text(msg, google=False):
        """
        Append each part of the orig message into 2 new variables
        (html and text) and return them. Also, remove any 
        attachments. If google=True then the reply will be prefixed
        with ">". The last is not tested with html messages...
        """
        # newhtml = ""
        newtext = ""

        for part in msg.walk():
            if (part.get('Content-Disposition')
                and part.get('Content-Disposition').startswith("attachment")):

                part.set_type("text/plain")
                part.set_payload("Attachment removed: %s (%s, %d bytes)"
                            %(NASA_UTILS.try_decode(part.get_filename()), 
                            part.get_content_type(), 
                            len(part.get_payload(decode=True))))
                del part["Content-Disposition"]
                del part["Content-Transfer-Encoding"]

            if part.get_content_type().startswith("text/plain") or part.get_content_type().startswith("text/html"):
                newtext += "\n"
                try:
                    tmp_text = part.get_payload(decode=True).decode("utf-8")
                except UnicodeDecodeError:
                    # 오류가 나면 cp949로 해보고 안되면 버림
                    try:
                        tmp_text = part.get_payload(decode=True).decode("cp949")
                    except Exception as e:
                        print(e)
                        tmp_text = ""
                
                # print(f"tmp_text : {tmp_text}, type : {type(tmp_text)}")
                
                # 테그 제외하고 등록
                newtext +=  re.sub('<[^>]+>', '', tmp_text)

        # 구글처럼 > 를 앞에 붙여 회신 본문 표시
        if google:
            newtext = newtext.replace("\n","\n> ")

        return newtext
    
    @staticmethod
    def try_decode(part:str):
        if part is None:
            return None
        
        _tmp_name_, _tmp_encoding_ = email.header.decode_header(part)[0] # 결과가 list 내 tuple 로 나오기 때문..
        if _tmp_encoding_ is not None:
            _tmp_name_ = _tmp_name_.decode(_tmp_encoding_)
        return _tmp_name_


    @staticmethod
    def backup_file(full_path:Path, prefix="checked_"):
        """
            현재시간으로 파일명 변경
        """
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S") 
        full_path.rename(full_path.parent / (f"{prefix}{full_path.name}.{now}"))
            
        return True