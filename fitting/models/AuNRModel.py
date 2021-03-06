# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 14:00:33 2018

@author: ZechT
"""

import os 
import numpy as np
from models.AbstractModel import AbstractModel
from sasmodels.core import load_model, load_model_info, build_model
from sasmodels.bumps_model import Model, Experiment
from sasmodels.data import load_data, plot_data

class AuNRModel(AbstractModel):
    
    def __init__(self,pars,name="AuNR",model_info='cylinder'):
        AbstractModel.__init__(self,pars,name,model_info)
        #self.pars=pars  #dict
        #self.name=name  #string
        #self.model_info = 'sphere+cylinder'
        self.kernel=build_model(load_model_info(self.model_info))
        
    def compute(self,data): 
        model = Model(self.kernel,**self.pars)
        data = load_data(data)
        Exp = Experiment(data,model=model)
        theory = np.array([data.x,Exp.theory()])
        return(theory)
        
    def plot(self,data):        
        model = Model(self.kernel,**self.pars)
        data = load_data(data)
        Experiment(data,model=model).plot()

    def calc_num(self):
        def calcRodNum(volfrac,R,L,unit='angstrom'): #nanoparticle per liter
            if unit=='angstrom':
                return(volfrac/(np.pi*(R*1e-10)**2*(L*1e-10)))
            else:
                return(volfrac/(np.pi*(R*1e-9)**2*(L*1e-9)))
        
        num = []
        num.append(calcRodNum(self.pars['scale'],self.pars['radius'],self.pars['length']))
        return(num)
        
    def calc_conc(self):
        pass
    
    def calc_volume(self):
        pass
    

if __name__ == '__main__':
    
    pars = {
             'background': 0.015, #<-
             'sld': 125,
             'sld_solvent': 9.45,
             'radius': 86.428, #<-
             'radius_pd': 0.2,
             'length':838.84, #<-
             'length_pd': 0.2,
            }
    
    data = r"..\\testcase\\data\\testdata_AuNRNS.txt"
    
    fitModel = AuNRModel(pars)
    fitModel.plot(data)
        
        