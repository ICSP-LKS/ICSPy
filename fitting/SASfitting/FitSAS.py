# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 14:00:33 2018

@author: ZechT
"""
import os

import subprocess
import json
import time
from string import Template
    

class fit():
    
    def __init__(self,Directory,File,tracking=False):
        
        if not os.path.isdir(Directory):
            raise Exception("{Dir} is not a valid directory.".format(Dir=Directory))
        self.directory = Directory       
        self.file = File         
        self.store = Directory+"\\fits_"+File
        self.pydir = Directory+"\\"+File+'.py'
        
        
    '''
    Compute function to start the bumps fitting process.
    Look up "https://bumps.readthedocs.io/en/latest/guide/fitting.html" for more information on the different options.
    When you want to use another fit algorithm like nelder mead (amobea) or differential evolution (de), please
    implement it by referring to the requirements of the fitting parameters given in the source above.
    '''
    def compute(self,algorithm='lm',steps=None,burn=None,samples=None,init='cov',pars=None):
        
        exceptionTemplate = Template('$Var is not defined or not a valid variable type ($Type).')
        bumpsString = 'bumps --fit='+algorithm+' '+str(self.pydir)+' --store="'+str(self.store)+'" --batch'
        
        if algorithm=='lm': #Least Squares Levenberg Marquardt Algorithm                 
            bumpsString+= ' --steps='+str(int(steps))
        
        elif algorithm=='dream': #Markov Chain Monte Carlo Algorithm, for final refinement of fit            
            bumpsString+= ' --samples='+str(int(samples))+' --burn='+str(int(burn))+' --parallel --init'+init
            if os.path.isdir(pars):
                bumpsString+= ' --pars='+pars            
        else:
            Warning("Algorithm not implemented in FitSAS.fit.compute()...")
        
        return subprocess(bumpsString)
        
    '''
    Function to parse the .err file generated by the bumps fitting library.
    Input:      -none
    Output:     -dictionary containing the fitted parameters
    '''
    def parse_err(self):
        def parsParams(directory):
            f = open(directory)
            Dicts = []
            for iLine in f.readlines():
                if '--' in iLine:
                    Dicts.append({})
                if " = " in iLine and not " in " in iLine:
                    Dicts[-1][iLine.split(' ')[0].split('.')[1]] = float(iLine.split(' ')[-1])
                elif " = " in iLine:                        
                    Dicts[-1][iLine.split(' ')[0].split('.')[1]] = float(iLine.split(' ')[2])
               
            return Dicts
        return(parsParams(self.store+r'\\'+self.file+'.err'))
    
    '''
    Function to parse the .par file generated by the bumps fitting library.
    Input:      -none
    Output:     -dictionary containing the fitted parameters
    '''    
    def parse_par(self):
        def parsParams(directory):
            f = open(directory)
            tempDict = {}
            for iLine in f.readlines():
                tempDict[iLine.split(' ')[0]] = float(iLine.split(' ')[1])
            return tempDict
        return(parsParams(self.store+r'\\'+self.file+'.par'))
        
    def gen_file(self,models,data,fittingVars,indices=[0,-1],additions=''):
              
        f = open(self.pydir,'w')        
        preamble="## -*- coding: utf-8 -*-\n\nimport sys,os\nsys.path.append(r'..\..\sasview\src')\nimport numpy as np\nfrom bumps.names import *\nimport matplotlib.pyplot as plt\nfrom sasmodels.core import load_model, load_model_info, build_model\n"
        preamble+="from sasmodels.bumps_model import Model, Experiment\nfrom sasmodels.data import load_data, plot_data\nfrom sasmodels.sasview_model import make_model_from_info\n"
        preamble+="from sasmodels.direct_model import call_kernel\n"
        f.write(preamble)
        #initialize sasmodels, parameters and fitting variables with ranges
        for i,iModel in enumerate(models):
            f.write(iModel.write_model())
            f.write(iModel.write_fittedvars(fittingVars[i]))
        #additions like depedencies or further restrictions on parameters
        f.write(additions)
        #define the expeirments to be fitted by bumps
        Exps = []  
        for i,iModel in enumerate(models):
            out,temp = iModel.write_experiment(data[i],indices)
            Exps.append(temp)
            f.write(out)
        #ending lines which are needed by bumps to start the fit    
        f.write("M = [")
        for iExp in Exps:                
            f.write(iExp)
        f.write("]\nproblem = FitProblem(M)\n")
        f.close()
        
    def gen_fileFC(self,fitContainer):
              
        f = open(self.pydir,'w')        
        preamble="## -*- coding: utf-8 -*-\n\nimport sys,os\nsys.path.append(r'..\..\sasview\src')\nimport numpy as np\nfrom bumps.names import *\nimport matplotlib.pyplot as plt\nfrom sasmodels.core import load_model, load_model_info, build_model\n"
        preamble+="from sasmodels.bumps_model import Model, Experiment\nfrom sasmodels.data import load_data, plot_data\nfrom sasmodels.sasview_model import make_model_from_info\n"
        preamble+="from sasmodels.direct_model import call_kernel\n"
        f.write(preamble)
        #initialize sasmodels, parameters and fitting variables with ranges
        self.gen_file(fitContainer.models,fitContainer.data,fitContainer.fittingVars,fitContainer.indices,fitContainer.additions)
    
class fitContainer():
    def __init__(self,models=[],data=[],fittingVars=[],indices=[0,-1],additions=''):
        self.models = models
        self.data = data
        self.fittingVars = fittingVars
        self.indices = indices
        self.additions = additions
        
        self.dict = {'models':self.models,
                         'data':self.data,
                         'fittingVars':self.fittingVars,
                         'indices':self.indices,
                         'additions':self.additions}
      
'''
Generate generic output .json and some standardized output message for every fit 
performed from .err and .par files generated from bumps.
Input:      -
            -
            -
            -
            -
            -
            -
Output      -
            -
'''
def generateOutput(name,fit_,models,data,percentage,ellapsed,current,additions=[]):    
    pars = [] 
    reviewFile = []
    try:
        print(name+' | ' +fit_.file+ ' || '+str(percentage)+
              '% finished | ellapsed time: '+str(ellapsed)+
              'min | computing time: '+str(current)+
              's | Results:')
        pars = fit_.parse_err()
        print(fit_.parse_par())
        for iAdd in additions:
            pars
        
        reviewFile = {}
        reviewFile['models'] = {}
        reviewFile['data'] = {}
        reviewFile['names'] = []
        reviewFile['parameters'] = {}
        for i,iPars in enumerate(pars):
            reviewFile['data'][models[i].name]=data[i]
            reviewFile['parameters'][models[i].name] = fit_.parse_err()[i]
            reviewFile['names'].append(models[i].name)
            models[i].pars=fit_.parse_err()[i]
            reviewFile['models'][models[i].name] = models[i].compute(data[i]).tolist()

        with open(fit_.pydir.split('.')[0]+r'.json','w') as f:
            json.dump(reviewFile,f,sort_keys=True, indent=4)
    except:
        print(name+' | ' +fit_.file+ ' || '+str(percentage)+
              '% finished | ellapsed time: '+str(ellapsed)+
              'min | computing time: '+str(current)+
              's | fit failed ....')
        reviewFile = None
    return(pars,reviewFile)
    