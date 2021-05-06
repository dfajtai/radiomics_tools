#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys

sys.path.insert(0, '/home/fajtai/py/')


def vprint(L):
    """
    Vertically print content of a list.
    :param L:
    :return:
    """
    def findMaxLen(L):
        if isinstance(L,list):
            if L == []:
                return 0

            lenList=[]
            for l in L:
                if type(l)==list:
                    lenList.append(max([len(str(k)) for k in l]))
                else:
                    lenList.append(len(l))
            return max(lenList)

        else:
            return len(L)

    maxLen =findMaxLen(L)

    formatter = '{:<*}'.replace("*",str(maxLen))

    if isinstance(L,list):
        for l in L:
            if isinstance(l,list):
                print("\t".join([formatter.format(k) for k in l]))
            else:
                print(str(l))
    else:
        return

def vprint_dict(_dict):
    l = []
    if isinstance(_dict,dict):
        for k in _dict.keys():
            l.append([k,_dict[k]])
        vprint(l)

def unwrapList(L):
    """
    Recursive method to get the list of all item in a complex/nested list.
    Example: L = [1,[2,3],[[4,5],6],[[[7,8,9]]],10,[],[11,[0]]] -> [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0]
    :param L: Nested list
    :return: List of items
    """
    items = []
    if isinstance(L,list):
        # print "List:"
        # print L
        for l in L:
            if isinstance(l,list):
                items.extend(unwrapList(l))
            elif isinstance(l,tuple):
                items.extend(unwrapList(list(l)))
            else:
                items.append(l)
        return items
    return L

def unwrapItems(V):
    if isinstance(V,list):
        return unwrapList(V)
    else:
        return [V]

def transpose_nested(nested_list):
    return map(list, zip(*nested_list))


def unique_list_items(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]