import os


import sys, getopt

import sys

def hello(a):
    os.system("set FLASK_APP=server.py")
    os.system("flask run --port " + str(a))
    os.system("python run_app.py")
    print("RUNNING ON ", a)

if __name__ == "__main__":
    a = int(sys.argv[1])
    hello(a)



