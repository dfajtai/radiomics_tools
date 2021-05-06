#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import pandas as pd
import re
import unicodedata

sys.path.insert(0, '/home/fajtai/py/')

def delete_useless_spaces(S):
    return re.sub(r'([^ ]) ([^ ])','\g<1>\g<2>',S)

def hun2ascii_remove_spec(value, spaceholder = "_",allowed_chars = ".-"):
    try:
        value = unicodedata.normalize('NFKD', unicode(value, encoding="utf8")).encode('ascii', 'ignore').lower().strip()
    except:
        filtered_str = ""
        for s in str(value):
            try:
                value = unicodedata.normalize('NFKD', unicode(s, encoding="utf8")).encode('ascii', 'ignore').lower()
                filtered_str+=value
            except:
                continue
        value = filtered_str

    value = str(value).replace(" ", spaceholder)
    value = re.sub(re.compile('[{spaceholder}]+'.format(spaceholder=spaceholder)), "{spaceholder}".format(spaceholder=spaceholder), value)

    allowed_chars = ["\\-" if c=="-" else c for c in allowed_chars]

    value = re.sub(re.compile('[^A-Za-z0-9{characters}]+'.format(characters = str(spaceholder)+"".join(allowed_chars))),"",value)
    value = re.sub(r'^[\d+\W+]+',"",value) #remove leading chars
    # value = re.sub(r'^[\d+\W+{spaceholder}]+'.format(spaceholder=spaceholder),"",value) #remove leading chars
    return str(value)


def hun2ascii_simple(value, spaceholder = "_", csv_sep = ",", alternative_csv_sep = ";"):
    value = unicodedata.normalize('NFKD', unicode(value, encoding="utf8")).encode('ascii', 'ignore').lower().strip()
    value = str(value).replace(" ",spaceholder).replace(csv_sep,alternative_csv_sep)
    value = re.sub(re.compile('[{spaceholder}]+'.format(spaceholder=spaceholder)),"{spaceholder}".format(spaceholder=spaceholder),value)
    return str(value)

def split_special(value,spaceholder="_"):
    return re.split(r"[{spaceholder}]+".format(spaceholder=spaceholder),str(spaceholder).join(re.split("[^\w_]",value)))


if __name__ == '__main__':
    # print(hun2ascii_simple("    áaásdqűadsúö OASHD     , qweqwd _qwdq__123Ű"))
    print(hun2ascii_remove_spec("a123--_asdh\/|.aisdh$ß",allowed_chars=["-","|"]))
    print(split_special("asd__qwre_$qwe1asd"))