# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 14:00:33 2018

@author: ZechT
"""


class AbstractModel():
    def __init__(self,pars,name,model_info):
        self.name = name
        self.model_info = model_info
        self.pars = pars
     
    def write_model(self):
        str_out="model_info = load_model_info('"+self.model_info+"')\n"
        str_out+="model_info.name = '"+self.name+"Model'\n"
        str_out+="kernel = build_model(model_info) #build_model makes kernel not model\n"
        str_out+="pars"+self.name+"="+str(self.pars)+"\n"
        str_out+=self.name+" = Model(kernel,**pars"+self.name+")\n"
        return(str_out)
        
    def write_dependency(self,modelName,params):
        str_out=""
        str_out+=self.name+"."+params[0]+" = "
        str_out+=modelName+"."+params[1]+"\n"        
        return(str_out)
        
    def write_fittedvars(self,Dict):
        str_out=""
        for iParam in Dict:
            str_out+=self.name+"."+iParam+".range("+str(Dict[iParam][0])+','+str(Dict[iParam][1])+")\n"
        return(str_out)
        
    def write_experiment(self,data,indices=[0,-1]):
        str_out=""
        dataname = self.name+"Data"
        str_out=dataname+"=load_data(r'"+data+"')\n"
        str_out+=dataname+".qmin="+dataname+".x["+str(indices[0])+"]\n"
        str_out+=dataname+".qmax="+dataname+".x["+str(indices[1])+"]\n"
        str_out+=dataname+".x="+dataname+".x["+str(indices[0])+":"+str(indices[1])+"]\n"
        str_out+=dataname+".dx="+dataname+".dx["+str(indices[0])+":"+str(indices[1])+"]\n"
        str_out+=dataname+".y="+dataname+".y["+str(indices[0])+":"+str(indices[1])+"]\n"
        str_out+=dataname+".dy="+dataname+".dy["+str(indices[0])+":"+str(indices[1])+"]\n"
        str_out+=dataname+".mask="+dataname+".mask["+str(indices[0])+":"+str(indices[1])+"]\n"
        str_out+=self.name+"Exp = Experiment(data="+dataname+",model="+self.name+")\n"
        return(str_out,self.name+"Exp")
        
                
    def get_pars(self):
        return(self.pars)
    
    def set_pars(self,pars):
        self.pars=pars
    
    def get_name(self):
        return(self.name)