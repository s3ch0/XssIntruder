import os
import difflib
import re
import requests
from collections import namedtuple



class XssIntruder:
    def __init__(self) -> None:
        self.__target_url = ""
        self.__payload_path = "./payloads"
        self.__payloads = []
        self.__result = [] # save the intruder result in it
        self.save_path = "./result"

    @staticmethod
    def unicode_encoding(text:str):
        encoded_s = ''.join(['&#{};'.format(ord(c)) for c in text])
        print(encoded_s)  # Hello, &#19990;&#30028;!

    @property
    def result(self):
        return self.__result
    @property
    def url(self):
        return self.__target_url
    
    @property
    def target_url(self):
        return self.__target_url

    @url.setter
    def url(self,target_url):
        self.__target_url = target_url
    
    @property
    def payload_path(self):
        return self.__payload_path

    @payload_path.setter
    def payload_path(self,payload_path):
        self.__payload_path = payload_path
   
    
    def injection(self,payload:str):
        response = requests.get(self.target_url+payload)
        res_html = response.content.decode("utf-8") .splitlines(keepends=True)
        # for i in range(len(res_html)):
        #     print(res_html[i])
        return res_html


    @property
    def payloads(self):
        self.load_payloads()
        return self.__payloads

    
    
    def load_payloads(self)->list:
        assert(os.path.exists(self.payload_path))
        with open(self.payload_path,'r') as fd:
            # todo checking 
            payloads = fd.readlines()
        payloads = [payloads[i].rstrip('\n') for i in range(len(payloads))]
        self.__payloads = payloads
        return payloads


    def inturder(self)->list: 
        assert(len(self.payloads) > 0)
        res_list = []
        for i in range(len(self.payloads)):
            response = requests.get(target_url+self.payloads[i])
            res_html = response.content.decode("utf-8") .splitlines(keepends=True)
            res_list.append(res_html)
        self.__result = res_list
        return res_list

    def save_injected_html(self):
        if os.path.exists(self.save_path):
            raise ValueError(f"{self.save_path} already exists.")
        os.makedirs(self.save_path)
        for i in range(len(self.result)):
            with open(os.path.join(self.save_path,'res'+str(i)),'w+',encoding='utf-8') as writer:
                writer.writelines(self.result[i])

    def circuit(self):
        self.load_payloads()
        self.inturder()
        self.save_injected_html()

    @staticmethod
    def diff_string(old_str, new_str):
        """
        Compare two strings and highlight the differences using ANSI escape codes.
        """
        result = []
        if old_str != new_str:
            matcher = difflib.SequenceMatcher(None, old_str, new_str)
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'replace':
                    old_parts = re.findall(r'\S+|\s', old_str[i1:i2])
                    new_parts = re.findall(r'\S+|\s', new_str[j1:j2])
                    for i in range(max(len(old_parts), len(new_parts))):
                        if i >= len(old_parts):
                            result.append(f"\033[32m{new_parts[i]}\033[0m")  # Green for added parts
                        elif i >= len(new_parts):
                            result.append(f"\033[31m{old_parts[i]}\033[0m")  # Red for deleted parts
                        elif old_parts[i] != new_parts[i]:
                            result.append(f"\033[31m{old_parts[i]}\033[0m\033[32m{new_parts[i]}\033[0m")  # Red and green for changed parts
                        else:
                            result.append(new_parts[i])  # Unchanged parts
                elif tag == 'delete':
                    old_parts = re.findall(r'\S+|\s', old_str[i1:i2])
                    for i in range(len(old_parts)):
                        result.append(f"\033[31m{old_parts[i]}\033[0m")  # Red for deleted parts
                elif tag == 'insert':
                    new_parts = re.findall(r'\S+|\s', new_str[j1:j2])
                    for i in range(len(new_parts)):
                        result.append(f"\033[32m{new_parts[i]}\033[0m")  # Green for added parts
                else:
                    result.append(new_str[j1:j2])  # Unchanged parts
            return ''.join(result)
        else:
            return new_str



    def xsslab_template(self,payload):
        response = requests.get(self.target_url)
        res_html = response.content.decode("utf-8") .splitlines()
        if res_html[16] == '<input name=keyword  value="">':
            template = f'<input name=keyword value="{payload}">'
            return template
        elif res_html[16] == "<input name=keyword  value=''>":
            template = f"<input name=keyword value='{payload}'>"
            return template
        else:
            return 0
            
    

    def xsslab_compare(self):
        payloads = self.payloads
        for i in range(len(payloads)):
                res_html_list = self.injection(payloads[i])
                template=self.xsslab_template(payloads[i])
                assert(template != 0)
                new_str = res_html_list[16] 
                # print(template)
                # print(new_str,end='')
                print(self.diff_string(template, new_str),end='')


if __name__ == '__main__':
    target_url = "http://127.0.0.1:8000/level5.php?keyword="
    Intruder = XssIntruder()
    Intruder.url=target_url
    Intruder.xsslab_compare()
