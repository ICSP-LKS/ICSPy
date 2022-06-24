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

from models.AuNRModel import AuNRModel
from models.AuNSModel import AuNSModel

class AuNRNSModel(AbstractModel):
    
    def __init__(self,pars,name="AuNRNS",model_info='sphere+cylinder'):
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

        num = []
        
        #calculate number of spheres
        pars={'scale':self.pars['A_scale'],
              'radius':self.pars['A_radius']}
        if 'core_shell' in self.model_info.split('+')[0]:
            pars['thickness'] = self.pars['A_thickness']
        num.append(AuNSModel(pars=pars).calc_num()[0])
        
        #calculate number of rods
        pars={'scale':self.pars['B_scale'],
                'radius':self.pars['B_radius'],
                'length':self.pars['B_length']}
        if 'core_shell' in self.model_info.split('+')[1]:
            pars['thickness'] = self.pars['A_thickness']
        num.append(AuNRModel(pars=pars).calc_num()[0])
        
        return(num)
        
    def calc_conc(self):
        pass
    
    def calc_volume(self):
        pass
    

# Testcases. to be implemented in unittests
if __name__ == '__main__':
    
    pars = { 'A_scale': 3.281e-8, #<-
             'A_sld': 125,
             'A_sld_solvent': 9.45,
             'A_radius': 156.91, #<-
             'A_radius_pd': 0.2,
             'B_scale': 4.8906586e-06, #<-
             'background': 0.015, #<-
             'B_sld': 125,
             'B_sld_solvent': 9.45,
             'B_radius': 86.428, #<-
             'B_radius_pd': 0.2,
             'B_length':838.84, #<-
             'B_length_pd': 0.2,
            }
    
    data = r"..\\..\\unittests\\data\\testdata_AuNRNS.txt"
    
    fitModel = AuNRNSModel(pars)
    fitModel.plot(data)
        
        