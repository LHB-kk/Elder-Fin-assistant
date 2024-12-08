import json
from datetime import datetime
import pandas as pd
from src.tools_config import tools
import akshare as ak
from openai import OpenAI
import logging
logging.basicConfig(
    filename='finInfoGet.log',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s-%(levelname)s-%(message)s'
)
current_data = datetime.now().date()
current_data = current_data.strftime('%Y-%m-%d')

import os
current_file_path = os.path.abspath(__file__)
parent_dir = os.path.dirname(current_file_path)

class stockInfo:
    def __init__(self):
        self.res_a = ak.stock_zh_a_spot_em()
        self.res_hk = ak.stock_hk_spot_em()
    def get_a_stock_code(self, stock_name):
        stock_code = self.res_a[self.res_a['名称'] == stock_name].iloc[0,1] # 002371
        return stock_code
    def get_a_stock_info(self, stock_code, period, start_date, end_date, adjust):
        stock_info = ak.stock_zh_a_hist(symbol=stock_code, period=period, start_date=start_date, end_date=end_date, adjust=adjust)
        stock_info['日期'] = stock_info['日期'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else None)
        return stock_info
    def get_hk_stock_code(self, stock_name):
        stock_code = self.res_hk[self.res_hk['名称'] == stock_name].iloc[0,1]
        return stock_code
    def get_hk_stock_info(self, stock_code, period, start_date, end_date, adjust):
        stock_info = ak.stock_hk_hist(symbol=stock_code, period=period, start_date=start_date, end_date=end_date, adjust=adjust)
        stock_info['日期'] = stock_info['日期'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else None)
        return stock_info
class fundInfo:
    def __init__(self):
        data_path = os.path.join(parent_dir, "data/基金数据.xlsx")
        self.realTime_data = pd.read_excel(data_path)
    def fund_realTime_info(self, fund_name):
        realTime_fund_info = self.realTime_data[self.realTime_data['基金简称'].str.contains(fund_name,na=False)]
        return realTime_fund_info
    def fund_NAV(self, fund_name, start_date = '2024-01-01', end_date = current_data):
        code = self.realTime_data[self.realTime_data['基金简称'].str.contains(fund_name,na=False)].iloc[0,0]
        fund_name_em_df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        fund_name_em_df['净值日期'] = pd.to_datetime(fund_name_em_df['净值日期'], errors = 'coerce')
        fund_name_em_df = fund_name_em_df[fund_name_em_df['净值日期'] >= start_date]
        fund_name_em_df = fund_name_em_df[fund_name_em_df['净值日期'] <= end_date]
        return fund_name_em_df
class APIcommunication:
    def __init__(self):
        self.client = OpenAI(
            api_key="API_KEY",
            base_url="BASE_URL",
        )
        self.stock_info = stockInfo()
        self.fund_info = fundInfo()
    def send_messages(self,messages:list):
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools
        )
        message = response.choices[0].message
        messages.append(message)
        if message.tool_calls:
            messages = self.function_calling(messages, message)
            message = self.send_messages(messages)
        return message
    def function_calling(self,messages:list, message):
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                parameters = json.loads(tool_call.function.arguments)
                tool_response = None
                if tool_name == 'get_a_stock_info':
                    stock_code = parameters['stock_code']
                    period = parameters['period']
                    start_date = parameters['start_date']
                    end_date = parameters['end_date']
                    adjust= parameters['adjust']
                    df = self.stock_info.get_a_stock_info(stock_code=stock_code, period=period, start_date=start_date, end_date=end_date, adjust=adjust)
                    tool_response = df.to_json(orient="records",force_ascii=False)
                elif tool_name == 'get_hk_stock_info':
                    stock_code = parameters['stock_code']
                    period = parameters['period']
                    start_date = parameters['start_date']
                    end_date = parameters['end_date']
                    adjust= parameters['adjust']
                    df = self.stock_info.get_hk_stock_info(stock_code=stock_code, period=period, start_date=start_date, end_date=end_date, adjust=adjust)
                    tool_response = df.to_json(orient="records",force_ascii=False)
                elif tool_name == 'fund_realTime_info':
                    fund_name = parameters['fund_name']
                    df = self.fund_info.fund_realTime_info(fund_name=fund_name)
                    tool_response = df.to_json(orient="records",force_ascii=False)
                elif tool_name == 'fund_NAV':
                    fund_name = parameters['fund_name']
                    start_date = parameters['start_date']
                    end_date = parameters['end_date']
                    df = self.fund_info.fund_NAV(fund_name=fund_name, start_date=start_date, end_date=end_date)
                    tool_response = df.to_json(orient="records",force_ascii=False)
                elif tool_name == 'get_a_stock_code':
                    stock_name = parameters['stock_name']
                    tool_response = self.stock_info.get_a_stock_code(stock_name=stock_name)
                elif tool_name == 'get_hk_stock_code':
                    stock_name = parameters['stock_name']
                    tool_response = self.stock_info.get_hk_stock_code(stock_name=stock_name)
                if tool_response is not None:
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": tool_response})
            return messages
def GetData(text):
    LLM_calling = APIcommunication()
    messages = [
        {"role": "system", "content": f"今天日期是{current_data}，你是一个金融信息获取助手，用于为用户提供精准的金融信息服务。\n##**要求**\n对于所有日期的价格信息，均取该日期当天收盘价。"},
        {"role": "user", "content": f"工具调用: {text}"}
        ]
    message = LLM_calling.send_messages(messages)
    return message.content
