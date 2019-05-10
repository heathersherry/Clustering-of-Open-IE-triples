from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from Graph import Graph
import math
import csv
import os, sys, time
import json
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet as wn
import re
from pprint import pprint
from TripleSimilarity import TripleSimilarity
from Lemmatizer import Lemmatizer

theta = 0.5
beta = 3
limit = 1000

class MyLinearRegression():
    def __init__(self, file_name, noun_info, wikipedia_patterns, nyt_patterns):
        self.file_name = file_name
        self.noun_info = noun_info
        self.data = [json.loads(line) for line in open(self.file_name)][:limit]
        self.noun_data = [json.loads(line) for line in open(self.noun_info)]
        (self.nyt_relation_index_dict, self.nyt_relation_content_dict) = self.obatinPATTYRelationPattern(wikipedia_patterns, nyt_patterns)
        self.postag_dict = {'JJ':'adj', 'JJR':'adj', 'JJS':'adj','CC':'con', 'DT':'det', 'CD':'num', 'PRP':'prp', 'PRP$':'prp', 'WP':'prp', 'WP$': 'prp', 'MD': 'mod'}
        self.norm_subject_dict = self.StoreInforInDict(self.data, 'triple_norm', 0)
        self.norm_object_dict = self.StoreInforInDict(self.data, 'triple_norm', 2)

    def StoreInforInDict(self, data, info, position):
        target_dict = {}
        for i in range(0, len(data)):
            word = data[i][info][position]
            if word in target_dict.keys():
                count = target_dict[word] + 1
                target_dict[word] = count
            else:
                target_dict.update({word: 1})
        print(target_dict)
        return target_dict

    def obatinPATTYRelationPattern(self, wikipedia_patterns, nyt_patterns):
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
            #if len(line_content[1].split('$')) > 2 and float(line_content[2]) >= 0.5:
            if len(line_content[1].split('$')) > 2:
                sys.stdout.write("\r" + (line_content[0]))
                sys.stdout.flush()
                synonymous_info = line_content[1].split('$')[:-1]

                synonymous_content = []
                for phrase in synonymous_info:
                    phrase_new = phrase.replace('[[pro]]', '[[prp]]')
                    synonymous_content.append(phrase_new[:phrase_new.find(';')])
                #print('#'*12)
                #print(synonymous_content)

                norm_synonymous_content = []
                for phrase in synonymous_content:
                    final_word = self.transferRalationPhraseToNormPattern(phrase)
                    norm_synonymous_content.append(final_word)
                #print(norm_synonymous_content)

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
                        

        pprint(relation_index_dict)
        pprint(relation_content_dict)
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
                return True
        return False

    def sim(self, t1, t2, data, noun_data, beta):
        ([text_sim, idf_sim, relation_sim, entity_sim, type_sim, dm_sim], sist_sim) = TripleSimilarity(t1, t2, data, noun_data, self.nyt_relation_index_dict, self.nyt_relation_content_dict, self.norm_subject_dict,self.norm_object_dict,beta).totalSim()
        return ([text_sim, idf_sim, relation_sim, entity_sim, type_sim, dm_sim], sist_sim)

    def generateTrainingData(self):
        data = self.data
        noun_data = self.noun_data
        X = []
        Y = {}
        result_dict = {}

        subject_record_dict = {}

        for i in range(0, len(data)):
            print data[i]
            for j in range(i + 1, len(data)):
                (sim_list, sim) = self.sim(data[i], data[j], data, noun_data, beta)
                X.append(sim_list)
                score = self.generateY(data[i], data[j])
                Y.update({str(data[i]['_id']) + '-' + str(data[j]['_id']): score})
                if score==1:
                    result_dict.update({data[i]['_id']:data[j]['_id']})
        print(result_dict)
        print(X)
        print(Y)
        return (X,Y.values())

    def generateTrainingDataUsingGraph(self):
        data = self.data
        noun_data = self.noun_data

        # Add id to each single record (make it convenient to check the clustering results )
        id = 0
        for single_data in data:
            single_data.update({"id": id})
            id += 1

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
        total_count = 0
        for i in range(0, len(data)):
            for j in range(i + 1, len(data)):
                if data[i]['true_link']['object'] == data[j]['true_link']['object'] and data[i]['true_link']['subject'] == data[j]['true_link']['subject']and self.relationSim(data[i], data[j]):
                    total_count +=1
                    ([text_sim, idf_sim, relation_sim, entity_sim, type_sim, dm_sim], sist_sim) = self.sim(data[i], data[j], data, noun_data, beta)
                    print(idf_sim)
                    triple_graph.addEdge(data[i]["id"], data[j]["id"])
        print("****************Find the Clusters****************")
        # Use DFS to find connected components
        triple_cc = triple_graph.connectedComponents()
        print(triple_cc)
        print(total_count)




    def generateY(self, t1, t2):
        if t1['true_link']['object'] == t2['true_link']['object'] and t1['true_link']['subject'] == t2['true_link']['subject'] and self.relationSim(t1, t2):
            return 1
        else:
            return 0

    def relationSim(self, t1, t2):
        t1_relation_synset = self.getRelationSynset(t1)
        t2_relation_synset = self.getRelationSynset(t2)
        score = self.overlap(t1_relation_synset, t2_relation_synset)
        return score

    def getRelationSynset(self, t):
        relation = t['triple'][1]  # We use the original format for comparison here.
        #print('*****'+relation)

        '''Process the phrase to get the universal pos tag patterns'''
        '''Note that we need to take the subject and object into consideration to judge the pos tags of the phrases'''
        target_phrase_pattern = Lemmatizer().lemmatizeRelationInSenetnce(relation, t['triple'])
        #print(target_phrase_pattern)

        t_relation_synset = []
        if target_phrase_pattern in self.nyt_relation_index_dict.keys():
            syn_id = self.nyt_relation_index_dict[target_phrase_pattern]
            for id in syn_id:
                t_relation_synset.extend(self.nyt_relation_content_dict[id])
        else:
            t_relation_synset.append(target_phrase_pattern)
        #print(t_relation_synset)
        return t_relation_synset

    def overlap(self, type1, type2):
        """Overlap Coefficient between lists"""
        set1 = set(type1)
        set2 = set(type2)

        union = set1 | set2
        intersection = set1 & set2
        if len(intersection) > 0:
            print('%%%%%%')
            print(type1)
            print(type2)
            print(union)
            return 1
        else:
            return 0



if __name__ == '__main__':

    #file_name = '../data/ReVerb/data_tmp_[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]_4/test.json'
    file_name = '../data/ReVerb/data_tmp_[1, 3, 9, 12, 14, 19, 21, 24]_3/reverb45K_noun_record.json'
    noun_info = '../data/ReVerb/domain_tmp/wiki_record.json'
    wikipedia_patterns = '../data/Patty-dataset/wikipedia-patterns.txt'
    nyt_patterns = '../data/Patty-dataset/nyt-patterns.txt'

    lr = MyLinearRegression(file_name, noun_info, wikipedia_patterns, nyt_patterns)
    (X,y) = lr.generateTrainingData()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    regressor = LinearRegression()
    regressor.fit(X_train, y_train)

    print(regressor.coef_)

