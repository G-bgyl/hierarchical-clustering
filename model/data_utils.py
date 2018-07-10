import pandas as pd

from  usrCut import *
import re

def is_Chinese_word(string):
    flag = False
    if re.search('[\u4e00-\u9fa5]', string) is not None:
        flag=True
    return flag

def is_string(string):
    flag = False
    if (re.search('[\u4e00-\u9fa5]', string) is None) and (re.search('[a-zA-Z]', string) is not None):
        flag = True
    return flag

def is_digit(string):
    flag = False
    if (not is_Chinese_word(string)) and (not is_string(string)) and (re.search("\d", string) is not None):
        flag = True
    return flag

def is_time(string):
    regex = "(\d+年\d+月\d+日)|(\d+年\d+月)|(\d+月\d+日)|((?<![-\d])\d+日)|(([012]{2})?\d{2}-\d{1,2}-\d{1,2})|([01]?\d-[0123]?\d(?!\d))|2018\d{4}|(\d+/\d+/\d+)|(\d+/\d+)|\d+-\d+ 月|[0,1]\d[0,1,2,3]\d"
    regex_time = "(\d+:\d+:\d+)|(\d+:\d+)|(\d+时\d+分\d+秒)|(\d+时\d+分)|(\d+时)|(\d+：\d+)|(\d{4} \d{4})|\d{1,2}日[0,1,2]\d点\d{2}分"
    # match_dt日期匹配，match_t时间匹配
    match_dt = re.search("(" + regex + ")" + "[\s,，]?" + "(" + regex_time + ")?", string)
    if match_dt is not None:
        return True
    else:
        return False

def sent_num_mask(one_sent, list = True,mask = True):
    """create a mask for numbers, turn time to 8, turn money and others to 1

    :param sentence: a list of word segments in one sentence, or a string of one sentence
    :param list: Boolean type. If True, the input should be a list, or it would be a string
    :param mask: Boolean type. Default True. If False, then jump the process of mask.
    :return:a list of word segments with mask
    """
    if list:
        if type(one_sent)== str:  # when the input is a string, like: '['w1','w2','w3'...]'
            one_sent=eval(one_sent)
        elif type(one_sent) == list and len(one_sent)==1:
            # when the input is a list of only one long string(of a list), like:["['w1','w2','w3'...]"]
            one_sent = eval(one_sent[0])

        if mask:
            sentence = ''.join(one_sent)
            sentence = hidden(sentence)
            # sentence = []
            # for seg in one_sent:
            #     if is_time(seg):
            #         seg = re.sub('\d', '1', seg)
            #     elif is_digit(seg):
            #         seg = re.sub('\d', '8', seg)
            #     elif is_string(seg):
            #         seg = re.sub('[a-zA-Z]','x',seg)
            #     sentence.append(seg)
        else:
            sentence = one_sent
    else:
        sentence = hidden(one_sent)

    return sentence

def delete_repetition( corpus, out_file=None, tolist = None, todict = None):
    """

    :param file_name: string of origin file name
    :param subset: a sequence or a list of column name that become the standard of defining repetition
    :param out_file:  string of output file name
    :return: a pandas dataframe
    """

    # print('Reading data...')
    if type(corpus)==list:
        data = pd.Series(corpus)
        print('df shape before drop:',data.shape)
        df = data.drop_duplicates()
    elif type(corpus)==dict:
        data = pd.DataFrame.from_dict(corpus, orient='index')
        print('df shape before drop:',data.shape)
        df = data.drop_duplicates()

    # output a file if needed
    if out_file:
        df.to_csv(out_file, sep='\t', header=True, index=False)
        print('Output file: %s\n' % (out_file))


    # print('df shape after drop:', df.shape)
    if tolist:
        df = df.values.tolist()
    elif todict:
        df = df.T.to_dict('list')
    return df

# word seg
def word_seg(text):
    """ calling function from usrCut

    :param text:
    :return:
    """
    return date_string_split(text)