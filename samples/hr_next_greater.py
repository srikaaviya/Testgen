# !/bin/python3

import math
import os
import random
import re
import sys

from collections import defaultdict


def findNextGreaterElementsWithDistance(readings):
    stack = [(readings[0], 0)]
    dic = defaultdict(list)
    res = []

    for i in range(1, len(readings)):
        while stack and readings[i] > stack[-1][0]:
            dic[stack[-1][0]].append((readings[i], (i - stack[-1][1])))
            stack.pop()
        stack.append((readings[i], i))

    for i in readings:
        if i in dic:
            res.append(dic[i].pop())
        else:
            res.append([-1, -1])
    return res


if __name__ == '__main__':
    readings_count = int(input().strip())

    readings = []

    for _ in range(readings_count):
        readings_item = int(input().strip())
        readings.append(readings_item)

    result = findNextGreaterElementsWithDistance(readings)

    print('\n'.join([' '.join(map(str, x)) for x in result]))
