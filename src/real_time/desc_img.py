import json
from openai import OpenAI
import logging
client = OpenAI(
    api_key="EMPTY",
    base_url="BASE_URL",
)
def generate_desc(item, img_url):
    try:
        completion = client.chat.completions.create(
                    model="model_name",
                    messages=[  
                                {"role" : "system", "content" : f"""
                                            图片是由社交媒体中关键词："{item}"下关联的推文、评论统计成的情绪图谱。请对该情绪图谱中的指标进行总结阐述。"""},
                                {
                                    "role": "user","content": [
                                        {"type": "text","text": """
                                            阐述图片中的内容。
                                        """},
                                        {"type": "image_url",
                                        "image_url": {"url": f"{img_url}"}}
                                    ]
                                }
                            ],
                    temperature=0.1,
                    presence_penalty=-1,
                    max_tokens=256,
                    )
        completion_json = json.loads(completion.model_dump_json())
        img_content = completion_json['choices'][0]['message']['content']
        return img_content
    except Exception as e:
        logging.info(f"获取情绪图谱分析出错：{str(e)}")
        return None