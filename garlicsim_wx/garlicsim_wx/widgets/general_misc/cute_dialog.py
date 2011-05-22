# Copyright 2009-2011 Ram Rachum.
# This program is distributed under the LGPL2.1 license.

'''
Defines the `CuteDialog` class.

See its documentation for more info.
'''

import wx

from garlicsim_wx.general_misc import wx_tools
from .cute_top_level_window import CuteTopLevelWindow


class CuteDialog(wx.Dialog, CuteTopLevelWindow):
    '''Improved dialog.'''
    
    def __init__(self, *args, **kwargs):
        if not kwargs.pop('skip_wx_init', False):
            wx.Dialog.__init__(self, *args, **kwargs)
        CuteTopLevelWindow.__init__(self, *args, **kwargs)
        self.set_good_background_color()
        self.SetDoubleBuffered(True)
        
        
    def ShowModal(self):
        self.Centre(wx.BOTH)
        return super(CuteDialog, self).ShowModal()
    
    
    @classmethod # blocktodo: Use everywhere I can, document
    def create_and_show_modal(cls, *args, **kwargs):
        dialog = cls(*args, **kwargs)
        try:
            result = dialog.ShowModal()
        finally:
            dialog.Destroy()
        return result