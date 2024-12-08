from fate_llm.inference.api import APICompletionInference
from fate_llm.algo.inferdpt import inferdpt
from fate_llm.algo.inferdpt.utils import InferDPTKit
from src.dynamic_epsilon import perturb_sentence

arbiter = ("arbiter", 10000)
guest = ("guest", 10000)
host = ("host", 9999)
name = "fed1"


def create_ctx(local):
    from fate.arch import Context
    from fate.arch.computing.backends.standalone import CSession
    from fate.arch.federation.backends.standalone import StandaloneFederation
    import logging

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    computing = CSession(data_dir="./session_dir")
    return Context(computing=computing, federation=StandaloneFederation(computing, name, local, [guest, host, arbiter]))


ctx = create_ctx(guest)
save_kit_path = 'kit_path'

kit = InferDPTKit.load_from_path(save_kit_path)

inference = APICompletionInference(api_url="API_URL", model_name='model_name', api_key='EMPTY')


doc_template = """{{question}} 
"""

instruction_template="""
<|im_start|>system
你是一个很有帮助ai金融助手<|im_end|>
<|im_start|>user
{{perturbed_doc}}<|im_end|>
<|im_start|>assistant

"""

decode_template = """你是一个很有帮助的ai金融助手。
任务1：{{perturbed_doc}}
任务1回答:{{perturbed_response | replace('\n', '')}}

借鉴任务1回答，对任务进行作答:
任务2:{{question}} 
任务2回答:
"""

inferdpt_client = inferdpt.InferDPTClient(ctx, kit, inference, epsilon=3.0)

inferdpt_client.perturb_sentence = perturb_sentence

def get_inferdpt_client_result(question, temperature=0.7, max_tokens=512):
    test_example = {
        'question': question
    }
    result = inferdpt_client.inference([test_example], doc_template, instruction_template, decode_template, \
                                 remote_inference_kwargs={
                                    'stop': ['<|im_end|>', '<|end_of_text|>'],
                                    'temperature': temperature,
                                    'max_tokens': max_tokens
                                 },
                                 local_inference_kwargs={
                                    'stop': ['<|im_end|>', '\n\n', '<|end_of_text|>'],
                                    'temperature': temperature,
                                    'max_tokens': max_tokens  
                                 })
    return result[0]['inferdpt_result']