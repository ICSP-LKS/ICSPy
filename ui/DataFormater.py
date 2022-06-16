# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 14:33:12 2015

@author: tobias
"""

import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
import PyQt5

#import handler
    
import configparser

class DataFormatter(QDialog):
    
    def __init__(self,root=None):
        
        QWidget.__init__(self,root)
        
        self.closed = PyQt5.QtCore.pyqtSignal
        self.setModal(True)
        self.handler_dict = {}
        
        self.resize(500,180)
        self.setWindowTitle('Data Formatter')
        self.root = root
        #self.root.hide()
        self.main_layout = QGridLayout(self)        
        self.main_layout.addWidget(QLabel('config: ',self),0,0,1,2)        
        dir_button1 = QPushButton(self,text='path')
        
        self.config = configparser.RawConfigParser()
        self.config.read('../'+os.name+'_config.cfg')
        self.handler_list = self.config.items('handler')
        
        self.config_dd = QComboBox(self)
        self.main_layout.addWidget(self.config_dd,1,1,1,1)
        
        self.finish_button = QPushButton(self,text='finish')
        self.finish_button.setSizeIncrement(1,1)
        
        #self.finish_button.
        #self.workdir_reader = QLineEdit(self)
        #self.workdir_reader.setText(self.cfg.get('Directories','working_directory'))
        
        
        #self.main_layout.addWidget(self.workdir_reader,1,1,1,1)
        #self.main_layout.addWidget(dir_button1,1,2,1,1)

        #self.main_layout.addWidget(self.finish_button,4,1,1,1)
        
        #self.main
        #button.show()    
        
        #def work_directory():
        #    self.ask_directory(self.workdir_reader)
        #def save_directory():
        #    self.ask_directory(self.savedir_reader)
            
        #self.connect(dir_button1, SIGNAL('clicked()'), work_directory)
        #self.connect(dir_button2, SIGNAL('clicked()'), save_directory)
        #self.connect(self.finish_button, SIGNAL('clicked()'), self.finish)
        
        self.show()



                
#    def finish(self):
#        
#        work_dir=self.workdir_reader.text()
#        save_dir=self.savedir_reader.text()
#        
#        if os.path.isdir(work_dir) and os.path.isdir(save_dir): 
#            self.cfg.set('Directories','working_directory',work_dir)
#            self.cfg.set('Directories','saving_directory',save_dir)
#            with open('setup.cfg', 'wb') as configfile:
#                self.cfg.write(configfile)
#            try:
#                #self.root.set_workingDir(work_dir)
#                #self.root.set_savingDir(save_dir)
#                
#                self.is_set=True
#                self.destroy()
#                self.emit(SIGNAL('closed()'))                
#            except:
#                print 'second'
#                self.error()
#        else:
#            print 'first'
#            self.error()
#            
#    def error(self):
#        message = QErrorMessage(self)
#        message.setWindowTitle('I am Error')
#        message.showMessage('no valid directory chosen!')
        
        
def main():
        # Create an PyQT5 application object.
    a = QApplication(sys.argv)

        # The QWidget widget is the base class of all user interface objects in PyQt5.    
    centralWidget = QWidget()
    tree = DataFormatter(centralWidget,r"../__testcase")
    tree.setFixedSize(395,395)
    

        # Set window title
    tree.setWindowTitle("DirTreeWidget")

        # Show window
    tree.show()

    sys.exit(a.exec_())


if __name__ == "__main__":
    main()
