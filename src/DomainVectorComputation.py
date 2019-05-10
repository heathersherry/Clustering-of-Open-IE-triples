import os, sys, time
import json
import re
from pprint import pprint

class DomainVectorComputatation():
    def __init__(self, file_name, noun_info, target_directory, record_file, domain_list, beta):
        self.file_name = file_name
        self.noun_info = noun_info
        self.domain_list = domain_list
        self.beta = beta
        self.target_directory = target_directory
        self.record_file = record_file

    def process(self):
        if not os.path.exists(self.target_directory):
            os.makedirs(self.target_directory)


        data = [json.loads(line) for line in open(self.file_name)]
        count = 0
        for triple in data:
            count+=1
            print(count)
            triple_nouns = triple['nouns']
            triple_detail = self.getNounInfo(triple_nouns)
            vector = self.calculateDomainVector(triple_detail)
            #print(sum(vector))
            triple.update({'domain_vector':vector})
            record_file = open(self.target_directory+'/'+self.record_file, 'a')
            json.dump(triple, record_file)
            record_file.write('\n')
            record_file.close()

    def calculateDomainVector(self, sourceinfo_dict):
        """Calcualte the domain vector for the source text of one triple"""
        #print(self.domain_list)
        D = len(self.domain_list)
        v = []

        A_record_dict = {}
        for noun, entity_type in sourceinfo_dict.items():
            #print noun
            noun_A_record_dict = {}
            for entity, type_prob_descrip in entity_type.items():
                A = []
                A_full = type_prob_descrip[3]
                for count in range(0, len(self.domain_list)):
                    if A_full[self.domain_list[count] - 1]>self.beta:
                        A.append(self.beta)
                    else:
                        A.append(A_full[self.domain_list[count] - 1])
                #print A
                noun_A_record_dict.update({entity:A})
            A_record_dict.update({noun:noun_A_record_dict})
        #print(A_record_dict)

        for k in range(0, D):
            #print '-------------------------------------'+str(k)

            hashmap = {}
            hashmap.update({(0, 0): 1})
            for noun, entity_type in sourceinfo_dict.items():
                #print '*'*40
                #print noun
                newmap = {}
                for key in hashmap.keys():
                    #print '~'*40
                    sum_ = key[0]
                    norm = key[1]
                    old_value = hashmap[key]
                    for entity, type_prob_descrip in entity_type.items():
                        A = A_record_dict[noun][entity]
                        p = type_prob_descrip[0]
                        temp = (sum_ + A[k], norm + sum(A))
                        if temp not in newmap.keys():
                            newmap.update({temp: 0})
                        newmap[temp] += old_value * p
                hashmap = newmap
            v_temp = 0
            for key_final in hashmap.keys():
                if key_final[1] > 0:
                    v_temp += float(key_final[0])/key_final[1] * hashmap[key_final]
            v.append(v_temp)
        print(v)
        return v

    def getNounInfo(self, noun_list):
        """Get detailed info of the nouns of a triple"""
        noun_data = [json.loads(line) for line in open(self.noun_info)]
        t_detail = {}
        for noun in noun_list:
            for noun_detail in noun_data:
                if noun_detail.keys()[0] == noun[1]:
                    t_detail.update({noun[1]: noun_detail.values()[0]})

        """Obtain the probability of each linking"""
        for noun in t_detail:
            sum = 0
            for entity, entity_detail in t_detail[noun].items():
                sum+= entity_detail[0]
            for entity, entity_detail in t_detail[noun].items():
                if sum == 0:
                    entity_detail[0] = 0.0
                else:
                    entity_detail[0] = entity_detail[0]/float(sum)
        print(t_detail)
        return t_detail



if __name__ == '__main__':
    domain_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
    #domain_list = [1, 3, 9, 12, 14, 19, 21,24]  # The domain we choose: arts, business, entertainment, food, health, politics, science, sports

    '''
    file_name = '../data/ReVerb/test.json'
    noun_info = '../data/ReVerb/domain_tmp/noun_test.json'
    beta = 4
    target_directory = '../data/ReVerb/data_tmp_' + str(domain_list) + '_' + str(beta)
    record_file = 'test.json'
    '''
    file_name = '../data/NYTimes2018/newyorktimes_openie_arts.json'
    noun_info = '../data/NYTimes2018/domain_tmp/wiki_record_arts.json'
    beta = 4
    target_directory = '../data/NYTimes2018/data_tmp_' + str(domain_list) + '_' + str(beta)
    record_file = 'newyorktimes_openie_arts.json'

    vector_processor = DomainVectorComputatation(file_name, noun_info, target_directory, record_file, domain_list, beta)
    vector_processor.process()
