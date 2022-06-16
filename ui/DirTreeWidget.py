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

import configparser

import handler.DataItem as data
import ui.AskHandler as AskHandler

class DirTreeWidget(QTreeWidget):
    
    def __init__(self,root,directory=None):
        QTreeWidget.__init__(self)
        self.root = root
        
        self.pathFromItem_dict = {}
        self.data = {}
        self.choices = {}
        
        self.config = configparser.RawConfigParser()
        self.config.read(os.name+'_config.cfg')
        self.home = self.config.get('dirs','home_directory')
        self.icon_directory = self.config.get('dirs','icon_directory')
        self.setHeaderLabel("")
        
        self.file_icon = QIcon(self.home+self.icon_directory+'File-64.png')
        self.folder_icon = QIcon(self.home+self.icon_directory+'Folder-64.png')

        
        self.setAcceptDrops(True)
        
        #if directory!=None:
        #    self.addDirectory(directory)
        self.show()    
    
    def addDirectory(self,directory):
        #self.clear()
        self.directory=directory
        list_dir = []
        for iItem in os.walk(directory):
            list_dir.append(iItem)
        
        
        main_item = QTreeWidgetItem()
        main_item.setText(0,os.path.split(directory)[1])
        main_item.setIcon(0,self.folder_icon) 
        #main_item.setText(1,os.path.split(directory)[0])
        
        
        dict_temp = {}
        
        dict_temp[directory] = main_item
        
        type_dict = {}
                 
        for iItem in list_dir:
            for iFolder in iItem[1]:
                item = QTreeWidgetItem()
                item.path = os.path.join(iItem[0],iFolder)
                item.setText(0,iFolder)
                item.setIcon(0,self.folder_icon)
                dict_temp[os.path.join(iItem[0],iFolder)]=item
                dict_temp[iItem[0]].addChild(item)
            for iFile in iItem[2]:
                item = data.DataItem()
                item.setText(0,iFile)
                item.setIcon(0,self.file_icon)
                dict_temp[iItem[0]].addChild(item)
                name = iFile.split('.')
                if name[-1] not in type_dict:
                    type_dict[name[-1]] = []
                type_dict[name[-1]].append(item)
                item.path=os.path.join(iItem[0],iFile)
        
        print(type_dict)
        temp = AskHandler.AskHandler(self,type_dict.keys())
        #temp.send.connect(self.addChoices)
        temp.exec()

        print(self.choices)
        for i,iChoices in enumerate(self.choices):
            print(iChoices)
            for jData in type_dict[iChoices]:
                item = jData
                item.handler = self.choices[iChoices]
                self.data[item.path] = item 
                         
        self.addTopLevelItem(main_item)
        self.choices = {}
        del dict_temp
        
        for iData in self.data:

            self.data[iData].readData()
                

    #only used to get the handler types from askhandler, do not use in other circumstances, SLOT!!!!
    def addChoices(self,choices):
        self.choices=choices
        
        
    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls:            
            e.accept()            
        else:
            e.ignore()
    
    def dropEvent(self,e):
        for iUrl in e.mimeData().urls():
            print(iUrl.path())
            if os.name == 'nt':
                self.addDirectory(iUrl.path().strip('/'))
            else:
                self.addDirectory(iUrl.path())
        
    def dragMoveEvent(self,e):
        pass

    def get_ItemPath(self,item):
        path=item.text(0)
        parent=item.parent()
        while(hasattr(parent.parent(),'text')):
            path=parent.text(0)+'/'+path
            parent=parent.parent()
        path=self.directory+'/'+path
        return(path)

    def get_selectedPaths(self):
        selected=self.selectedItems()
        paths=[]
        for i in range(len(selected)):
            paths.append(selected[i].path)
        return(paths)
    
def main():
        # Create an PyQT5 application object.
    a = QApplication(sys.argv)

        # The QWidget widget is the base class of all user interface objects in PyQt5.    
    centralWidget = QWidget()
    os.chdir('../')
    tree = DirTreeWidget(centralWidget,r"../__testcase")
    tree.setFixedSize(395,395)
    

        # Set window title
    tree.setWindowTitle("DirTreeWidget")

        # Show window
    tree.show()

    sys.exit(a.exec_())


if __name__ == "__main__":
    main()
