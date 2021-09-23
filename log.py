
import traceback
from datetime import datetime

LOG_FILE = ".logs"

def make_log(_str):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return f"=================================================\n" + \
    f"{now} {_str}\n" + \
    f"{traceback.format_exc()}"

def write(e):
    try:
        with open(LOG_FILE, 'a') as file:
            message = make_log(str(e))
            file.write(message)
            print(message) # temporary
    except Exception as E:
        print("ERROR DURING WRITING TO LOGFILE: " + str(E))
        print(traceback.format_exc())
