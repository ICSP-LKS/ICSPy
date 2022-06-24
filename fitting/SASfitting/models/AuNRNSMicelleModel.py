# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 14:00:33 2018

@author: ZechT
"""

import os 
import numpy as np
import matplotlib.pyplot as plt
from models.AbstractModel import AbstractModel
from sasmodels.core import load_model, load_model_info, build_model
from sasmodels.bumps_model import Model, Experiment
from sasmodels.data import load_data, plot_data

from models.AuNRModel import AuNRModel
from models.MicelleModel import MicelleModel
from models.AuNSModel import AuNSModel


class AuNRNSMicelleModel(AbstractModel):
    
    def __init__(self,pars,name="AuNRNSMicelle",model_info='core_shell_sphere+core_shell_cylinder+core_shell_ellipsoid@hayter_msa'):
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
        print(self.pars)
        model = Model(self.kernel,**self.pars)
        data = load_data(data)
        Experiment(data,model=model).plot()

    def calc_num(self):
        
        num = []
        
        #calculate number of micelles
        if 'ellipsoid' in self.model_info:
            num.append(MicelleModel(pars=self.pars,model_info='core_shell_ellipsoid@hayter_msa').calc_num()[0])
        elif 'sphere' in self.model_info:
            num.append(MicelleModel(pars=self.pars,model_info='core_shell_sphere@hayter_msa').calc_num()[0])
        
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
    plt.close('all')
    pars = { 'background': 0.0751, #<-
         'A_scale': 3.281e-20, #<-
         'A_sld_core': 4.502,
         'A_sld_shell': -.375,
         'A_sld_solvent': 6.34,
         'A_radius':156.91, #<-
         'A_radius_pd': 0.2,
         'A_thickness': 32, 
         'B_scale': 4.8906586e-20, #<-
         'B_sld_core': 4.502,
         'B_sld_shell': -.375,
         'B_sld_solvent': 6.34,
         'B_radius': 86.428, #<-
         'B_radius_pd': 0.2,
         'B_thickness': 32, 
         'B_length':838.84, #<-
         'B_length_pd': 0.2,        
         'radius_equat_core':  17.6, 
         'x_core': 1.9899, #<-
         'thick_shell': 7,
         'thick_shell_pd':0.45,
         'x_polar_shell': 1,
         'sld_core': -.375,
         'sld_shell': 1.03,
         'sld_solvent': 6.34,
         'volfraction': 0.039948, #<- 
         'charge': 28.068, #<-
         'temperature': 308,
         'concentration_salt': 6.94e-4, #<-
         'dielectconst': 71.08}   
    
     
    data = r"..\\..\\..\\unittests\\data\\testdata_MicellelowQ.txt"
    
    fitModel = AuNRNSMicelleModel(pars)
    fitModel.plot(data)
    str_out = ""
    str_out += fitModel.write_model()
    str_out += fitModel.write_fittedvars({'charge':[0,100],'volfraction':[0,0.7],'x_core':[1,5],'concentration_salt':[1e-8,1e-1]})
    temp,Exp1 = fitModel.write_experiment(data)
    str_out += temp
    print(str_out)
    print(Exp1)
    pars = { 'background': 0.0751, #<-    
            'A_scale': 3.281e-08, #<-
         'A_sld_core': 4.502,
         'A_sld_shell': -.375,
         'A_sld_solvent': 6.34,
         'A_radius':156.91, #<-
         'A_radius_pd': 0.2,
         'A_thickness': 32, 
         'B_scale': 4.8906586e-06, #<-
         'B_sld_core': 4.502,
         'B_sld_shell': -.375,
         'B_sld_solvent': 6.34,
         'B_radius': 86.428, #<-
         'B_radius_pd': 0.2,
         'B_thickness': 32, 
         'B_length':838.84, #<-
         'B_length_pd': 0.2,        
         'radius_equat_core':  17.6, 
         'x_core': 1.9899, #<-
         'thick_shell': 7,
         'thick_shell_pd':0.45,
         'x_polar_shell': 1,
         'sld_core': -.375,
         'sld_shell': 1.03,
         'sld_solvent': 6.34,
         'volfraction': 0.039948, #<- 
         'charge': 28.068, #<-
         'temperature': 308,
         'concentration_salt': 5.94e-10, #<-
         'dielectconst': 71.08}
    fitModel.pars=pars
    str_out = fitModel.write_model()
    print(str_out)
    print(fitModel.calc_num())
    
    fitModel.plot(r"..\\..\\..\\unittests\\data\\testdata_MicellelowQ.txt")
    