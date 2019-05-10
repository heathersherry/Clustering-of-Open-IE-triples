from pyjarowinkler import distance
import json,math, nltk
from nltk.corpus import brown
from pprint import pprint
from Lemmatizer import Lemmatizer

class TripleSimilarity:
    def __init__(self, triple_1, triple_2, data, noun_data, relation_nyt_index, relation_nyt_dict, norm_subject_dict, norm_object_dict, beta):
        self.t1 = triple_1
        self.t2 = triple_2
        self.data = data
        self.noun_data = noun_data

        self.relation_nyt_index = relation_nyt_index
        self.relation_nyt_dict = relation_nyt_dict

        self.norm_subject_dict = norm_subject_dict
        self.norm_object_dict = norm_object_dict

        self.beta = beta
        self.domain_num = 25

        self.patty_postag_list = ['adj', 'con', 'det', 'num', 'prp', 'pro','mod'] # prp: personal pronoun; pro: pronoun, "he, their, her, my, I";  mod:modal verb, "will, can, may, should"
        self.nltk_postag_list = ['ADJ', 'CONJ', 'DET', 'NUM', 'PRON', 'PRON']
        #self.postag_dict = {'JJ':'adj', 'JJR':'adj', 'JJS':'adj', 'RB':'adj', 'RBR':'adj', 'RBS':'adj','CC':'con', 'DT':'det', 'CD':'num', 'PRP':'prp', 'PRP$':'prp', 'WP':'prp', 'WP$': 'prp', 'MD': 'mod'}
        self.postag_dict = {'JJ':'adj', 'JJR':'adj', 'JJS':'adj','CC':'con', 'DT':'det', 'CD':'num', 'PRP':'prp', 'PRP$':'prp', 'WP':'prp', 'WP$': 'prp', 'MD': 'mod'}


    def totalSim(self):

        '''noun phrases'''
        t1_subject = self.t1['triple_norm'][0]
        t2_subject = self.t2['triple_norm'][0]
        t1_object = self.t1['triple_norm'][2]
        t2_object = self.t2['triple_norm'][2]

        #print('********noun sim**********')
        text_sim = self.textSim(t1_subject, t2_subject, t1_object, t2_object)
        #print(text_sim)
        idf_sim = self.IDFScore(t1_subject, t2_subject, t1_object, t2_object)
        #print(idf_sim)

        '''relation phrases'''
        #print('********relation sim**********')
        relation_sim = self.relationSim()
        #print(relation_sim)

        ''' source text '''
        t1_nouns = self.t1['nouns']
        t2_nouns = self.t2['nouns']
        t1_detail = self.getNounInfo(t1_nouns)
        t2_detail = self.getNounInfo(t2_nouns)

        #print('********entity sim**********')
        entity_sim = self.entitySim(t1_detail, t2_detail)
        #print(entity_sim)

        #print('********type sim**********')
        type_sim = self.typeSim(t1_detail, t2_detail)
        #print(type_sim)

        #print('********domain sim**********')
        dm_sim = self.domainSim(self.t1['domain_vector'], self.t2['domain_vector'])
        #print(dm_sim)

        if dm_sim == -1:
            sim =  (text_sim + idf_sim + relation_sim + entity_sim + type_sim) / 5
        else:
            sim = (text_sim+idf_sim+relation_sim+entity_sim+type_sim+dm_sim)/6

        return([text_sim,idf_sim,relation_sim,entity_sim,type_sim,dm_sim],sim)



    def stringSimilarity(self, np1, np2):
        """ Text similarity """
        return distance.get_jaro_distance(np1, np2, winkler='True', scaling=0.1)

    def textSim(self, t1_subject, t2_subject, t1_object, t2_object):
        stringSim_sub = self.stringSimilarity(t1_subject, t2_subject)
        stringSim_obj = self.stringSimilarity(t1_object, t2_object)
        return (stringSim_sub + stringSim_obj) / 2

    def IDFScore(self, t1_subject, t2_subject, t1_object, t2_object):
        """ IDF token overlap """
        idf1 = self.IDFTokenOverlap(t1_subject, t2_subject, self.data)
        idf2 = self.IDFTokenOverlap(t1_object, t2_object, self.data)
        return(idf1 + idf2) / 2

    def IDFTokenOverlap(self, w1, w2, data):
        w1_list = set(w1.split(' '))
        w2_list = set(w2.split(' '))
        nltk_stopwords = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll",
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
                     'Won', "Won't", 'Wouldn', "Wouldn't"])
        # print(nltk_stopwords)
        w1_final = w1_list - nltk_stopwords
        w2_final = w2_list - nltk_stopwords
        # print(w1_final)
        # print(w2_final)

        union = w1_final | w2_final
        intersection = w1_final & w2_final
        # print(union)
        # print(intersection)
        if len(intersection) == 0:
            return 0

        upper = 0
        lower = 0
        for w in union:
            # print('------')
            # print(w)
            w_frequency = 0
            '''
            for i in range(0, len(data)):
                if w in data[i]['triple_norm'][0].split(' '):
                    w_frequency += 1
                if w in data[i]['triple_norm'][2].split(' '):
                    w_frequency += 1
            '''
            for word in self.norm_subject_dict.keys():
                if w in word.split(' '):
                    w_frequency += self.norm_subject_dict[word]
            for word in self.norm_object_dict.keys():
                if w in word.split(' '):
                    w_frequency += self.norm_object_dict[word]
            # print(w_frequency)
            df_w = math.pow(math.log(1 + w_frequency), -1)
            # print(df_w)
            if w in intersection:
                upper += df_w
            lower += df_w
        # print(upper)
        # print(lower)
        return float(upper / lower)

    def relationSim(self):
        t1_relation_synset = self.getRelationSynset(self.t1)
        t2_relation_synset = self.getRelationSynset(self.t2)
        score = self.overlapCoefficient(t1_relation_synset, t2_relation_synset)
        return score

    '''def getRelationSynset(self, t):
        relation = t['triple_norm'][1]   #Since PATTY uses the original format of the datatset, we use the original format for comparison here.
        #print(relation)
        tokens = nltk.word_tokenize(relation)
        #print(nltk.pos_tag(tokens, tagset='universal'))

        #Process the phrase to get the universal pos tag patterns
        target_phrase_pattern = ''
        for world_tuple in nltk.pos_tag(tokens):
            if world_tuple[1] in self.postag_dict.keys():
                target_phrase_pattern += '[['+self.postag_dict[world_tuple[1]]+']] '
            else:
                target_phrase_pattern += world_tuple[0]+' '
        print(target_phrase_pattern)

        t_relation_synset = []
        if target_phrase_pattern in self.relation_nyt_index.keys():
            syn_id = self.relation_nyt_index[target_phrase_pattern]
            t_relation_synset = self.relation_nyt_dict[syn_id]
        else:
            t_relation_synset.append(target_phrase_pattern)
        print t_relation_synset
        return t_relation_synset
    '''

    def getRelationSynset(self, t):
        relation = t['triple'][1]  # We use the original format for comparison here.
        #print('*****'+relation)

        '''Process the phrase to get the universal pos tag patterns'''
        '''Note that we need to take the subject and object into consideration to judge the pos tags of the phrases'''
        target_phrase_pattern = Lemmatizer().lemmatizeRelationInSenetnce(relation, t['triple'])
        #print(target_phrase_pattern)

        t_relation_synset = []
        if target_phrase_pattern in self.relation_nyt_index.keys():
            syn_id = self.relation_nyt_index[target_phrase_pattern]
            for id in syn_id:
                t_relation_synset.extend(self.relation_nyt_dict[id])
        else:
            t_relation_synset.append(target_phrase_pattern)
        #print(t_relation_synset)
        return t_relation_synset

    def getNounInfo(self, noun_list):
        """Get detailed info of the nouns of a triple"""
        t_detail = {}
        for noun in noun_list:
            for noun_detail in self.noun_data:
                if noun_detail.keys()[0] == noun[1]:
                    t_detail.update({noun[1]: noun_detail.values()[0]})

        """Obtain the probability of each linking"""
        for noun in t_detail:
            sum = 0
            for entity, entity_detail in t_detail[noun].items():
                sum+= entity_detail[0]
            if sum!= 0:
                for entity, entity_detail in t_detail[noun].items():
                    entity_detail[0] = entity_detail[0]/float(sum)
        #print(t_detail)
        return t_detail

    def entitySim(self, dict1, dict2):
        """Entity similarity"""

        t1_entity_dict = {}
        for noun, noun_detail in dict1.items():
            for entity, entity_detail in noun_detail.items():
                t1_entity_dict.update({entity: entity_detail[0]})
        #print(t1_entity_dict)

        t2_entity_dict = {}
        for noun, noun_detail in dict2.items():
            for entity, entity_detail in noun_detail.items():
                t2_entity_dict.update({entity: entity_detail[0]})
        #print(t2_entity_dict)


        return(self.overlapCoefficientWithProbability(t1_entity_dict, t2_entity_dict))

    def overlapCoefficientWithProbability(self, type1, type2):
        """Overlap Coefficient between dicts, with probability"""

        list1 = type1.keys()
        list2 = type2.keys()
        set1 = set(list1)
        set2 = set(list2)
        intersection = set1 & set2
        upper = 0

        if len(intersection)>0:
            for entity in intersection:
                p = (type1[entity]+type2[entity])/2.0
                upper+=p
        if len(type1) > len(type2):
            shorter_len = len(type2)
        else:
            shorter_len = len(type1)

        if shorter_len == 0:
            return 0
        else:
            jaccard = float(upper / shorter_len)
            return jaccard

    def typeSim(self, dict1, dict2):
        """Type similarity"""

        t1_type_list = []
        for noun, noun_detail in dict1.items():
            for entity, entity_detail in noun_detail.items():
                t1_type_list.extend(entity_detail[1])
        #print(t1_type_list)

        t2_type_list = []
        for noun, noun_detail in dict2.items():
            for entity, entity_detail in noun_detail.items():
                t2_type_list.extend(entity_detail[1])
        #print(t2_type_list)

        return (self.overlapCoefficient(t1_type_list, t2_type_list))

    def overlapCoefficient(self, type1, type2):
        """Overlap Coefficient between lists"""

        set1 = set(type1)
        set2 = set(type2)

        union = set1 | set2
        intersection = set1 & set2

        if len(type1) > len(type2):
            shorter_len = len(type2)
        else:
            shorter_len = len(type1)

        # jaccard = float(len(intersection)) / len(union)
        if shorter_len == 0:
            return 0
        else:
            jaccard = float(len(intersection)) / shorter_len
            return jaccard

    def domainSim(self, vector1, vector2):
        """Domain similarity"""

        #vector1 = self.calculateDomainVector(dict1)
        #vector2 = self.calculateDomainVector(dict2)

        return self.cosine_similarity(vector1,vector2)

    def calculateDomainVector(self, sourceinfo_dict):
        """Calcualte the domain vector for the source text of one triple"""
        D = self.domain_num
        v = []
        for k in range(0, D):
            hashmap = {}
            hashmap.update({(0, 0): 1})
            for noun, entity_type in sourceinfo_dict.items():
                # print '-'*40
                newmap = {}
                for key in hashmap.keys():
                    sum_ = key[0]
                    norm = key[1]
                    old_value = hashmap[key]
                    for entity, type_prob_descrip in entity_type.items():
                        A = type_prob_descrip[3]
                        p = type_prob_descrip[0]
                        # print A
                        # print sum_
                        # print A[k]
                        # print norm
                        # print sum(list(A))
                        if A[k] > self.beta:
                            A[k] = self.beta
                        temp = (sum_ + A[k], norm + sum(A))
                        if temp not in newmap.keys():
                            newmap.update({temp: 0})
                        newmap[temp] += old_value * p
                hashmap = newmap
            v_temp = 0
            for key_final in hashmap.keys():
                if key_final[1] > 0:
                    v_temp += float(key_final[0]) / key_final[1] * hashmap[key_final]
            v.append(v_temp)
        print(v)
        return v

    def cosine_similarity(self, x, y):
        """ return cosine similarity between two lists """
        if sum(x)==0 or sum(y) == 0:
            return -1
        numerator = sum(a * b for a, b in zip(x, y))
        denominator = self.square_rooted(x) * self.square_rooted(y)
        return round(numerator / float(denominator), 8)

    def square_rooted(self, x):
        """ return 3 rounded square rooted value """
        return round(math.sqrt(sum([a * a for a in x])), 3)