# -*- coding: UTF-8 -*-
from openai import OpenAI
import json
import logging
ds_client = OpenAI(api_key="EMPTY", base_url="BASE_URL")
def partition_task(text):
    try:
        response = ds_client.chat.completions.create(
                    model="chat-model",
                    messages=[
                        {"role": "system", "content": """
                            你是一个对用户输入问题进行预处理的助手，我将提供给你一段用户输入的内容，需要你提取问题中与金融知识或金融产品相关的关键词。
                            要求用json格式输出，输出格式样例为：{"关键词" : []}
                            """
                        },
                        {
                            "role" : "user", "content" : f"今天A股行情怎么样？"
                        },
                        {
                            "role" : "assistant", "content" : """{"关键词" : ["A股"]}"""
                        },
                        {
                            "role" : "user", "content" : f"{text}"
                        }
                    ],
                    stream=False,
                    temperature=1
                )
        ana_result = json.loads(response.choices[0].message.content)
        return ana_result
    except Exception as e:
        logging.info(f"{str(e)}")
        return None