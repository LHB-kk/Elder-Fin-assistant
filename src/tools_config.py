tools = [
    {
        "type": "function",
        "function": {
            "name": "get_a_stock_info",
            "description": "获取中国A股单只股票行情数据['开票价', '收盘价', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']",
            "parameters": {
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "纯数字表示的股票代码（六位）"
                    },
                    "period" : {
                        "type": "string",
                        "description": "获取周期，范围为{'daily', 'weekly', 'monthly'}"
                    },
                    "start_date" : {
                        "type": "string",
                        "description": "开始查询的日期，格式为'YYYYmmdd'"
                    },
                    "end_date" : {
                        "type": "string",
                        "description": "结束查询的日期，格式为'YYYYmmdd'"
                    },
                    "adjust" : {
                        "type": "string",
                        "description": "是否复权，qfq: 返回前复权后的数据; hfq: 返回后复权后的数据"
                    }
                },
                "required": ["stock_code", "period", "start_date", "end_date", "adjust"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_a_stock_code",
            "description": "获取中国A股单只股票代码",
            "parameters": {
                "type": "object",
                "properties": {
                    "stock_name": {
                        "type": "string",
                        "description": "股票名称"
                    }
                },
                "required": ["stock_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_hk_stock_info",
            "description": "获取港股单只股票行情数据['开盘价', '收盘价', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']",
            "parameters": {
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "纯数字表示的股票代码（五位）"
                    },
                    "period" : {
                        "type": "string",
                        "description": "获取周期，范围为{'daily', 'weekly', 'monthly'}"
                    },
                    "start_date" : {
                        "type": "string",
                        "description": "开始查询的日期，格式为'YYYYmmdd'"
                    },
                    "end_date" : {
                        "type": "string",
                        "description": "结束查询的日期，格式为'YYYYmmdd'"
                    },
                    "adjust" : {
                        "type": "string",
                        "description": "是否复权，qfq: 返回前复权后的数据; hfq: 返回后复权后的数据"
                    }
                },
                "required": ["stock_code", "period", "start_date", "end_date", "adjust"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_hk_stock_code",
            "description": "获取港股单只股票代码",
            "parameters": {
                "type": "object",
                "properties": {
                    "stock_name": {
                        "type": "string",
                        "description": "股票名称"
                    }
                },
                "required": ["stock_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fund_realTime_info",
            "description": "获取指定名称基金的实时信息['基金代码', '基金简称','当前单位净值', '当前累计净值', '上一日单位净值', '上一日累计净值', '日增长值' ,'日增长率', '申购状态', '赎回状态', '手续费']",
            "parameters": {
                "type": "object",
                "properties": {
                    "fund_name": {
                        "type": "string",
                        "description": "基金名称"
                    },
                    "indicator": {
                        "type": "string",
                        "description": "基金名称"
                    }
                },
                "required": ["fund_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fund_NAV",
            "description": "获取指定名称基金的历史单位净值信息['净值日期', '单位净值', '日增长率']",
            "parameters": {
                "type": "object",
                "properties": {
                    "fund_name": {
                        "type": "string",
                        "description": "基金名称"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "开始查询的日期，格式为'YYYY-mm-dd'"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "结束查询的日期，格式为'YYYY-mm-dd'"
                    }
                },
                "required": ["fund_name", "start_date", "end_date"]
            }
        }
    }

]