import json
import pickle
import re

import pandas as pd

data = pd.read_stata('trademark.dta')
data_nodup = data.drop_duplicates('or_name')

list_id = list(data_nodup['rf_id'])

list_old_conm = list(data_nodup['or_name'])
list_conm = []
for i in range(0, len(list_old_conm)):
    name = list_old_conm[i].lower()  # lower case
    list_conm.append(name)

post = r"( |\()a corp.*of.*$"  # "a corp... of..."
post_re = re.compile(post)
for i in range(0, len(list_conm)):
    name = list_conm[i]
    newname = post_re.sub('', name)
    list_conm[i] = newname

# change ., to space
for i in range(0, len(list_conm)):
    name = list_conm[i]
    if '.,' in name:
        newname = name.replace('.,', ' ')
        list_conm[i] = newname

# replacce x.y.z to xyz


def fix_pattern(name, i):  # i from 10 to 1
    temp_re = re.compile(r'\b(\w)' + i*r'\.(\w)\b')  # x.x.x
    m = re.search(temp_re, name)
    if m:
        new_re = ''.join(ele for ele in ['\\' + str(j)
                                         for j in range(1, i+1+1)])
        # reverse quoation, new_re = r"\1\2\3"
        newname = temp_re.sub(new_re, name)
        return newname
    else:
        return name


for i in range(0, len(list_conm)):
    name = list_conm[i]
    newname = list_conm[i]
    for n_x in range(10, 0, -1):
        newname = fix_pattern(newname, n_x)
    if newname != name:
        list_conm[i] = newname

# clean every char to correct ones
list_conm_afcharc = []

garbage = []
for i in range(0, 33):
    garbage.append(chr(ord('\x80') + i))

garbage.append('\xad')

# dict_replace gives the correct char to replace the old one
with open('dict_char_replace.json', 'r') as f:
    dict_replace = json.load(f)

for i in range(0, len(list_conm)):
    name = list_conm[i]
    newchar_list = []
    for char in name:
        if char == "\"":
            newchar_list.append(" ")
        elif char in garbage:
            newchar_list.append(" ")
        elif char != ' ':
            newchar_list.append(dict_replace[char])
        else:
            newchar_list.append(' ')
    newname = ''.join(newchar for newchar in newchar_list)
    list_conm_afcharc.append(newname)

# dont replace . as space, keep dot, because for .com or .net keeping them has better results for search
# dot space or dot at the end of the string or dot at beg
dot2replace_re = re.compile(r"\. |\.$|^\.")
for i in range(0, len(list_conm_afcharc)):
    name = list_conm_afcharc[i]
    newname = dot2replace_re.sub(' ', name)
    list_conm_afcharc[i] = newname

# clean extra white space
white0_re = re.compile(r" +")
for i in range(0, len(list_conm_afcharc)):
    name = list_conm_afcharc[i]
    newname = white0_re.sub(' ', name)
    list_conm_afcharc[i] = newname

# begin or end with whitespace
white1_re = re.compile(r"^ | $")
for i in range(0, len(list_conm_afcharc)):
    name = list_conm_afcharc[i]
    newname = white1_re.sub('', name)
    list_conm_afcharc[i] = newname

# take care of u s, u s a
usa_re = re.compile(r"\b(u) \b(s) \b(a)\b")
us_re = re.compile(r"\b(u) \b(s)\b")
for i in range(0, len(list_conm_afcharc)):
    name = list_conm_afcharc[i]
    newname = usa_re.sub('usa', name)
    newname = us_re.sub('us', newname)
    list_conm_afcharc[i] = newname

with open('list_trademark_id.piclke', 'wb') as handle:
    pickle.dump(list_id, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('list_trademark_conm.piclke', 'wb') as handle:
    pickle.dump(list_old_conm, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('list_trademark_newname.piclke', 'wb') as handle:
    pickle.dump(list_conm_afcharc, handle, protocol=pickle.HIGHEST_PROTOCOL)
