# Copyright 2009-2010 Ram Rachum. No part of this program may be used, copied
# or distributed without explicit written permission from Ram Rachum.

'''
Defines the Frame class.

See its documentation for more information.
'''

from __future__ import with_statement

import os
import sys
import random
import cPickle as pickle_module
import subprocess
import webbrowser

import wx
from garlicsim_wx.general_misc.third_party import aui
import pkg_resources

from garlicsim.general_misc import dict_tools
from garlicsim.general_misc import string_tools
import garlicsim_wx.general_misc.thread_timer as thread_timer

import garlicsim
from garlicsim_wx.gui_project import GuiProject
import garlicsim_wx.widgets
import garlicsim_wx.misc
from garlicsim_wx.widgets import workspace_widgets

from . import images as __images_package
images_package = __images_package.__name__


class Frame(wx.Frame):
    '''
    The main window of garlicsim_wx.
    
    This window allows the user to create and manipulate gui projects.
    '''
    def __init__(self, *args, **keywords):
        
        wx.Frame.__init__(self, *args, **keywords)
        
        self.SetDoubleBuffered(True)
        self.SetIcons(garlicsim_wx.misc.icon_bundle.get_icon_bundle())
        
        self.Bind(wx.EVT_CLOSE, self.on_close)
                
        self.tree_browser = None
        self.seek_bar = None
        self.shell = None
        self.state_repr_viewer = None
        
        self.aui_manager = garlicsim_wx.misc.aui.AuiManager(self)
                
        self.gui_project = None
        
        # tododoc properties here
        
        self.CreateStatusBar()
        
        self.__init_menus()        
        
        self.background_timer = thread_timer.ThreadTimer(self)
        
        self.background_timer.start(150)
        
        self.Bind(
            thread_timer.EVT_THREAD_TIMER,
            lambda event: self.sync_crunchers(),
            self.background_timer
        )
        
        self.aui_manager.Update()
        
        self.Show()
        
        self.Maximize()

        
    def __init_menus(self):
                
        
        menu_bar = self.menu_bar = garlicsim_wx.misc.MenuBar(self)
        self.SetMenuBar(menu_bar)
        
        """
        tododoc: is this needed?
        self._recalculate_all_menus()
        """
        
        
    def _recalculate_all_menus(self):
        try_recalculate = lambda thing: \
            thing._recalculate() if hasattr(thing, '_recalculate') else None
        for (menu, label) in self.menu_bar.GetMenus():
            for item in menu.GetMenuItems():
                try_recalculate(item)
            try_recalculate(menu)
        try_recalculate(self.menu_bar)

    
    def on_close(self, event):
        '''Close the application window.'''
        if self.gui_project:
            self.gui_project.stop_playing()
        self.aui_manager.UnInit()
        self.Destroy()        
        event.Skip()        
        self.background_timer.stop()

    def finalize_active_node(self, e=None):
        '''Finalize editing of the active node in the active gui project.'''
        assert self.gui_project
        return self.gui_project.finalize_active_node()

    def on_new(self, event=None):
        '''Create a new gui project.'''        
        
        if self.gui_project is not None:
            
            if hasattr(sys, 'frozen'):
                program_to_run = [sys.executable]
                we_are_main_program = 'GarlicSim' in sys.executable
            else:
                main_script = os.path.abspath(sys.argv[0])
                program_to_run = [sys.executable, main_script]
                we_are_main_program = ('run_gui' in main_script) or \
                                    ('garlicsim_wx' in main_script)
            
            if not we_are_main_program:
                dialog = \
                    garlicsim_wx.widgets.misc.NotMainProgramWarningDialog(self)
                if dialog.ShowModal() != wx.ID_YES:
                    return
        
        dialog = garlicsim_wx.widgets.misc.SimpackSelectionDialog(self)
        
        if dialog.ShowModal() == wx.ID_OK:
            simpack = dialog.get_simpack_selection()
        else:
            dialog.Destroy()
            return
        dialog.Destroy()

        
        if self.gui_project is None:
            self._new_gui_project_from_simpack(simpack)
        else:    
                
            program_to_run.append('__garlicsim_wx_new=%s' % simpack.__name__)
         
            subprocess.Popen(program_to_run)
            
            return
            
    def _new_gui_project_from_simpack(self, simpack):
        assert self.gui_project is None # tododoc
        gui_project = GuiProject(simpack, self)
        self.__setup_gui_project(gui_project)

    def on_exit_menu_button(self, event):
        '''Exit menu button handler.'''
        self._post_close_event()

        
    def _post_close_event(self):
        '''Post a close event to the frame.'''
        event = wx.PyEvent(self.Id)
        event.SetEventType(wx.wxEVT_CLOSE_WINDOW)
        wx.PostEvent(self, event)
        
        
    def sync_crunchers(self):
        '''
        Take work from the crunchers, and give them new instructions if needed.
                
        (This is a wrapper that calls the sync_crunchers method of all the
        gui projects.)
        
        Talks with all the crunchers, takes work from them for implementing
        into the tree, retiring crunchers or recruiting new crunchers as
        necessary.
        
        Returns the total amount of nodes that were added to each gui project's
        tree.
        '''
        nodes_added = self.gui_project.sync_crunchers() \
                    if self.gui_project else 0
        
        if nodes_added > 0:
            pass#self.Refresh()
        
        return nodes_added
    
    def __setup_gui_project(self, gui_project):
        
        self.gui_project = gui_project
        
        # todo: should create StateReprViewer only if the simpack got no
        # workspace widgets
        
        self.tree_browser = workspace_widgets.TreeBrowser(self)
        self.aui_manager.AddPane(
            self.tree_browser,
            aui.AuiPaneInfo()\
            .Bottom().Row(0)\
            .BestSize(1000, 100).MinSize(200, 50).MaxSize(10000, 250)\
            .Caption(self.tree_browser.get_uppercase_name())
            .Floatable(False)\
            .CloseButton(False)
        )
        
        self.playback_controls = workspace_widgets.PlaybackControls(self)
        self.aui_manager.AddPane(
            self.playback_controls,
            aui.AuiPaneInfo()\
            .Bottom()\
            .BestSize(184, 128).MinSize(184, 128).MaxSize(184, 128)\
            .Caption(self.playback_controls.get_uppercase_name())
            .Resizable(False)\
            .CloseButton(False)        
        )
        
        self.seek_bar = workspace_widgets.SeekBar(self)
        self.aui_manager.AddPane(
            self.seek_bar,
            aui.AuiPaneInfo()\
            .Bottom().Row(1)\
            .BestSize(600, 40).MinSize(200, 40).MaxSize(10000, 100)\
            .Caption(self.seek_bar.get_uppercase_name())
            .Floatable(False)\
            .CloseButton(False)
        )
        
        self.shell = workspace_widgets.Shell(self)
        self.aui_manager.AddPane(
            self.shell,
            aui.AuiPaneInfo()\
            .Right().Row(0)\
            .BestSize(400, 600)\
            .Caption(self.shell.get_uppercase_name())
            .MaximizeButton(True)\
            .CloseButton(False)
        )
        
        """
        self.state_repr_viewer = workspace_widgets.StateReprViewer(self)
        self.aui_manager.AddPane(
            self.state_repr_viewer,
            aui.AuiPaneInfo()\
            .BestSize(300, 300)\
            .MaximizeButton(True)\
            .Center()\
            .Caption(self.state_repr_viewer.get_uppercase_name())
            .Floatable(False)\
            .CloseButton(False)
        )
        """
        settings_wx = self.gui_project.simpack_wx_grokker.settings
        

        big_widget_class = settings_wx.BIG_WORKSPACE_WIDGETS[0] if \
                         settings_wx.BIG_WORKSPACE_WIDGETS else \
                         workspace_widgets.StateReprViewer

        self.big_widget = big_widget_class(self)
        self.aui_manager.AddPane(
            self.big_widget,
            aui.AuiPaneInfo()\
            .BestSize(300, 300)\
            .MaximizeButton(True)\
            .Center()\
            .Caption(self.big_widget.get_uppercase_name())
            .Floatable(False)\
            .CloseButton(False)
        )
        
        if isinstance(self.big_widget, workspace_widgets.StateReprViewer):
            self.state_repr_viewer = self.big_widget
        
        """
        big_widget_classes = \
            settings_wx.BIG_WORKSPACE_WIDGETS #+ \
        #    [workspace_widgets['StateReprViewer']]
        
        self.big_widgets = []
        # todo: not the right way, should be easy listing of all widget
        
        
        for i, BigWidget in enumerate(big_widget_classes):
            big_widget = BigWidget(self)
            self.aui_manager.AddPane(
                big_widget,
                aui.AuiPaneInfo()\
                .BestSize(300, 300)\
                .MaximizeButton(True)\
                .Center()\
                .Caption(big_widget.get_uppercase_name())\
                .Floatable(False)\
                .CloseButton(False),
                target=self.state_repr_viewer.get_aui_pane_info()
            )
            #.NotebookPage(notebook_id, i)\
            self.big_widgets.append(big_widget)

        """
        
        self.aui_manager.Update()
        
        self.gui_project.emitter_system.top_emitter.emit()
        
    
    def on_open(self, event=None):
        '''Raise a dialog for opening a gui project from file.'''
        
        if self.gui_project is not None:
            
            if hasattr(sys, 'frozen'):
                program_to_run = [sys.executable]
                we_are_main_program = 'GarlicSim' in sys.executable
            else:
                main_script = os.path.abspath(sys.argv[0])
                program_to_run = [sys.executable, main_script]
                we_are_main_program = ('run_gui' in main_script) or \
                                    ('garlicsim_wx' in main_script)
            
            if not we_are_main_program:
                dialog = \
                    garlicsim_wx.widgets.misc.NotMainProgramWarningDialog(self)
                if dialog.ShowModal() != wx.ID_YES:
                    return
                
        wildcard = 'GarlicSim Simulation Pickle (*.gssp)|*.gssp|All files (*)|*|'
        
        # Todo: something more sensible here. Ideally should be last place you
        # saved in, but for starters can be desktop.
        folder = os.getcwd()
        
        gui_project_vars = None

        open_dialog = wx.FileDialog(self, message='Choose a file',
                                    defaultDir=folder, defaultFile='',
                                    wcd=wildcard, style=wx.OPEN)
        if open_dialog.ShowModal() == wx.ID_OK:
            path = open_dialog.GetPath()
            
            if self.gui_project is None:
                self._open_gui_project_from_path(path)
            else:
                if hasattr(sys, 'frozen'):
                    program = [sys.executable]
                else:
                    program = [sys.executable, os.path.abspath(sys.argv[0])]
                    # Todo: what if some other program is launching my code?
                    
                program.append('__garlicsim_wx_load=%s' % path)
             
                subprocess.Popen(program)
                        
        
    
    def _open_gui_project_from_path(self, path):
        
        try:
            with file(path, 'r') as my_file:
                gui_project_vars = pickle_module.load(my_file)
                
        except Exception, exception:
            dialog = wx.MessageDialog(
                self,
                'Error opening file:\n' + str(exception),
                style=(wx.OK | wx.ICON_ERROR)
            )
            dialog.ShowModal()
            return
                
        if gui_project_vars:
            try:
                gui_project = GuiProject.load_from_vars(self, gui_project_vars)
            except Exception, exception:
                dialog = wx.MessageDialog(
                    self,
                    'Error opening file:\n' + str(exception),
                    style=(wx.OK | wx.ICON_ERROR)
                )
                dialog.ShowModal()
                
            self.__setup_gui_project(gui_project)

    
    
    def on_save(self, event=None):
        '''Raise a dialog for saving a gui project to file.'''
        
        assert self.gui_project is not None
        wildcard = 'GarlicSim Simulation Pickle (*.gssp)|*.gssp|All files (*)|*|'
        folder = os.getcwd()
        try:
            save_dialog = wx.FileDialog(self, message='Save file as...',
                                     defaultDir=folder, defaultFile='',
                                     wcd=wildcard,
                                     style=wx.SAVE | wx.OVERWRITE_PROMPT)
            if save_dialog.ShowModal() == wx.ID_OK:
                path = save_dialog.GetPath()
    
                try:
                    with file(path, 'w') as my_file:
                        picklable_vars = self.gui_project.__getstate__()
                        pickle_module.dump(picklable_vars, my_file)
    
                except IOError, error:
                    error_dialog = wx.MessageDialog(
                        self,
                        'Error saving file\n' + str(error)
                    )
                    error_dialog.ShowModal()
            
        finally:
            # fuck_the_path()
            pass
            
        save_dialog.Destroy()
    
    """    
    def delete_gui_project(self,gui_project):
        I did this wrong.
        self.gui_projects.remove(gui_project)
        self.notebook.AddPage(gui_project.main_window,"zort!")
        self.notebook.DeletePage(0)
        del gui_project
    """
