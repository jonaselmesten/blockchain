
import datetime as dt
from _thread import *


def five(a, b):
    print("FIVE")
    current_min = dt.datetime.now().second

    while True:
        new_min = dt.datetime.now().second
        if new_min % 5 == 0 and new_min != current_min:
            print("New second:", new_min)
            current_min = new_min

def three(a, b):
    print("THREE")
    current_min = dt.datetime.now().second

    while True:
        new_min = dt.datetime.now().second
        if new_min % 3 == 0 and new_min != current_min:
            print("New second:", new_min)
            current_min = new_min
try:
    start_new_thread(three, ("Thread-1", 2))
    start_new_thread(five, ("Thread-2", 4))
except:
    print("WRROR")

while 1:
    pass
