# -*- coding: UTF-8 -*-
from flask import Flask, request
from deepseek import partition_task
from weibo_info import get_content
import logging
file_handler = logging.FileHandler('logging.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler]
)
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.logger.handlers = [] 
app.logger.addHandler(file_handler) 
@app.route('/get_info', methods = ['POST'])
def get_info():
    try:
        text = request.json
        text = text.get('item')
    except Exception as e:
        logging.info(e)
    if text:
        try:
            keywords = partition_task(text)['关键词']
            if keywords:
                res = []
                for word in keywords:
                    res_realtime = {}
                    res_realtime['abstract'], res_realtime['img_url'], res_realtime['img_desc'] = get_content(word)
                    if res_realtime:
                        res.append(res_realtime)
                    else:
                        res.append(res_realtime)
                return {
                    "item" : f"{text}",
                    "keywords" : f"{keywords}",
                    "all_back" : res,
                    "message" : "Success"
                }, 200
            else:
                return {
                "item" : f"{text}",
                "keywords" : f"",
                "all_back" : res,
                "message" : f"实时信息关键词提取出错"
            }, 500
        except Exception as e:
            return {
                "item" : f"{text}",
                "keywords" : f"",
                "all_back" : res,
                "message" : f"{str(e)}"
            }, 500
if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0',port=8080)