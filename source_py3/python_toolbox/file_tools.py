# Copyright 2009-2014 Ram Rachum.
# This program is distributed under the MIT license.

'''Defines various tools related to temporary files.'''

import pathlib
import re

from python_toolbox import context_management


N_MAX_ATTEMPTS = 100

numbered_name_pattern = re.compile(
    r'''(?P<raw_name>.*) \((?P<number>[0-9]+)\)'''
)

def _get_next_name(path):
    assert isinstance(path, pathlib.Path)
    suffix = path.suffix
    suffixless_name = path.name[:-len(suffix)]
    parent_with_separator = str(path)[:-len(path.name)]
    assert pathlib.Path('{}{}{}'.format(parent_with_separator,
                                        suffixless_name, suffix)) == path
    match = numbered_name_pattern.match(suffixless_name)
    if match:
        fixed_suffixless_name = '{} ({})'.format(
            match.group('raw_name'),
            int(match.group('number'))+1,
        )
    else:
        fixed_suffixless_name = '{} (1)'.format(suffixless_name,)
    return pathlib.Path(
        '{}{}{}'.format(parent_with_separator, fixed_suffixless_name, suffix)
    )
    
    
class FileContainer(context_management.ContextManager):
    def __init__(self, file):
        self.file = file
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        return self.file.__exit__(exc_type, exc_value, exc_traceback)
        

def create_file_renaming_if_taken(path, mode='x',
                                  buffering=-1, encoding=None,
                                  errors=None, newline=None):
    assert 'x' in mode
    current_path = pathlib.Path(path)
    for i in range(N_MAX_ATTEMPTS):
        try:
            return current_path.open(mode, buffering=buffering,
                                     encoding=encoding, errors=errors,
                                     newline=newline)
        except FileExistsError:
            current_path = _get_next_name(current_path)
    else:
        raise Exception("Exceeded {} tries, can't create file {}".format(
            N_MAX_ATTEMPTS,
            path
        ))
    

def write_to_file_renaming_if_taken(path, data, mode='x',
                                    buffering=-1, encoding=None,
                                    errors=None, newline=None):
    with create_file_renaming_if_taken(
        path, mode=mode, buffering=buffering, encoding=encoding, errors=errors,
        newline=newline) as file:
        
        return file.write(data)
        