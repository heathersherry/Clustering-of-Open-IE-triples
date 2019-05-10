# Clustering-of-Open-IE-triples

*****************************************Readme*****************************************
The source code of SIST is in the /src folder. The dataset we used is in the /data folder

---------------------------------------Code---------------------------------------
To execute the complete clustering process of SIST, you need to follow these steps:

1. DomainGeneration.py
For each candidate entity of a noun phrase, it generates the domain counter of each type of the entity.
Input files: '../data/NYTimes2018/wiki_record_*.json' and '../data/ReVerb/wiki_record.json'
Output files: '../data/NYTimes2018/domain_tmp/wiki_record_*.json' and '../data/ReVerb/domain_tmp/wiki_record.json'

2. DomainVectorComputation.py
Compute the domain vector of a source text according to the specified beta and domain counter.
Input files: 
'../data/NYTimes2018/newyorktimes_openie_*.json' and the corresponding '../data/NYTimes2018/domain_tmp_wiki_record_*.json', or
'../data/Reverb/reverb45K_*_record.json' and the corresponding '../data/Reverb/domain_tmp/wiki_record.json'
Output files:
'../data/NYTimes2018/data_tmp_*/newyorktimes_openie_*.json', or
'../data/Reverb/data_tmp_*/reverb45K_*_record.json'

3. main.py
The clustering (based on specific domain lists and beta). The classes in Graph, TripleSimilarity and Lemmatizer are used to assist the clustering.
Input files: 
'../data/NYTimes2018/data_tmp_*/newyorktimes_openie_*.json', or
'../data/Reverb/data_tmp_*/reverb45K_*_record.json'
(Example: If we would like to conduct the clustering in Reverb on arts, business, entertainment, food, health, politics, science and sports, we first find their correponding ids in the folder '../data/Domain_keywords', i.e., [1, 3, 9, 12, 14, 19, 21,24]. We then define a beta value, e.g., 3. We then choose '../data/Reverb/data_tmp_[1, 3, 9, 12, 14, 19, 21, 24]_3/reverb45K_*_record.json' as the input file)
Output:
The clustering Results

---------------------------------------Data---------------------------------------
1. Reverb (as mentioned in the paper, with side information added): The original data is '../data/Reverb/*.json'
2. NYTimes2018 (as mentioned in the paper, with side information added): The original data is '../data/NYTimes2018/*.json'
3. Patty-dataset: This is a dataset released by "PATTY: A Taxonomy of Relational Patterns with Semantic Types" [EMNLP-CoNLL '12]. It contains relation patterns from both Wikipedia and NYTimes. We can use both patterns. 
4. Domain_keywords (as mentioned in the paper)
