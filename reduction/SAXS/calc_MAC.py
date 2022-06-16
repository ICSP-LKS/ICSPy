# -*- coding: utf-8 -*-
"""
Created on Mon May 18 16:27:22 2020

@author: ZechT
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt

def npoly(x,a,b,c,d,e,f,g,h):
    return(a*x**7+b*x**6+c*x**5+d*x**4+e*x**3+f*x**2+g*x+h)
    

#MAC=np.loadtxt('MAC_table.txt')
MAC=np.loadtxt('MAC_table2.txt',skiprows=3)


plt.figure()
plt.yscale('log')
plt.xscale('log')
plt.plot(MAC[:,0],MAC[:,2])
plt.plot(MAC[:,0],MAC[:,1])
EnergyGallium = 9.251674e-3
EnergyCopper = 8.0478227e-3
plt.plot([EnergyGallium,EnergyGallium],[10e-4,10e3],color='red')
plt.plot([EnergyCopper,EnergyCopper],[10e-4,10e3],color='red')