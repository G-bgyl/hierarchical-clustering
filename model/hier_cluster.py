'''hier_cluster.py
    created by 5dgravity,2018
    main input:     10w raw file
                    a interval of string length and stopword threshold,
    main output:    a dendrogram picture.
    path: /sms_sp_class/model
    directory needed:
        ../data/    raw data stored here
        ../pickles/ process of function create_corpus() saved here
        ../pic/     picture outputs saved here
        ../outputs/ text ouputs saved here

'''

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from scipy.cluster.hierarchy import ward, dendrogram

import matplotlib.pyplot as plt

from data_utils import *
import pickle
from datetime import datetime

import csv
def create_corpus(start,end,threshold,save = False, overide = False):
    fname = '%s-%s-%s' % (start, end, threshold)
    if overide:
        corpus = pickle.load(open("corpus%s-%s.p" % (datetime.now().strftime("%m%d"), fname),"rb"))
        text_unseg = pickle.load(open("text_unseg%s-%s.p" % (datetime.now().strftime("%m%d"), fname),"rb"))

        print('finish load corpus from pickle!')
        return corpus,text_unseg
    else:
        stop_words = []
        # print('Begin prepare lines:')

        text_seg, text_unseg,text_unseg2  = {},{}, {}
        corpus_freq = {}
        corpus = {}
        with open('../data/sms_10w_0705.txt', 'r') as f:
            lines = [i.strip() for i in f.readlines()]
            lines = [i.split("\t") for i in lines]

            # select content row
            for k, line in enumerate(lines):
                if len(line[12])<=start or len(line[12]) >end:
                    continue
                else:
                    sent = sent_num_mask(line[12],list=False)
                    text_unseg[k] = sent

            len_unseg = len(text_unseg)
            # create word seg and count frequency of each word
            # len of text_seg should be the same of text_unseg
            for i,text in text_unseg.items():
                w_list = word_seg(text)

                # add mask to sents that have already segmented.
                # add mask to delete duplicate more efficiently
                # sent = sent_num_mask(w_list)

                # append one list of segs into dict
                text_seg[i] = w_list

                # count frequency: loop through each seg in w_list
                for i in  w_list:
                    if i in corpus_freq:
                        corpus_freq[i] += 1
                    else: corpus_freq[i] = 1

            # create stop words list
            for key, value  in corpus_freq.items():
                if value > threshold:
                    stop_words.append(key)
            print(stop_words)
            print('len of stop words:%d\n'%len(stop_words))


            # create the final word lists for tfidf
            for key, line in text_seg.items():
                # if i < 10000:
                    striped_list = []
                    line = list(line)

                    # filter the useless words for tfidf
                    for i in line:
                        if i not in stop_words:
                            striped_list.append(i)

                    if len(striped_list) >0:
                        # corpus[key] = striped_list
                        corpus[key] = "".join(striped_list)
                        text_unseg2[key] = ''.join(striped_list)
            text_unseg2 = delete_repetition(text_unseg2, todict=True) # return dict like: {id:['content']}

            id_list = sorted(text_unseg2.keys())
            text_unseg  = [text_unseg[i]    for i in id_list]  # return list like:['content1','content2'...]
            corpus      = [corpus[i]        for i in id_list]  # return list like:[['1','11'],['2','22']...]

            print('len of final corpus:%d'%len(text_unseg))

            print('scope of delete reduplication:%s%%\n'%(round(100 * (len_unseg - len(corpus))/len_unseg,3)))

        if save:
            pickle.dump(corpus, open("../pickles/corpus%s-%s.p" % (datetime.now().strftime("%m%d"), fname), "wb+"))
            pickle.dump(text_unseg, open("../pickles/text_unseg%s-%s.p" % (datetime.now().strftime("%m%d"), fname), "wb+"))

            # print('finish save corpus to pickle!\n')
    return corpus, text_unseg, fname




def plot(corpus,fname):
    """ plot the dendrogram based on corpus

    :param corpus: a list of lists represent sentences, in which each word is seperated by space
    :param fname: a string that will be part of the file name, aims to distinguish the output file
    :return: a dendrogram instance that help to analysis each sentence within dendrogram
    """
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
    print('Begin prepare matrices:',tfidf_matrix.shape)
    def print_tfidf():
        # print words and tfidfs:
        words = tfidf_vectorizer.get_feature_names()
        for i in range(len(corpus)):
            if i<5:
                print('----Document %d----' % (i))
                for j in range(len(words)):
                    if tfidf_matrix[i, j] > 1e-5:
                        print(words[j], tfidf_matrix[i, j])  # .encode('utf-8')
    print_tfidf()

    dist = 1 - cosine_similarity(tfidf_matrix)

    print('\nBegin print img:')
    linkage_matrix = ward(dist) #define the linkage_matrix using ward clustering pre-computed distances
    print('line 68: linkage_matrix = ward(dist)')
    fig, ax = plt.subplots(figsize=(20, 600)) # set size
    ax = dendrogram(
        linkage_matrix,
        leaf_font_size=6,
        orientation="right"
        # ,
        # truncate_mode='lastp', # show only the last p merged clusters
        # p=12,  # show only the last p merged clusters
        # leaf_rotation=90.,
        # show_contracted=True,  # to get a distribution impression in truncated branches

        )  # labels=[i for i in range(len(corpus))]

    print('line 71: ax = dendrogram(...)')
    plt.tick_params(\
        axis= 'x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off')
    print('line 78: plt.tick_params')
    plt.tight_layout() #show plot with tight layout # plt.show()
    print('line 80: plt.tight_layout()')

    plt.savefig('../pic/ward_clusters-%s.png'%(fname), dpi=100) #save figure as ward_clusters
    return ax

if __name__=='__main__':

    _min,_max,threshold = 20,50,800

    corpus, text_unseg, fname= create_corpus(_min,_max,threshold, save = False, overide = False)
    print(fname)
    ax = plot(corpus,fname)

    with open('../outputs/%s-%s.csv'%(fname,datetime.now().strftime("%m%d")),'w') as file:
        writer = csv.writer(file, delimiter = '\t')
        ids= ax['leaves']
        for i in reversed(ids):
            # writer.writerow(['%5s'%(i),'%85s'%text_unseg[i],'%85s'%(''.join(corpus[i]))])
            writer.writerow(['%5s'%(i),text_unseg[i]])

            # print('%s   \t%s'%(i,text_unseg[i])) # ''.join(corpus[i]),


