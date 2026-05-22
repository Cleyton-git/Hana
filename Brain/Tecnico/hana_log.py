import logging

logger = logging.getLogger("Hana")
logger.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.WARNING)

file = logging.FileHandler("hana_debug.log", encoding="utf-8")
file.setLevel(logging.INFO)

logger.addHandler(console)
logger.addHandler(file)

def Hana_log(msg):
    logger.info(msg)
    
def Hana_console(msg):
    logger.warning(msg)
