import json
import requests
from typing import List, Dict

from src.log import logger
from inferdpt_client import get_inferdpt_client_result


from src.get_data import GetData
from src.prompt import QUERY_REWRITE_PROMPT_TEMPLATE, \
                        SPLIT_TASK_PROMPT_TEMPLATE



def query_rewrite(user_input: str, user_messages: List[Dict[str, str]]) -> str:

    history = user_messages[1:]
   
    history_info = ''
    for item in history:
        if item['role'] == 'user':
            history_info += f"用户: {item['content']}\n"
        else:
            history_info += f"ai金融数字人: {item['content']}\n"

    query_rewrite_prompt = QUERY_REWRITE_PROMPT_TEMPLATE.format(history_info, user_input)
    res = get_inferdpt_client_result(question=query_rewrite_prompt)
    return res


def split_task(text: str)-> List[Dict]:

    try:
        SPLIT_TASK_PROMPT = SPLIT_TASK_PROMPT_TEMPLATE.replace("{text}", text)
        task_list = get_inferdpt_client_result(prompt=SPLIT_TASK_PROMPT)
        task_list = json.loads(task_list)

    except Exception as e:
        logger.error(f"{e}")
        task_list = []

    return task_list

def answer_task(task_list: List[Dict[str, str]])-> str:
    answers = []
    for task in task_list:
        task_content = task['task_content']
        task_tpye = task['task_type']

        if task_tpye == 'social_media_comment':
            res = get_market_info(query=task_content)
            answers.append(res)
        elif task_tpye == 'knowledge_retrieval':
            
            try: 
                res = get_rag_response(query=task_content)
                answers.append(res)
            except Exception as e:
                logger.error(f"{e}")

        elif task_tpye == 'stock_history_data':
            ans = GetData(text=task_content)
            answers.append(ans)

        else:
            logger.info(f"task_tpye: {task_tpye}, task_content：{task_content}")

    answer_info = '\n'.join(answers)
    return answer_info

def get_market_info(query: str)-> str:
    try:
        context = ''
        res = requests.post(url='get_data_url', json={"item": query})
        res = res.json()
        all_back = res["all_back"]
        for item in all_back:
            context += item['abstract'] + '\n'
            if item['img_desc']:
                context += item['img_desc']
        return context
    
    except Exception as e:
        logger.error(f"{e}")
        return []

def get_rag_response(query: str, mode:str='local',  only_need_context: bool=False)-> str:
    data = {
        "query": query,
        "mode": mode,
        "only_need_context": only_need_context
    }
    res = requests.post(url='rag_server_path', json=data)
    res = res.json()
    if res['status'] == 'success':
        return res['data']
    else:
        return "Error"