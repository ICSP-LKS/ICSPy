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


class Step(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.initUI()

    def initUI(self):
        pass
       
class Loop(QWidget):
    def __init__(self):
        QWidget.__init__(self)
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
        self.addDummyStep()
        self.StepBox.addStretch()
        
        self.setWindowTitle('Loop')
        self.show()

    def addDummyStep(self):
        Step=DummyStep(self)
        self.StepBox.addWidget(Step)
        self.Steps.append(Step)

    def insertStep(self,number):
        Step=DummyStep(self)
        self.StepBox.insertWidget(number,Step)
        self.Steps.insert(number,Step)
        self.numerateSteps()

    def addDummyLoop(self):
        DummyLoop=Loop()
        self.StepBox.addWidget(DummyLoop)
        self.Steps.append(DummyLoop)

    def insertLoop(self,number):
        ILoop=Loop()
        self.StepBox.insertWidget(number,ILoop)
        self.Steps.insert(number,ILoop)
        self.numerateSteps()

    def numerateSteps(self):
        for i in range(len(self.Steps)):
            self.Steps[i].number=i+1
            self.Steps[i].NumberLabel.setText(str(i+1))

    def removeWidget(self,Widget):
        self.StepBox.removeWidget(Widget)
        Widget.hide()
        self.Steps.remove(Widget)
        del Widget
        self.numerateSteps()


class DummyStep(Step):
    def __init__(self, root):
        QWidget.__init__(self)
        self.root=root
        self.number=0
        self.HBox=QHBoxLayout(self)

        self.NumberLabel=QLabel(str(len(root.Steps)+1))

        self.AddStepButton=QPushButton('add Step')
        self.AddStepButton.clicked.connect(self.insertStep)

        self.AddLoopButton=QPushButton('add Loop')
        self.AddLoopButton.clicked.connect(self.insertLoop)

        self.RemoveButton=QPushButton('remove')
        self.RemoveButton.clicked.connect(self.remove)
	
        self.HBox.addWidget(self.NumberLabel)
        self.HBox.addStretch()
        self.HBox.addWidget(self.AddStepButton)
        self.HBox.addWidget(self.AddLoopButton)
        self.HBox.addWidget(self.RemoveButton)

    

    def addStep(self):
        self.root.addDummyStep()

    def insertStep(self):
        self.root.insertStep(self.number)

    def addLoop(self):
        self.root.addDummyLoop()

    def insertLoop(self):
        self.root.insertLoop(self.number)
        
    def remove(self):
        self.root.removeWidget(self)
            
if __name__=='__main__':
    
    app=QApplication(sys.argv)
    ex = Loop()
    sys.exit(app.exec_())
