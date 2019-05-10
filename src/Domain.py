from math import *
from decimal import Decimal
import json,time
from os import listdir
from os.path import isfile, join

class Domain():
    def search_for_keywords(self,original,keyword_list):
        sentence_list = original.split(' ')
        count = 0
        for keyword in keyword_list:
            if keyword in sentence_list:
                count+=1
        return count