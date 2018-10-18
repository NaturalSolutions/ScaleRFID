#!/usr/bin/env python3

import re
# import classGetch
# import Screen


def weigh():
    flag = True
    while flag:
        try:
            weight = input()
        except EOFError:
            pass
        if weight:
            flag = False
            weightInt = int(re.findall(r"\d+", str(weight)[0]))
            weightString = str(weightInt)
            if len(weightString) >= 0:
                return weightString


def control(weight, data):
    if weight < data.Weight_Min_Imp:
        return "ImpMin"
    elif weight > data.Weigh_tMax_Imp:
        return "ImpMax"
    elif weight < data.Weight_Min_Path and weight > data.Weigh_tMin_Imp:
        return "PathMin"
    elif weight > data.Weight_Max_Path and weight < data.Weight_Max_Imp:
        return "PathMax"
    else:
        return "Normal"


# def validate(result):
#     if result == "Normal":
#         Screen.
