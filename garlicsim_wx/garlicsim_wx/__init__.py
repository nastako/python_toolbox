# Copyright 2009 Ram Rachum. No part of this program may be used, copied or
# distributed without explicit written permission from Ram Rachum.

'''
This is garlicsim_wx, a wxPython GUI for GarlicSim.

The final goal of this project is to become a fully-fledged application for
working with simulations, friendly enough that it may be used by
non-programmers.
'''

import bootstrap

import wx

from application_window import ApplicationWindow
from gui_project import GuiProject

def start():
    '''
    Start the gui.
    '''
    app = wx.PySimpleApp()
    my_app_win = ApplicationWindow(None, -1, "GarlicSim", size=(600, 600))

    '''
    import cProfile
    cProfile.run("app.MainLoop()")
    '''
    app.MainLoop()
    
if __name__ == "__main__":
    start()