import six

def unidecode(unicode_str):
    if six.PY2:
        text_type = six.text_type
    if six.PY3:
        text_type = six.text_type
    if isinstance(unicode_str,six.string_types):
        try:
            _unicode_str = str(unicode(unicode_str).encode("utf-8"))
            #TODO not working...
            # _unicode_str = str(text_type(unicode_str)).encode("utf-8")
            return _unicode_str
        except:
            return unicode_str

    return unicode_str

def strcode(string):
    if six.PY2:
        r = str(string)
    if six.PY3:
        r = unidecode(string).decode()
    return r

# if __name__ == '__main__':
#     # A = strcode(b'/data/dopa-onco/etc/dopa-onco.db')
#     A = unidecode(b"asdas").decode("utf-8")
#     pass
