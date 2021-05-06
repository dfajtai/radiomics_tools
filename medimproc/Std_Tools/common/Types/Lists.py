#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'/home/fajtai/py/')
from Std_Tools.common.unidecode import strcode

class typed_list(list):
    def __init__(self,obj = None):
        super(typed_list,self).__init__()
        if obj == None:
            self._obj = object
        else:
            if type(obj) == type:
                self._obj = obj
            else:
                self._obj = type(obj)

    def append(self, object):
        if self._obj == object:
            super(typed_list, self).append(object)
            return self

        if isinstance(object,self._obj):
            super(typed_list,self).append(object)
        return self

    def extend(self, iterable):
        if self._obj == object:
            super(typed_list, self).extend(iterable)
            return self

        for i in iterable:
            if isinstance(i, self._obj):
                super(typed_list,self).append(i)
        return self


class named_list(typed_list):
    def __init__(self,obj = None,key = "name"):
        super(named_list,self).__init__(obj=obj)
        self._key = key

    def __new__(cls, data=None, *args, **kwargs):
        obj = super(named_list, cls).__new__(cls, data)
        return obj

    def __getitem__(self, key):
        """
        :param key: int - index or str - name
        :return: object -> type: self._obj.__class__
        """
        items = []
        key = strcode(key)
        if isinstance(key,str):
            for item in self:
                if hasattr(item, self._key):
                    # if eval("item.{0}".format(self._key)) == key:
                    if key in eval("item.{0}".format(self._key)):
                        items.append(item)
            if len(items)==0:
                raise IndexError('no object named {!r}'.format(key))
            return items

        return list.__getitem__(self,key)


    def __setitem__(self, key, value):
        if isinstance(key,str):
            for item in self:
                if hasattr(item, self._key):
                    if eval("item.{0}".format(self._key)) == key:
                        self.remove(item)
                        if isinstance(value, self._obj):
                            self.append(value)

    def __delitem__(self, key):
        if isinstance(key,str):
            for item in self:
                if hasattr(item, self._key):
                    if eval("item.{0}".format(self._key)) == key:
                        self.remove(item)


# L=["a","qq","qe",12,10,40]
#
# F = typed_list(int).extend(L)
# print F

# class C:
#     def __init__(self,n):
#         self.n = n

# q = C("a")
# N = named_list(obj=q,key="n")
# N.append(C("q"))
# N.append(C("w"))
# N.append(C("e"))
# print(N["e"].n)


