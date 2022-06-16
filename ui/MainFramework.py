# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 18:30:32 2017

@author: ZechT
"""

import os, sys

import numpy as np

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import ui.DirTreeWidget as DirTreeWidget
import ui.Steps as Steps
#from function.routine import routine

import configparser

class MainFramework(QMainWindow):
    
    
    def __init__(self,parent=None):
        QMainWindow.__init__(self, parent)        
        
        self.config = configparser.RawConfigParser()
        self.config.read(os.name+'_config.cfg')
        self.home = self.config.get('dirs','home_directory')
        self.icon_directory = self.config.get('dirs','icon_directory')
        print(self.home)

        self.setMinimumSize(300,250)
        self.root = QWidget(self)        
        self.root.show()    
        
        self.tool_tab_dict = {}
        self.working_dir=self.config.get('dirs','working_directory')
        self.saving_dir=self.config.get('dirs','saving_directory')
        
        
        #self.settings = QSettings("last_session", "PloPoV0.1")
        
        

