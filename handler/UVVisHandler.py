# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 21:52:37 2018

@author: ZechT
"""

def createUVVisDataset(dataID,Dirs):
    import pandas as pd
    import numpy as np
    
    #columns of pandas table
    ID = []
    LAMBDA = []
    INT = []
    CORR = []
    I400 = []
    LSPR = []
    TSPR = []
    NP = []
    LSPR_SIGMA = []
    LSPR_INT = []
    TSPR_SIGMA = []
    TSPR_INT = []
    NP_INT = []
    NP_SIGMA = []
    FIT = []
    
    #set data for pandas columns from parameter lists
    for i,iData in enumerate(dataID):
        ID.append(iData)
        LAMBDA.append(np.array([]))
        INT.append(np.array([]))
        CORR.append(0.0)
        I400.append(0.0)
        LSPR.append(0.0)
        TSPR.append(0.0)
        NP.append(0.0)
        NP_INT.append(0.0)
        NP_SIGMA.append(0.0)
        LSPR_SIGMA.append(0.0)
        LSPR_INT.append(0.0)
        TSPR_SIGMA.append(0.0)
        TSPR_INT.append(0.0)
        FIT.append(np.array([]))
    
    super_data = pd.DataFrame({'ID':ID,
                              'LAMBDA':LAMBDA,
                              'INT':INT,
                              'CORR':CORR,
                              'I400':I400,
                              'LSPR':LSPR,
                              'LSPR_SIGMA':LSPR_SIGMA,
                              'LSPR_INT':LSPR_INT,
                              'TSPR':TSPR,
                              'TSPR_SIGMA':TSPR_SIGMA,
                              'TSPR_INT':TSPR_INT,
                              'NP':NP,
                              'NP_INT':NP_INT,
                              'NP_SIGMA':NP_SIGMA,
                              'FIT':FIT})
    # function to take mean over all rows (repeated measurements) of the UV-vis spectrum
    def create_df(List):
        new = pd.concat(List, ignore_index=True)
        a = new.index.values
        idx = np.array([a, a],dtype=float).T.flatten()[:len(a)]
        idx
        new = new.groupby(idx).mean()
        del new['nm']
        new = new.astype(float)
        #new=new.rename({0:'1.',1:'2.',2:'3.'})
        return new.transpose()
    super_data = super_data.set_index('ID')
    #super_data = super_data.drop(['toz114hx025'])
    
    # get intensity and wavelength data for every dataset
    for i,iData in enumerate(super_data.index.values):
        
        tp = []
        
        try:
            #print(iDir)
            tp.append(pd.read_csv(Dirs[i],delimiter='	',skiprows=6,dtype=float))
        except:
            pass
        tp = create_df(tp)
        #print(super_data.loc([iData,'INT']).value)
        super_data.set_value(iData,'INT',tp.iloc[:,0].values.astype(float))
        super_data.set_value(iData,'LAMBDA',tp.index.values.astype(float))
    
    super_data  ### <------------------------------------------------------------------- This Is The Pandas Dataset 
    return super_data