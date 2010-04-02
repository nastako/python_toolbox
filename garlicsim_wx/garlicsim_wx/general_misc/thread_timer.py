# Copyright 2009-2010 Ram Rachum. No part of this program may be used, copied
# or distributed without explicit written permission from Ram Rachum.

'''
This module defines the ThreadTimer object. See its documentation for more
info.
'''
# todo: daemonize?
# todo: kickass idea: make all timers use one thread that will sleep smartly
# to send all events correctly.

import threading
import time

import wx

wxEVT_THREAD_TIMER = wx.NewEventType()
EVT_THREAD_TIMER = wx.PyEventBinder(wxEVT_THREAD_TIMER, 1)

class ThreadTimer(object):
   '''
   A timer for a wxPython app which runs on a different thread.
   
   This solved a problem of wxPython timers being late when the program is
   busy.
   '''
   n = 0
   def __init__(self, parent):
      self.parent = parent
      ThreadTimer.n += 1
      self.wx_id = wx.NewId()
      self.__init_thread()
      self.alive = False

   def __init_thread(self):
      thread_name = ''.join(('Thread used by ThreadTimer no. ', str(self.n)))
      self.thread = Thread(name=thread_name)
      # Overwriting previous thread, so it'll get garbage-collected, hopefully
      self.thread.parent = self
   
   def start(self, interval):
      '''Start the timer.'''
      self.interval = interval
      self.alive = True
      self.thread.start()

   def stop(self):
      '''Stop the timer.'''
      self.alive = False
      self.__init_thread()
   
   Start = start
   Stop = stop
      
   def GetId(self):
      return self.wx_id

      
class Thread(threading.Thread):
   '''Thread used as a timer for wxPython programs.'''
   def run(self):
      interval_in_seconds = self.parent.interval / 1000.0
      def sleep():
            time.sleep(interval_in_seconds)

      sleep()
      try:
         while self.parent.alive:
            event = wx.PyEvent(self.parent.wx_id)
            event.SetEventType(wxEVT_THREAD_TIMER)
            wx.PostEvent(self.parent.parent, event)
            sleep()
      except:
         return # Just so it wouldn't raise an error when wx is shutting down