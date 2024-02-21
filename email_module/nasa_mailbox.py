from poplib  import POP3


class mailbox:
    # 생성 - ID/PW 정보 수신
    host_name = "" 
    user_name = ""
    pass_name = ""
    debug_flag = True
    pop3_connected = False
    conn_pop3 = None

    def __init__(self, user_id, pass_name, host_name = "pop3.nice.co.kr"):
        # self.credential = credential
        self.user_name = user_id
        self.pass_name = pass_name
        self.host_name = host_name
       

    def debug(self, *msgs):
        if self.debug_flag:
            print(' '.join([str(aa) for aa in msgs]))


    def __connect_pop3__(self):
        """\brief Method for connecting to POP3 server                        
        \return True   If connection to POP3 succeeds or if POP3 is already connected
        \return False  If connection to POP3 fails
        """
        #------Check that POP3 is not already connected-----------------------
        if not self.pop3_connected:
            #------Connect POP3-----------------------------------------------
            self.debug(100, 'Connecting POP3 with: ', self.host_name, self.user_name, self.pass_name)
            self.conn_pop3 = POP3(self.host_name)            
            res1 = self.conn_pop3.user(self.user_name)
            string1 = str(res1)      
            self.debug(100, 'User identification result:', string1) 
            res2 = self.conn_pop3.pass_(self.pass_name)        
            string2 = str(res2)                
            self.debug(100, 'Pass identification result:', string2)                        
            #------Check if connection resulted in success--------------------
            #------Server on DavMail returns 'User successfully logged on'----
            if  string2.find('OK Login successful') > -1 or string1.find('User successfully logged on') > -1 :
                self.pop3_connected = True            
                return True
            else:
                return False
            #endif         
        else:       
            self.debug(255, 'POP3 already connected')
            return True
        #endif 