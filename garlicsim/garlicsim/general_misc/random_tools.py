# Copyright 2009-2011 Ram Rachum.
# This program is distributed under the LGPL2.1 license.

'''
This module defines the `` class.

See its documentation for more information.
'''

import random


def random_partition(sequence, partition_size, allow_reminder=False):
    if allow_reminder:
        raise NotImplementedError
    if len(sequence) % partition_size != 0:
        raise Exception('''blocktodo''')
    
    shuffled_sequence = shuffled(sequence)

    subsequences = [shuffled_sequence[i::partition_size] for i in
                    xrange(partition_size)]
    
    return zip(*subsequences)


def shuffled(sequence):
    sequence_copy = sequence[:]
    random.shuffle(sequence_copy)
    return sequence_copy