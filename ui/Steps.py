# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 00:15:10 2017

@author: matthias
"""


## kann nur mit python3 geöffnet werden, nicht mit python.
import numpy as np
import matplotlib.pyplot as plt
import sys
import PyQt5
from PyQt5.QtWidgets import QWidget, QCheckBox, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLabel

from PyQt5.QtCore import Qt



class Loop(QWidget):      
    def __init__(self,root=None):
        QWidget.__init__(self)
        self.root=root
        self.number=0
        self.Steps=[]
        self.initUI()
        
    def initUI(self):
	
        self.MainHBox=QHBoxLayout(self)
        self.NumberLabel=QLabel('  ')
        self.MainHBox.addWidget(self.NumberLabel)
        self.StepBox=QVBoxLayout()
        self.StepBox.setSpacing(0)
        self.MainHBox.addLayout(self.StepBox)
        self.addStep()
        self.StepBox.addStretch()
        
        self.setWindowTitle('Loop')
        self.show()

    def addStep(self):
        newStep=Step(self)
        self.StepBox.addWidget(newStep)
        self.Steps.append(newStep)

    def insertStep(self,number):
        newStep=Step(self)
        self.StepBox.insertWidget(number,newStep)
        self.Steps.insert(number,newStep)
        self.numerateSteps()

    def insertLoop(self,number):
        ILoop=LoopStep(self)
        self.StepBox.insertWidget(number,ILoop)
        self.Steps.insert(number,ILoop)
        self.numerateSteps()

    def numerateSteps(self):
        for i in range(len(self.Steps)):
            self.Steps[i].number=i+1
            self.Steps[i].NumberLabel.setText(str(i+1))

    def removeWidget(self,Widget):
        if len(self.Steps)>1:
            self.StepBox.removeWidget(Widget)
            Widget.hide()
            self.Steps.remove(Widget)
            del Widget
            self.numerateSteps()
            self.adjustSize()
            if self.root is not None:
                 self.root.adjustSize()
        else:
            pass


class Step(QWidget):
    def __init__(self, root):
        QWidget.__init__(self)
        self.root=root
        self.number=0
        self.HBox=QHBoxLayout(self)

        self.NumberLabel=QLabel(str(len(root.Steps)+1))

        self.StepLabel=QLabel('Abstract Step')

        self.AddStepButton=QPushButton('+')
        self.AddStepButton.clicked.connect(self.insertStep)
        textWidth = self.AddStepButton.fontMetrics().boundingRect(self.AddStepButton.text()).width()
        self.AddStepButton.setMaximumWidth(textWidth+15)

        self.AddLoopButton=QPushButton('add Loop')
        self.AddLoopButton.clicked.connect(self.insertLoop)

        self.RemoveButton=QPushButton('-')
        self.RemoveButton.clicked.connect(self.remove)
        textWidth = self.RemoveButton.fontMetrics().boundingRect(self.RemoveButton.text()).width()
        self.RemoveButton.setMaximumWidth(textWidth+15)
	
        self.HBox.addWidget(self.NumberLabel)
        self.HBox.addWidget(self.StepLabel)
        self.HBox.addStretch()
        self.HBox.addWidget(self.AddStepButton)
        self.HBox.addWidget(self.AddLoopButton)
        self.HBox.addWidget(self.RemoveButton)

    

    def addStep(self):
        self.root.addStep()

    def insertStep(self):
        self.root.insertStep(self.number)

    def addLoop(self):
        self.root.addDummyLoop()

    def insertLoop(self):
        self.root.insertLoop(self.number)
        
    def remove(self):
        self.root.removeWidget(self)
        del self

class LoopStep(Step):
    def __init__(self, root):
        Step.__init__(self, root)
        self.HBox.insertWidget(2,Loop(root=root))
        self.StepLabel.setText('Loop')

            
if __name__=='__main__':
    
    app=QApplication(sys.argv)
    ex = Loop()
    sys.exit(app.exec_())
