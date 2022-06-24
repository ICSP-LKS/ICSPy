# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 14:00:33 2018

@author: ZechT
"""
import os,sys
import numpy as np
sys.path.append(r"C:\Users\ZechT\FAUbox\Auswertung\Software\ICSPy")
from models.AbstractModel import AbstractModel
from sasmodels.core import load_model, load_model_info, build_model
from sasmodels.bumps_model import Model, Experiment
from sasmodels.data import load_data, plot_data

class AuNSModel(AbstractModel):
    
    def __init__(self,pars,name="AuNS",model_info='sphere'):
        AbstractModel.__init__(self,pars,name,model_info)
        
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
        def calcSphereNum(volfrac,R,T=0): #nanoparticle per liter
            return(volfrac/(4/3*np.pi*(R*1e-9)**3))
        num=[]
        if 'core_shell' in self.model_info:
            num.append(calcSphereNum(self.pars['scale'],self.pars['radius'],self.pars['thickness']))
        else:
            num.append(calcSphereNum(self.pars['scale'],self.pars['radius']))
        return(num)
        
    def calc_conc(self):
        pass
    
    def calc_volume(self):
        pass
    

# Testcases. to be implemented in unittests
if __name__ == '__main__':
    
    pars = { 'scale': 3.281e-8, #<-
             'sld': 125,
             'sld_solvent': 9.45,
             'radius': 156.91, #<-
             'radius_pd': 0.2,
             'background': 0.015, #<-
            }
    
    data = r"..\\..\\unittests\\data\\testdata_AuNRNS.txt"
    
    fitModel = AuNSModel(pars)
    fitModel.plot(data)
        
        