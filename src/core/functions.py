"""Core AWS config Class
"""

# Copyright (C) 1999-2021 Jerome Erasmus
# Written by Jerome Erasmus

import pyperclip3

__all__ = ['Functions', 'search_list']


class Functions:

    @staticmethod
    def copyClipboard(value):
        ''' Copies value to clipboard

        '''
        pyperclip3.copy(value)
        print(Fontcol.GREEN, '\nCopied to clipboard')



class Fontcol:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[97m'
