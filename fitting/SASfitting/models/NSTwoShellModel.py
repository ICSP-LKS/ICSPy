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

from models.AuNSModel import AuNSModel

class NSTwoShellModel(AbstractModel):
    
    def __init__(self,pars,name="NSTwoShellModel",model_info='core_multi_shell'):
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
        num=[]
        #calculate number of spheres
        pars={'scale':self.pars['scale'],
              'radius':self.pars['radius']}
        if 'core_shell' in self.model_info.split('+')[0]:
            pars['thickness'] = self.pars['thickness1']+self.pars['thickness2']
        num.append(AuNSModel(pars=pars).calc_num()[0])
        return(num)
        
    def calc_conc(self):
        pass
    
    def calc_volume(self):
        pass
    

# Testcases. to be implemented in unittests
if __name__ == '__main__':
    
    pars = { 'n':2,
             'scale': 3.281e-4, #<-
             'sld_core': 125,
             'sld_solvent': 9.45,
             'radius': 100, #<-
             'radius_pd': 0.2,
             'sld1':20,
             'sld2':70,
             'thickness1':50,
             'thickness2':20,
            }
    
    data = r"..\\..\\unittests\\data\\testdata_AuNRNS.txt"
    
    fitModel = NSTwoShellModel(pars)
    fitModel.plot(data)
    print(fitModel.calc_num())
    
    pars = { 'n':4,
             'scale': 3.281e-4, #<-
             'sld_core': 125,
             'sld_solvent': 9.45,
             'radius': 100, #<-
             'radius_pd': 0.2,
             'sld1':20,
             'sld2':70,
             'thickness1':50,
             'thickness2':20,
             'sld3':20,
             'sld4':70,
             'thickness3':50,
             'thickness4':20,
            }
    
    data = r"..\\..\\unittests\\data\\testdata_AuNRNS.txt"
    
    fitModel = NSTwoShellModel(pars)
    fitModel.plot(data)
    print(fitModel.calc_num())
        
        