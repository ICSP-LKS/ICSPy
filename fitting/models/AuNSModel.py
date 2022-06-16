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
        def calcSphereNum(volfrac,R): #nanoparticle per liter
            return(volfrac/(4/3*np.pi*(R*1e-9)**3))
        def calcRodNum(volfrac,R,L): #nanoparticle per liter
            return(volfrac/(np.pi*(R*1e-9)**2*(L*1e-9)))
        
        num = []
        num.append(calcSphereNum(self.pars['A_scale'],self.pars['A_radius']))
        #num.append(calcRodNum(self.pars['B_scale'],self.pars['B_radius'],self.pars['B_length']))
        return(num)
        
    def calc_conc(self):
        pass
    
    def calc_volume(self):
        pass
    

if __name__ == '__main__':
    
    pars = { 'scale': 3.281e-8, #<-
             'sld': 125,
             'sld_solvent': 9.45,
             'radius': 156.91, #<-
             'radius_pd': 0.2,
             'background': 0.015, #<-
            }
    
    data = r"..\\testcase\\data\\testdata_AuNRNS.txt"
    
    fitModel = AuNSModel(pars)
    fitModel.plot(data)
        
        