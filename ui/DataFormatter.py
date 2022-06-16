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

#import handler
    
import configparser

class DataFormatter(QDialog):
    
    def __init__(self,Dir,root=None,):
        
        QWidget.__init__(self,root)
        
        self.closed = PyQt5.QtCore.pyqtSignal
        self.setModal(True)
        self.handler_dict = {}
        
        self.resize(500,180)
        self.setWindowTitle('Data Formatter')
        self.root = root
        #self.root.hide()
        self.main_layout = QGridLayout(self)        
        self.main_layout.addWidget(QLabel('config: ',self),0,0,1,1)
        
        self.config = configparser.RawConfigParser()
        self.config.read('../'+os.name+'_config.cfg')
        self.handler_list = self.config.items('handler')       
        
        self.config_dd = QComboBox(self)
        self.main_layout.addWidget(self.config_dd,0,1,1,1)
        for iHandler in self.handler_list:
            self.config_dd.addItem(iHandler[0])
        
        self.finish_button = QPushButton(self,text='finish')
        self.finish_button.setSizeIncrement(1,1)      
        self.finish_button.clicked.connect(self.finish)
   
        self.main_layout.addWidget(self.finish_button,2,2,1,1)        

        self.show()

    def update(self):
        self.centerCenterWidget = self.handler_dict[self.config_dd.currentText()]        
      
    def finish(self):
        
        sys.path.append(self.config.get('dirs','home_directory'))
        import handler.AutoHandler as auto
        import handler.EasyHandler as easy
        
def main():
        # Create an PyQT5 application object.
    
    a = QApplication(sys.argv)

        # The QWidget widget is the base class of all user interface objects in PyQt5.    
    centralWidget = QWidget()
    tree = DataFormatter('../__testcase/Testdaten/Ordner1/testdata1.dat',centralWidget)
    tree.setFixedSize(395,395)
    

        # Set window title
    tree.setWindowTitle("DirTreeWidget")

        # Show window
    tree.show()

    sys.exit(a.exec_())


if __name__ == "__main__":
    main()
