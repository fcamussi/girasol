#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 02:07:42 2022

@author: fernando
"""

from sklearn.model_selection import train_test_split


parcelas = range(1, 151)
train,test = train_test_split(parcelas, test_size=0.1, random_state=0)
print(f'cantidad: {len(parcelas)}')
print(f'cantidad train: {len(train)}')
print(f'cantidad test: {len(test)}')
print('--- . ---')
print('train:')
print(train)
print('test:')
print(test)
