# -*- coding: UTF-8 -*-
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import requests
import re
import time
import json
import base64
from pic_to_url import gene_url
from desc_img import generate_desc
from concurrent.futures import ThreadPoolExecutor
def weibo_api(text):
    header = {
    "authority": "com",
    "method": "GET",
    "path": "/api/llm",
    "scheme": "scheme",
    "accept-language": "zh-CN,zh;q=0.8",
    "referer": "url",
    "user-agent": "",
    "cookie": "cookie",
    "accept-encoding": "gzip"
    }
    url = f'url'
    try:
        response = requests.get(url=url, headers=header, verify=False)
        response_content = response.content.decode('utf-8')
        response_content_json = json.loads(response_content)
        result = response_content_json['msg']
        return result
    except Exception as e:
        logging.info(f"{str(e)}")
        return ""
class website_B:
    def __init__(self):
        pass
    def create_driver(self, text):
        encoded_text = urllib.parse.quote(text)
        url = 'query=' + encoded_text
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        option.add_argument('--no-sandbox')  
        option.add_argument('--disable-gpu')  
        option.add_argument('--disable-dev-shm-usage')  
        mobile_emulation = {
            "deviceName": "iPhone X"
        }
        option.add_experimental_option("mobileEmulation", mobile_emulation)
        driver = webdriver.Chrome(service=Service(), options=option)
        driver.get(url)
        return driver
    def get_emotion(self,text):
        driver = self.create_driver(text)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "/html/body/div/div"))
            )
            canvas = driver.find_element(By.XPATH, "//*[starts-with(@id,'starsDom')]")  
            canvas_base64 = driver.execute_script("""
                var canvas = arguments[0].querySelector('canvas');
                return canvas.toDataURL('image/png').substring(22);
                """, canvas)
            with open(f"./pic/{text}.png", "wb") as file:
                file.write(base64.b64decode(canvas_base64))
            img_url = gene_url(f'{text}.png')
        except Exception as e:
            img_url = "未能生成情绪图谱。"
        try:
            if img_url:
                img_desc = generate_desc(text, img_url)
            else:
                img_url = "未能生成情绪图谱。"
                img_desc = "词条相关推文数过少，获取不到情绪分析。"
        except Exception as e:
            img_desc = "分析舆论情绪出错。"
        return img_url, img_desc
    def get_abstract(self, text):
        driver = self.create_driver(text)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "/html/body/div/div"))
            )
            content = driver.page_source
            matches = re.findall(r'<div data-v-2f46cf83="">(.*?)</div>', content)
            if matches:
                try:
                    abstract = matches[1]
                    # details = matches[2]
                except Exception as e:
                    logging(str(e))
            else:
                abstract = ""
            return abstract
        except Exception as e:
            logging.info(f"{str(e)}")
            return None
    def run_concurrent_tasks(self, text):
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_emotion = executor.submit(self.get_emotion, text)
            future_abstract = executor.submit(self.get_abstract, text)
            img_url, img_desc = future_emotion.result()
            abstract_result = future_abstract.result()
            return abstract_result, img_url, img_desc
def get_content(text):
    emotion = website_B()
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_A = executor.submit(weibo_api,text)
        future_B = executor.submit(emotion.run_concurrent_tasks, text)
        abstract_result = future_A.result()
        sub_abstract_result, img_url, img_desc = future_B.result()
    if not abstract_result:
        res_abstract = sub_abstract_result
    else:
        res_abstract = abstract_result
    res_abstract = res_abstract.replace('<br>', '')
    return res_abstract, img_url, img_desc