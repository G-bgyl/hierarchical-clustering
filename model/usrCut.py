import re
import jieba
import os


# 添加删除jieba词典
user_dict = os.getcwd() + "/词典/org_name.txt"
jieba.load_userdict(user_dict)
jieba.load_userdict(os.getcwd() + "/词典/combine_words.txt")
jieba.load_userdict("./词典/special_words.txt")
jieba.load_userdict("./词典/address.txt")
jieba.load_userdict("./词典/personal_name.txt")
with open("./词典/split_words.txt", "r") as f:
    for i in f.readlines():
        jieba.del_word(i.strip())


# 获得时间的mask
def get_datetime_masks(text):
    regex = "(\d+年\d+月\d+日)|(\d+年\d+月)|(\d+月\d+日)|((?<![-\d])\d+日)|(([012]{2})?\d{2}-\d{1,2}-\d{1,2})|([01]?\d-[0123]?\d(?!\d))|2018\d{4}|(\d+/\d+/\d+)|(\d+/\d+)|\d+-\d+ 月"
    regex_time = "(\d+:\d+:\d+)|(\d+:\d+)|(\d+时\d+分\d+秒)|(\d+时\d+分)|(\d+时)|(\d+：\d+)|(\d{4} \d{4})"
    # match_dt日期匹配，match_t时间匹配
    match_dt = re.finditer("(" + regex + ")" + "[\s,，]?" + "(" + regex_time + ")?", text)
    match_t = re.finditer(regex_time, text)
    result = [i.span() for i in match_dt]
    # if len(result) == 0:
    #     result.extend([i.span() for i in match_t])
    # else:
    result_t = [i.span() for i in match_t]
    # if len(result_t) != 0:
    # 去除时间重复
    for i in result_t:
        if i[1] not in [j for i, j in result]:
            result.append(i)
    # 去除匹配结尾的标点符号
    result_no_p = []
    for i in result:
        group = text[i[0]:i[1]]
        if re.search(".+[\s,，]$", group) is not None:
            result_no_p.append((i[0], i[1]-1))
        else:
            result_no_p.append((i[0], i[1]))
    return result_no_p


# 51人品和360借条不脱敏数字
def get_org_masks(text):
    orgs = ["51人品", "360借条"]
    regex = ["(" + i + ")|" for i in orgs]
    regex = "".join(regex)
    regex = regex[:-1]
    return [i.span() for i in re.finditer(regex, text)]


#文本脱敏
def hidden(text):
    bankName = ["中信银行", "长沙银行", "网商银行", "农商银行", "建设银行",
                "平安银行", "工商银行", "农业银行", "中国银行", "光大银行",
                "民生银行", "兴业银行", "广发银行", "邮储银行", "北京银行",
                "湘江银行", "交通银行", "微众银行", "华夏银行", "浦发银行",
                "人民银行", "招商银行", "广州银行"]
    # 替换 bankName 中的银行信息
    for i in bankName:
        text = re.sub(i.strip(), "某某银行", text, 0)
    # 替换数字信息
    date_time = get_datetime_masks(text) + get_org_masks(text)
    org = get_org_masks(text)
    org_index = []
    if len(org) > 0:
        for i in org:
            org_index.extend(list(range(i[0], i[1])))

    index = []

    if len(date_time) > 0:
        for i in date_time:
            index.extend(list(range(i[0], i[1])))

    text_hide_digit = ""
    for char in range(len(text)):
        if not text[char].isdigit():
            text_hide_digit += text[char]
        else:
            if char not in index:
                text_hide_digit += "8"
            else:
                if (re.search("20\d{2}",text[char:char+4]) is not None) or (re.search("20\d{2}",text[char-1:char+3]) is not None) or char in org_index:
                    text_hide_digit += text[char]
                else:
                    text_hide_digit += "1"
    text = re.sub("\d","8", text, 0)
    return text_hide_digit


#切分字符串
def cut_text(text, cuts):
    left = 0
    result = []
    cuts += [len(text)]
    cuts.sort()
    for c in cuts:
        tmp = text[left:c]
        if tmp:
            result += [tmp]
            left = c
    return result


# 根据mask结果重新切分字符串
def mask_cuts(s, c):
    #     l   r
    # ... ---- ...
    seg_left = seg_right = 0
    result = []
    cut = c.pop(0) if c else None

    while s:
        seg = s.pop(0) # get a new seg
        seg_left = seg_right
        seg_right += len(seg)

        # case 1: --- ... ( ) or nothing to cut
        # where ( ) denotes a pair of cuts, --- for seg
        if not cut or seg_right <= cut[0]:
            result += [seg]
        # case 2: -(-- ... --)-
        else:
            while s and seg_right < cut[1]:
                seg += s.pop(0)
                seg_right = seg_left + len(seg)
            # special case: -(--)--(--)-
            seg_cuts = []
            while cut and cut[1] <= seg_right:
                seg_cuts += [cut[0] - seg_left, cut[1] - seg_left]
                cut = c.pop(0) if c else None  # get a new cut
            result += cut_text(seg, seg_cuts)
    return result


#获得字符串mask
def get_char_masks(text):
    regex = "[a-zA-Z0-9-\*￥]([a-zA-Z0-9\*\-\./:#\+&@,，_]*[a-zA-Z0-9\*%\-‰])?"
    result_iter = re.finditer(regex, text)
    result = [i.span() for i in result_iter]
    return result


# 特殊处理带空格，括号，字符及强制性分词的词语
with open("./词典/special_name.txt", "r+") as f:
    special_name = [i.strip() for i in f.readlines()]
with open("./词典/address.txt", "r+") as f:
    address = [i.strip() for i in f.readlines()]


def get_special_masks(text):
    special = ["微信零 X", "支付宝（中国）网络技术有限公司", "ETC卡", "于", "e生活", "QQ钱包",
               "App Store & Apple Music", "E气费", "e招贷","e钱庄","E车E站", "金融IC卡",
               "融e联", "E商宝", "还款额", "应还款额","盗刷","交通违章","工资收入"]
    special = special + special_name + address
    regex = ["(" + i + ")|" for i in special]
    regex = "".join(regex)
    regex = regex[:-1]
    result_iter = re.finditer(regex, text)
    result = [i.span() for i in result_iter]
    return result


# 修改特殊处理结果
def get_revised_special_masks(text):
    revised = ["等于", "基于"]
    regex = ["(" + i + ")|" for i in revised]
    regex = "".join(regex)
    regex = regex[:-1]
    result_iter = re.finditer(regex, text)
    result = [i.span() for i in result_iter]
    return result


#jieba分词，根据分词字符位置切分脱敏的文本



def jieba_cut_hide(text):
    segs = [i for i in jieba.cut(text)]
    return segs


def date_string_split(text):
    jieba_split = jieba_cut_hide(text)
    char_masked = mask_cuts(jieba_split, get_char_masks(text))
    datetime_masked = mask_cuts(char_masked, get_datetime_masks(text))
    org_masked = mask_cuts(datetime_masked, get_org_masks(text))
    special_masked = mask_cuts(org_masked, get_special_masks(text))
    revised_special_masked = mask_cuts(special_masked, get_revised_special_masks(text))
    return revised_special_masked

if __name__ == "__main__":
    # import pandas as pd
    # data = pd.read_csv("data_clean1.txt", delimiter="\t")
    revised_special_masked = date_string_split('000分词系统')
    print(revised_special_masked)
