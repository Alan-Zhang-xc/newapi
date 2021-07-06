# -*- coding: utf-8 -*-
import random


def send_shortmsg(phone):
    code = ""
    for i in range(4):
        ran = random.randint(0, 9)
        code += str(ran)
    ret, code = {"status_code": 200}, code
    return ret, code
