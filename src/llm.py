import re
import time
from typing import List, Dict
from openai import OpenAI

from src.log import logger
from src.llm_utils import query_rewrite, split_task, answer_task
from src.prompt import FINAL_ANSWER_PROMPT_TEMPLATE

class MODEL_API:
    def __init__(self, api_key = None, base_url = "base_url"):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
    

    def infer_stream(self, user_input: str, user_messages: List[Dict], llm_queue, chunk_size:int = 10):
        logger.info(f"[LLM] User input: {user_input}")
        time_cost = []
        start_time = time.time()
        if len(user_messages) == 1:
            user_messages[0]['content'] = '你是一个ai金融数字人,负责回答用户提出的问题，回答时使用短句，确保语气情感丰富、友好，并且响应迅速以保持用户的参与感。'

        new_query_input = query_rewrite(user_input, user_messages)
        task_list = split_task(text=new_query_input)
        answer_info = answer_task(task_list=task_list)
        FINAL_ANSWER_PROMPT = FINAL_ANSWER_PROMPT_TEMPLATE.format(answer_info, new_query_input)

        user_messages.append({'role': 'user', 'content': FINAL_ANSWER_PROMPT})

        completion = self.client.chat.completions.create(
            model="qwen",
            messages=user_messages,
            stream=True
        )
        
        chat_response = ""
        buffer = ""
        sentence_buffer = ""
        sentence_split_pattern = re.compile(r'(?<=[,;.!?，；：。:！？》、”])')
        fp_flag = True
        for chunk in completion:
            chat_response_chunk = chunk.choices[0].delta.content
            chat_response += chat_response_chunk
            buffer += chat_response_chunk

            sentences = sentence_split_pattern.split(buffer)
            
            if not sentences:
                continue
            
            for i in range(len(sentences) - 1):
                sentence = sentences[i].strip()
                sentence_buffer += sentence

                if fp_flag or len(sentence_buffer) >= chunk_size:
                    llm_queue.put(sentence_buffer)
                    time_cost.append(round(time.time()-start_time, 2))
                    start_time = time.time()
                    sentence_buffer = ""
                    fp_flag = False
            
            buffer = sentences[-1].strip()

        sentence_buffer += buffer
        if sentence_buffer:
            llm_queue.put(sentence_buffer)

        llm_queue.put(None)
        
        user_messages.pop()   
        user_messages.append({'role': 'user', 'content': new_query_input})
        user_messages.append({'role': 'assistant', 'content': chat_response})
        
        if len(user_messages) > 10:
            user_messages.pop(0)
        
        return chat_response, user_messages, time_cost