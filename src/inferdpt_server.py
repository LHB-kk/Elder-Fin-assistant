from fate_llm.algo.inferdpt.inferdpt import InferDPTServer
from fate_llm.inference.api import APICompletionInference

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


ctx = create_ctx(arbiter)
inference_server = APICompletionInference(api_url="BASE_URL", model_name='model_name', api_key='EMPTY')
inferdpt_server = InferDPTServer(ctx, inference_server)

while True:
    inferdpt_server.inference()