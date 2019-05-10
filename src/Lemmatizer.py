from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

class Lemmatizer():

    def __init__(self):
        self.postag_dict = {'JJ':'adj', 'JJR':'adj', 'JJS':'adj','CC':'con', 'DT':'det', 'CD':'num', 'PRP':'prp', 'PRP$':'prp', 'WP':'prp', 'WP$': 'prp', 'MD': 'mod'}


    def get_wordnet_pos(self,tag):
        if tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('V'):
            return wordnet.VERB
        elif tag.startswith('N'):
            return wordnet.NOUN
        elif tag.startswith('R'):
            return wordnet.ADV
        else:
            return None

    def lemmatizeSentence(self, sentence):
        tokens = word_tokenize(sentence)
        tagged_sent = pos_tag(tokens)

        wnl = WordNetLemmatizer()
        lemmas_sent = []
        for tag in tagged_sent:
            #print(tag)
            wordnet_pos = self.get_wordnet_pos(tag[1])
            if wordnet_pos == None:
                lemmas_sent.append(tag[0])
            else:
                lemmas_sent.append(wnl.lemmatize(tag[0], pos=wordnet_pos))
        return lemmas_sent

    def lemmatizeRelationInSenetnce(self, relation, triple):
        sentence = triple[0] + ' ' + triple[1] + ' ' + triple[2]
        tokens = word_tokenize(sentence)
        tagged_sent = pos_tag(tokens)
        wnl = WordNetLemmatizer()
        lemmas_sent = []
        for tag in tagged_sent:
            #print(tag)
            wordnet_pos = self.get_wordnet_pos(tag[1])
            if tag[1] in self.postag_dict.keys():
                lemmas_sent.append('[[' + self.postag_dict[tag[1]] + ']]')
            else:
                if wordnet_pos == None:
                    lemmas_sent.append(tag[0])
                else:
                    target = wnl.lemmatize(tag[0], pos=wordnet_pos)
                    lemmas_sent.append(target)
        relation_list = relation.split(' ')
        #print(relation_list)
        #print(triple)
        #print(lemmas_sent)

        start_index = len(triple[0].split(' '))
        end_index = len(lemmas_sent)-len(triple[2].split(' '))
        #print(start_index)
        #print(end_index)
        final_word = []
        for i in range(start_index, end_index):
            final_word.append(lemmas_sent[i])
        #print(final_word)
        return ' '.join(final_word)




if __name__ == '__main__':
    lem = Lemmatizer()
    sentence = 'football was a family of team sports that involve, to varying degrees, kicking a ball to score a goal.'
    sentence = 'he eventually becomes you'

    #print (lem.lemmatizeSentence(sentence))

    relation = 'interrogate'
    triple = ['Darth Vader', 'interrogates', 'Anna']
    print (lem.lemmatizeRelationInSenetnce(relation, triple))
