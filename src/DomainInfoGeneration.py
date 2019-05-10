from math import *
from decimal import Decimal
import json,time
from os import listdir
from os.path import isfile, join
from pprint import pprint

class DomainInforgeneration:

    def getKeywords(self, input, output, keyword_folder):
        '''Obtain keywords from the record lists'''
        onlyfiles = [f for f in listdir(keyword_folder) if isfile(join(keyword_folder, f))]

        keyword_list = []
        for file in onlyfiles:
            with open(keyword_folder +'/' + file) as f:
                lines = f.read().splitlines()
                keyword_list.append(lines)

        '''a list which contains |D| sublists, while each sublist contains the keywords in the |D|th domain'''
        print(len(keyword_list))
        self.computeDomainCounter(input, output, keyword_list)


    def computeDomainCounter(self, input, output,keyword_list):
        '''Computer domain counter for each entity in the noun list'''
        file = input

        data = [json.loads(line) for line in open(file)]

        for i in range(0, len(data)):
            noun_detail = data[i]
            print(noun_detail)
            for noun, noun_info in noun_detail.items():
                for entity, entity_info in noun_info.items():
                    domain_counter = []
                    for j in range(0, len(keyword_list)):
                        if len(entity_info[2]):
                            count = self.searchKeywords(entity_info[2], keyword_list[j])
                            domain_counter.append(count)
                        else:
                            domain_counter.append(0)
                    print(domain_counter)
                    new_entity_info = entity_info
                    new_entity_info.append(domain_counter)
                    noun_info[entity] = new_entity_info
            print(noun_detail)
            record_file = open(output, 'a')
            record_file.write(json.dumps(noun_detail) + '\n')
            record_file.close()


    def searchKeywords(self,original_list,keyword_list):
        '''Search potential keywords for each type description'''
        sentence_list = []
        for description in original_list:
            sentence_list.extend(description.split(' '))
        count = 0
        for keyword in keyword_list:
            if keyword in sentence_list:
                count+=1
        return count

def main(file):
    domainGenerator = DomainInforgeneration()
    keyword_folder = '../data/Domain_keywords'
    input = '../data/NYTimes2018/'+file
    output = '../data/NYTimes2018/domain_tmp/'+file
    domainGenerator.getKeywords(input, output, keyword_folder)

if __name__ == '__main__':
    file_list = ['wiki_record_sports.json', 'wiki_record_arts.json', 'wiki_record_business.json', 'wiki_record_food.json', 'wiki_record_health.json', 'wiki_record_movies.json', 'wiki_record_politics.json', 'wiki_record_science.json']
    for file in file_list:
        main(file)