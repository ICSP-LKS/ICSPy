#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 11:24:02 2017

@author: zech
"""

import pandas as pd
import numpy as np

def get_SASfit_Parameters(directory):
    params=pd.read_csv(directory,delimiter=";")
    
    # get the starting index of contributing sectors
    contribs_start = list(np.where((params['description']=='scattering contribution')==True)[0]+2)
    # get ending index of contributing sectors inside table
    contribs_end = list(np.where(params['description'].isnull()&params['description.1'].isnull()&params['description.2'].isnull())[0])
    # append the length of table to have limiting index for last contributing factor
    contribs_end.append(len(params))
    
    contribs = list(zip(contribs_start,contribs_end))
    
    data = pd.DataFrame(columns=['desc','val','err'])
    
    
    def get_schnitt(dat,cont,endstr):
        #get sector 'endstr' out of 3 possible ones
        schnitt = dat[['description'+endstr,'value'+endstr,'error'+endstr]][cont[0]:cont[1]]
        # get index for position in which column 'description' is NaN and exclude those
        index = np.where([not i for i in schnitt['description'+endstr].isnull()])[0]
        # schnitt will be extracted now
        schnitt=schnitt[['description'+endstr,'value'+endstr,'error'+endstr]].loc[schnitt.index[index]]
        return schnitt
    
    
    for i in range(0,len(contribs)):
        
        # textrac schnitt for size distribution ''
        schnitt=get_schnitt(params,contribs[i],'')
        # transfer schnitt into pandas DataFrame by ignoring the old and setting new columns names
        temp=pd.DataFrame(schnitt.values.tolist(),columns=['desc','val','err'])
        # apppend the extracted parameters to main DataFrame data
        data=data.append(temp,ignore_index=True)
        
        # extract schnitt for form factor '.1'
        schnitt=get_schnitt(params,contribs[i],'.1')
        temp=pd.DataFrame(schnitt.values.tolist(),columns=['desc','val','err'])
        data=data.append(temp,ignore_index=True)
        
        # extract schnitt for structure factor
        schnitt=get_schnitt(params,contribs[i],'.2')
        temp=pd.DataFrame(schnitt.values.tolist(),columns=['desc','val','err'])
        data=data.append(temp,ignore_index=True)
        
    return(data)

def main():
    data=get_SASfit_Parameters('MLZ_2017/sasfit-test/micelle_717_par.csv')
    print(data)
    
if __name__== "__main__":
    main()