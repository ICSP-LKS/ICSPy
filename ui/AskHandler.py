# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 14:33:12 2015

@author: tobias
"""

import os,sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import PyQt5

import configparser
    
class AskHandler(QDialog):
    
    def __init__(self,root,d_types):
        
        QDialog.__init__(self)
        self.root = root        
        self.closed = PyQt5.QtCore.pyqtSignal
        self.setModal(True)
        
        self.send = PyQt5.QtCore.pyqtSignal(dict)

        self.config = configparser.RawConfigParser()
        self.config.read(os.name+'_config.cfg')
        self.home = self.config.get('dirs','home_directory')
        
        self.handlers = []
        self.getHandlerTypes()
        
        #self.handlers = ['auto','sasdata','temp']
        
        self.options = d_types
        
        self.choices = {}
        
        self.setWindowTitle('Handler')
        self.root = root
        #self.root.hide()
        self.main_layout = QGridLayout(self)  
        
        self.finish_button = QPushButton(self,text='finish')
        self.finish_button.setSizeIncrement(1,1)
        #print(self.handlers)

        for i,iTyp in enumerate(d_types):
            self.add_option(iTyp,i)
        
        self.main_layout.addWidget(self.finish_button,len(d_types)+1,3,1,1)
 
        self.finish_button.clicked.connect(self.finish)
        #self.exec()

    def __del__(self):        
        pass
    
    def add_option(self,option,pos):
              
        self.main_layout.addWidget(QLabel('Choose Data handler for "'+option+'":',self),pos,1,1,1)        
        box = QComboBox(self)
        box.addItems(self.handlers)
        self.choices[option] = box
        self.main_layout.addWidget(box,pos,3,1,1)    
            
    def finish(self):
        opt = {}
        for i,iTyp in enumerate(self.choices):
            opt[iTyp] = self.choices[iTyp].currentText()
        #self.send.emit(opt)
        #print('choices in askhandler: ')
        #self.choices
        self.root.addChoices(opt)    
        
        self.done(QDialog.Accepted)
        
    def getHandlerTypes(self):
        list_dir = []
        for iItem in os.walk('handler/reader/'):
            list_dir.append(iItem)
        print(list_dir)
        for iItem in list_dir:
            for iFile in iItem[2]:
                self.handlers.append(iFile.split('_')[0])
        
        
def main():
        # Create an PyQT5 application object.
    a = QApplication(sys.argv)
    os.chdir('../')
        # The QWidget widget is the base class of all user interface objects in PyQt5.    
    centralWidget = QWidget()
    tree = AskHandler(centralWidget,['txt','sas','temp'])
    #tree.setFixedSize(395,395)
    

        # Set window title
    tree.setWindowTitle("AskHandler")

        # Show window
    tree.show()

    sys.exit(a.exec_())


if __name__ == "__main__":
    main()