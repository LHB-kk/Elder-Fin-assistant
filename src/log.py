import logging

class MyLogging(logging.Logger):
    def __init__(self,name,level = logging.INFO,file = None):
        super().__init__(name,level)

        fmt = "%(asctime)s %(name)s %(levelname)s %(filename)s--%(lineno)dline :%(message)s"
        formatter = logging.Formatter(fmt)

        if file:
            handle2 = logging.FileHandler(file,encoding="utf-8")
            handle2.setFormatter(formatter)
            self.addHandler(handle2)
        else:
            handle1 = logging.StreamHandler()
            handle1.setFormatter(formatter)
            self.addHandler(handle1)

    
logger = MyLogging("mylog",file=r"./log.log")
