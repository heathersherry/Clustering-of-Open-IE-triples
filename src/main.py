from Graph import Graph
import math
import csv
import os, sys, time
import json
import re
from pprint import pprint
from TripleSimilarity import TripleSimilarity
from Lemmatizer import Lemmatizer
import sys
sys.setrecursionlimit(3000)

theta = 0.5
beta = 3
limit = 100 #You can modify this value to work on different numbers of the triples

class SIST():

    def __init__(self, file_name, noun_info, wikipedia_patterns, nyt_patterns):
        self.file_name = file_name
        self.noun_info = noun_info
        '''Obtain triples'''
        self.data = [json.loads(line) for line in open(self.file_name)][:limit]
        '''Obtain side information (stored in noun_data)'''
        self.noun_data = [json.loads(line) for line in open(self.noun_info)]
        '''Obtain relation patterns'''
        (self.nyt_relation_index_dict, self.nyt_relation_content_dict) = self.obatinPATTYRelationPattern(wikipedia_patterns, nyt_patterns)
        '''Obtain required triple information stored in dict'''
        self.norm_subject_dict = self.StoreInforInDict(self.data, 'triple_norm', 0)
        self.norm_object_dict = self.StoreInforInDict(self.data, 'triple_norm', 2)

    def StoreInforInDict(self, data, info, position):
        target_dict = {}
        for i in range(0, len(data)):
            word = data[i][info][position]
            if word in target_dict.keys():
                count = target_dict[word]+1
                target_dict[word] = count
            else:
                target_dict.update({word:1})
        #print(target_dict)
        return target_dict

    def obatinPATTYRelationPattern(self,wikipedia_patterns, nyt_patterns):
        '''Obtain the synonymous patterns of relation phrases'''
        #(relation_wikipeida_index, relation_wikipedia_dict) = self.readPATTYRelation(wikipedia_patterns)
        (relation_nyt_index, relation_nyt_dict) = self.readPATTYRelation(nyt_patterns)
        return (relation_nyt_index, relation_nyt_dict)

        #return ({},{})

    def readPATTYRelation(self, filename):
        '''Read the synonymous patterns of relation phrases from files'''
        relation_index_dict = {}
        relation_content_dict = {}
        file = open(filename, "r")

        patterns = file.readlines()
        print('-' * 30 + 'Reading ' + filename + ' (' + str(len(patterns)) + ' in total)' + '-' * 30)
        for i in range(1, len(patterns)):
            line = patterns[i]
            line_content = line.split('\t')
            '''
            tags = re.findall(re.compile(r'\[\[(.*?)\]\]'), line_content[1])
            for tag in tags:
                if tag in different_pos_tag:
                    continue
                else:
                    different_pos_tag.append(tag)
            '''
            # if len(line_content[1].split('$')) > 2 and float(line_content[2]) >= 0.5:
            if len(line_content[1].split('$')) > 2:
                sys.stdout.write("\r" + (line_content[0]))
                sys.stdout.flush()
                synonymous_info = line_content[1].split('$')[:-1]

                synonymous_content = []
                for phrase in synonymous_info:
                    phrase_new = phrase.replace('[[pro]]', '[[prp]]')
                    synonymous_content.append(phrase_new[:phrase_new.find(';')])
                # print('#'*12)
                # print(synonymous_content)

                norm_synonymous_content = []
                for phrase in synonymous_content:
                    final_word = self.transferRalationPhraseToNormPattern(phrase)
                    norm_synonymous_content.append(final_word)
                # print(norm_synonymous_content)

                relation_content_dict.update({int(line_content[0]): norm_synonymous_content})
                for phrase in norm_synonymous_content:
                    if phrase not in relation_index_dict.keys():
                        index_list = []
                        index_list.append(int(line_content[0]))
                        relation_index_dict.update({phrase: index_list})
                    else:
                        index_list = relation_index_dict[phrase]
                        index_list.append(int(line_content[0]))
                        relation_index_dict[phrase] = index_list

        #pprint(relation_index_dict)
        #pprint(relation_content_dict)
        return (relation_index_dict, relation_content_dict)

    def transferRalationPhraseToNormPattern(self, phrase):
        word_list = phrase.split(' ')
        final_word_list = {}
        for count in range(0, len(word_list)):
            final_word_list.update({count: word_list[count]})
        # print(final_word_list)

        """Deal with the phrases where "[[...]]" have been deleted"""
        meaningful_phrase = ''
        for word in final_word_list.values():
            if word.find('[[') == -1 and word.find(']]') == -1:
                meaningful_phrase += word + ' '
        meaningful_phrase = meaningful_phrase[:-1]
        # print (meaningful_phrase)

        final_meaningful_phrase_list = Lemmatizer().lemmatizeSentence(meaningful_phrase)
        # print(final_meaningful_phrase_list)

        for count, word in final_word_list.items():
            if word.find('[[') == -1 and word.find(']]') == -1:
                continue
            else:
                final_meaningful_phrase_list.insert(count, word)
        # print(final_meaningful_phrase_list)
        final_word = ' '.join(final_meaningful_phrase_list)
        return final_word

    def canopy_noun_overlap(self, a, b):
        '''Check whether there is overlap of non-stopwords for two give words'''
        stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll",
                     "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's",
                     'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs',
                     'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am',
                     'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
                     'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
                     'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during',
                     'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
                     'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
                     'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
                     'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't",
                     'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't",
                     'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't",
                     'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn',
                     "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won',
                     "won't", 'wouldn', "wouldn't", 'I', 'Me', 'My', 'Myself', 'We', 'Our', 'Ours', 'Ourselves', 'You',
                     "You're", "You've", "You'll", "You'd", 'Your', 'Yours', 'Yourself', 'Yourselves', 'He', 'Him',
                     'His', 'Himself', 'She', "She's", 'Her', 'Hers', 'Herself', 'It', "It's", 'Its', 'Itself', 'They',
                     'Them', 'Their', 'Theirs', 'Themselves', 'What', 'Which', 'Who', 'Whom', 'This', 'That', "That'll",
                     'These', 'Those', 'Am', 'Is', 'Are', 'Was', 'Were', 'Be', 'Been', 'Being', 'Have', 'Has', 'Had',
                     'Having', 'Do', 'Does', 'Did', 'Doing', 'A', 'An', 'The', 'And', 'But', 'If', 'Or', 'Because',
                     'As', 'Until', 'While', 'Of', 'At', 'By', 'For', 'With', 'About', 'Against', 'Between', 'Into',
                     'Through', 'During', 'Before', 'After', 'Above', 'Below', 'To', 'From', 'Up', 'Down', 'In', 'Out',
                     'On', 'Off', 'Over', 'Under', 'Again', 'Further', 'Then', 'Once', 'Here', 'There', 'When', 'Where',
                     'Why', 'How', 'All', 'Any', 'Both', 'Each', 'Few', 'More', 'Most', 'Other', 'Some', 'Such', 'No',
                     'Nor', 'Not', 'Only', 'Own', 'Same', 'So', 'Than', 'Too', 'Very', 'S', 'T', 'Can', 'Will', 'Just',
                     'Don', "Don't", 'Should', "Should've", 'Now', 'D', 'Ll', 'M', 'O', 'Re', 'Ve', 'Y', 'Ain', 'Aren',
                     "Aren't", 'Couldn', "Couldn't", 'Didn', "Didn't", 'Doesn', "Doesn't", 'Hadn', "Hadn't", 'Hasn',
                     "Hasn't", 'Haven', "Haven't", 'Isn', "Isn't", 'Ma', 'Mightn', "Mightn't", 'Mustn', "Mustn't",
                     'Needn', "Needn't", 'Shan', "Shan't", 'Shouldn', "Shouldn't", 'Wasn', "Wasn't", 'Weren', "Weren't",
                     'Won', "Won't", 'Wouldn', "Wouldn't"]
        a_list = a.split()
        b_list = b.split()
        common_word_list = list(set(a_list) & set(b_list))
        if len(common_word_list) == 0:
            return False
        for word in common_word_list:
            if word in stopwords:
                continue
            else:
                #print(word)
                return True
        return False

    def sim(self, t1, t2, data, noun_data, beta):
        ([text_sim, idf_sim, relation_sim, entity_sim, type_sim, dm_sim], sist_sim) = TripleSimilarity(t1, t2, data, noun_data, self.nyt_relation_index_dict, self.nyt_relation_content_dict, self.norm_subject_dict,self.norm_object_dict,beta).totalSim()
        return ([text_sim, idf_sim, relation_sim, entity_sim, type_sim, dm_sim], sist_sim)

    def cluster(self):
        '''Clustering. The first step is to construct a triple graph and produce canopies. The second step is to process the canopies.'''
        data = self.data
        noun_data = self.noun_data
        final_result=[]

        # Add '_id' to each single record (The self-generated datasets do not has id)
        count = 0
        for single_data in data:
            # pprint(single_data)
            count += 1
            if '_id' in single_data.keys():
                continue
            else:
                single_data.update({'_id': count})

        # Add id to each single record (make it convenient to check the clustering results )
        id = 0
        for single_data in data:
            single_data.update({"id":id})
            id +=1


        print("****************Construct Triple Graph****************")
        # create a triple-dictionary recording the ids of the triples
        triple_dict = {}
        count = 0
        for single_data in data:
            if single_data['_id'] not in triple_dict.values():
                triple_dict.update({count: single_data['_id']})
                count += 1
        print(triple_dict)

        triple_graph = Graph(len(triple_dict))

        for i in range(0, len(data)):
            for j in range(i + 1, len(data)):
                if self.canopy_noun_overlap(data[i]["triple_norm"][0],data[j]["triple_norm"][0]) or \
                        self.canopy_noun_overlap(data[i]["triple_norm"][2], data[j]["triple_norm"][2]):
                    #print(data[i]["triple_norm"][0], data[j]["triple_norm"][0], data[i]["triple_norm"][2], data[j]["triple_norm"][2])
                    triple_graph.addEdge(data[i]["id"], data[j]["id"])

        print("****************Find the Canopies****************")
        # Use DFS to find connected components
        triple_cc = triple_graph.connectedComponents()
        print(triple_cc)

        print("****************Construct Canopy Graph****************")
        for canopy in triple_cc:
            if len(canopy) == 1:
                continue
            else:
                print("+++++++++++++++One Canopy+++++++++++++")
                print(canopy)
                # find the real ids and contents of the triples
                canopy_data_list = []
                for canopy_id in canopy:
                    canopy_data_list.append(data[canopy_id])
                #print(canopy_data_list)

                # create a canopy-dictionary recording the ids of the triples
                canopy_dict = {}
                count = 0
                for single_data in canopy_data_list:
                    canopy_dict.update({count: single_data['_id']})
                    count += 1
                #print(canopy_dict)

                # build the canopy_graph
                canopy_graph = Graph(len(canopy_dict))

                for i in range(0, len(canopy_data_list)):
                    for j in range(i + 1, len(canopy_data_list)):
                        sys.stdout.write("\r" + str(canopy_data_list[i]['_id'])+' , '+str(canopy_data_list[j]['_id']))
                        sys.stdout.flush()
                        ([text_sim, idf_sim, relation_sim, entity_sim, type_sim, dm_sim], sist_sim) = self.sim(canopy_data_list[i], canopy_data_list[j], data, noun_data, beta)
                        if sist_sim >=theta:
                            single_node_1 = -1
                            single_node_2 = -1
                            for key, value in canopy_dict.items():
                                if value == canopy_data_list[i]['_id']:
                                    single_node_1 = key
                                if value == canopy_data_list[j]['_id']:
                                    single_node_2 = key
                            if single_node_1 != -1 and single_node_2 != -1:
                                canopy_graph.addEdge(single_node_1, single_node_2)

                # Use DFS to find connected components
                canopy_cc = canopy_graph.connectedComponents()
                #print(canopy_cc)
                print('\n')

                # find the real ids of the triples

                for cluster in canopy_cc:
                    cluster_list = []
                    for node in cluster:
                        cluster_list.append(canopy_dict[node])
                    print(cluster_list)
                    final_result.append(cluster_list)
        print("****************Final Results****************")
        print(final_result)



if __name__ == '__main__':
    file_name = '../data/ReVerb/data_tmp_[1, 3, 9, 12, 14, 19, 21, 24]_3/reverb45K_test_noun_record.json'
    noun_info = '../data/ReVerb/domain_tmp/wiki_record.json'
    #file_name = '../data/NYTimes2018/data_tmp_[1, 3, 9, 12, 14, 19, 21, 24]_3/newyorktimes_openie_arts.json'
    #noun_info = '../data/NYTimes2018/domain_tmp/wiki_record_arts.json'
    wikipedia_patterns = '../data/Patty-dataset/wikipedia-patterns.txt'
    nyt_patterns = '../data/Patty-dataset/nyt-patterns.txt'
    sist = SIST(file_name, noun_info, wikipedia_patterns, nyt_patterns)
    sist.cluster()
