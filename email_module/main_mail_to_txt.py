import os
import re
import email
from nasa_mailbox import mailbox
from nasa_utils import NASA_UTILS

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

md_folder_name = "tmp_md"

if __name__ == "__main__":

    path_of_this_file = os.path.dirname(os.path.realpath(__file__))
    os.chdir(path_of_this_file)
    try:
        os.mkdir(md_folder_name)
    except:
        os.chdir(md_folder_name)
        for file in os.listdir():
            os.remove(file)
        os.chdir(path_of_this_file)

    # NASA_UTILS.print_log("init pop3 connection")  
    mail = mailbox('E_MAIL_ID', 'PASSWORD')

    mail.pop3_connected = False
    mail.__connect_pop3__()
    all_mail_list = mail.conn_pop3.list()[1]

    # 최근 50개의 메세지만 확인
    TOP_N_MESSAGE = 100

    # 지금까지 수신한 메일의 UID 가져오기
    # sql_get_all_mail_uid = "select id from nasa_mail"
    # df = NASA_UTILS.show_sql(sql_get_all_mail_uid, settings['path_to_db_file'], False)

    # all_mail_uids = []
    # if df is not None:
    #     all_mail_uids = df['id'].to_list()

    # 메일 가져오기를 스킵할 송신인
    pass_list = ['security@aptmail.nice.co.kr']

    for i, bb in enumerate([int(aa.decode('ASCII').split(' ')[0]) for aa in all_mail_list[-1*TOP_N_MESSAGE:]]):
        # list 에서 나오는 id는 index 로 uniqueness 를 보장하지 않음
        # 따라서 최근 N개를 가져온 이후 UID 대조 필요

        with open(f"{md_folder_name}/tmp_{i}.md", 'w', encoding='utf-8') as f:
      
            (server_msg, body, octets) = mail.conn_pop3.retr(bb)

            msg = email.message_from_bytes(b'\n'.join(body))

            re_parsed = {}

            re_parsed['subject'] = NASA_UTILS.try_decode(msg['subject'])
            re_parsed['from'] = get_markup_tag(msg['FROM'])
            re_parsed['to'] = get_markup_tag(msg['TO'])
            re_parsed['cc'] = get_markup_tag(msg['CC'])
            re_parsed['date'] = msg['Date']
            re_parsed['body'] = remove_multiple_spaces(clean_markup(NASA_UTILS.parse_orig_text(msg, google=True)).replace('> ', ''))

            f.write("-----start of a email-----")
            if re_parsed['from'] not in pass_list:
                for k in ['subject', 'from', 'to', 'cc', 'date', 'body']:
                    f.write(f"<{k}>\n{re_parsed[k]}\n\n\n")
            f.write("-----end of a email-----")

    mail.conn_pop3.close()