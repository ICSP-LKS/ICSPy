# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 14:00:33 2018

@author: ZechT
"""

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

class MicelleModel(AbstractModel):
    
    def __init__(self,pars,name="Micelle",model_info='core_shell_ellipsoid@hayter_msa'):
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
        def calcMicelleNum(volfrac,R,x,t): #nanoparticle per liter
            return(volfrac/(4/3*np.pi*((R+t)*1e-9)**2*((x*R+t)*1e-9)))
        
        num = []
        if "ellipsoid" in self.model_info:
            num.append(calcMicelleNum(self.pars['volfraction'],self.pars['radius_equat_core'],self.pars['x_core'],self.pars['thick_shell']))
        elif "sphere" in self.model_info:
            num.append(calcMicelleNum(self.pars['volfraction'],self.pars['radius'],self.pars['radius'],self.pars['thickness']))
        return(num)
        
    def calc_conc(self):
        pass
    
    def calc_volume(self):
        pass
    
#    def write_model(self):
#        super(AbstractModel,self).write_model()
#        
#    def write_dependency(self,modelName,params):
#        super(AbstractModel,self).write_dependency(modelName,params)
#        
#    def write_fittedvars(self,Dict):
#        super(AbstractModel,self).write_fittedvars(Dict)
#        
#    def write_experiment(self,data,indices=[0,-1]):
#        super(AbstractModel,self).write_experiment(data,indices)

    

if __name__ == '__main__':
    
    pars = { 'background': 0.0751, #<-         
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
    
    data = r"..\\testcase\\data\\testdata_Micelle.txt"
    
    fitModel = MicelleModel(pars)
    fitModel.plot(data)
    str_out = ""
    str_out += fitModel.write_model()
    str_out += fitModel.write_fittedvars({'charge':[0,100],'volfraction':[0,0.7],'x_core':[1,5],'concentration_salt':[1e-8,1e-1]})
    temp,Exp1 = fitModel.write_experiment(data)
    str_out += temp
    print(str_out)
    print(Exp1)
    pars = { 'background': 0, #<-         
         'radius_equat_core':  0, 
         'x_core': 0, #<-
         'thick_shell': 0,
         'thick_shell_pd':0,
         'x_polar_shell': 0,
         'sld_core': 0,
         'sld_shell': 0,
         'sld_solvent': 0,
         'volfraction': 0, #<- 
         'charge': 0, #<-
         'temperature': 0,
         'concentration_salt': 0, #<-
         'dielectconst': 0}
    fitModel.pars=pars
    str_out = fitModel.write_model()
    print(str_out)