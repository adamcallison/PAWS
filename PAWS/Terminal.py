#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Tkinter Terminal Application

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                      Python Adventure Writing System                          #
#                             Tkinter Terminal                                 #
#                     Originally Written by Roger Plowman (c) 2008             #
#                     Converted to Tkinter by Adam, 2026                        #
#                                                                               #
# The C="""...""" statements scattered throughout this source code are actually #
# a work-around for Python's lack of block comments. Notepad++ can only fold    #
# block comments, not a series of comment lines. Using C="""...""" doesn't      #
# increase PAWS memory footprint, although it does have a tiny impact           #
# on loading time.                                                              #
#                                                                               #
C="""
  This module contains the skeleton of the terminal program, basically the
  main loop code and a few references.

  Written By: Roger Plowman (original), Adam (Tkinter port)
  Written On: 01/20/2008 (original), 2026 (Tkinter port)
  """
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

from . import TerminalFrame

def main():
    application = TerminalFrame.TFrame()
    application.mainloop()

if __name__ == '__main__':
    main()