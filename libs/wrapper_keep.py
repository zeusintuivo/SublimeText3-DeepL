#!/usr/bin/python
# coding:utf-8

def side_trims(text):
    largo = len(text)
    left_diff = largo - len(text.lstrip())
    lefty = ""
    if left_diff > 0:
        lefty = text[:left_diff]
    righty_aus = text.rstrip()
    right_diff = (largo - len(righty_aus)) * -1
    righty = ""
    if right_diff < 0:
        righty = text[right_diff:]
    trimo = righty_aus.lstrip()
    print('trans ("' + text + '")')
    print('trimo ("' + lefty + '")' + str(left_diff) + '("' + trimo + '")' + str(right_diff) + '("' + righty + '")')

    return [lefty, righty, trimo]



def wrapper_keep(sentence, start, end, fake):
    sentence_data = ""
    split_percent = sentence.split(start)  # ' < '
    splitted_trans = ""
    count_split = 0
    for splitted in split_percent:
        if splitted in (None, ''):
            print('wrapper a z null')
            splitted_trans = splitted_trans + start  # ' < '
        else:
            print('wrapper b z ', start, splitted)
            if end in splitted:  # ' > '
                print('wrapper end', end, splitted)
                cut_other_part = splitted.split(end)  # ' > '
                first_part = cut_other_part[0]
                second_part_split = cut_other_part[1]
                if second_part_split in (None, ''):
                    splited_data = ''
                else:
                    print('wrapper first_part', start, first_part)
                    splited_data_trans = 'trans 1'
                    print('wrapper second part', end, second_part_split)
                    splited_data = splited_data + 'trans 2'
                if count_split == 0:
                    splitted_trans = splitted_trans + splited_data_trans + end + splited_data  # ' > '
                else:
                    splitted_trans = splitted_trans + start + splited_data_trans + end + splited_data  # ' < '+' > '
            else:
                print('wrapper  else', splitted)
                splited_data = 'trans 3'
                splitted_trans = splitted_trans + splited_data
                splitted_trans = splited_data
            count_split = count_split + 1
    if count_split == 0:
        sentence_data = sentence_data + start + splitted_trans  # ' < '
    else:
        sentence_data = splitted_trans
    return sentence_data





print(wrapper_keep('Les Cookies dits « Techniques » (listés ci-après) ayant pour', '«', '»', True))

#
# sp
#