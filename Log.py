import datetime

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Timenow string
def Now():
    return datetime.datetime.now().strftime('%d-%m-%Y:%H-%M-%S')

# Time now string filename safe
def NowString():
    return datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S')


# method to perform a structued log
def Log(type,msg):
    # type checking for output and coloration
    if  (type == 1):
        typeStr = "LOG"
        typeCol = bcolors.OKBLUE
    elif(type == 2):
        typeStr = "ERROR"
        typeCol = bcolors.FAIL
    elif(type == 3):
        typeStr = "WARNING"
        typeCol = bcolors.WARNING
    elif(type == 4):
        typeStr = "SUCCESS"
        typeCol = bcolors.OKGREEN
    else :
        typeStr = "LOG"
        typeCol = bcolors.OKBLUE

    # printing lof to terminal
    print("[\033[92m %s \033[0m]  %s%-8s%s : %s" % (Now(),typeCol,typeStr,bcolors.ENDC,msg))
