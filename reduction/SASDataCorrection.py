# -*- coding: utf-8 -*-
"""
Created on Mon Dec  3 15:30:16 2018

@author: ZechT
"""
# # Script for the Correction of differential scattering cross section in SAXS experiments (cooking book)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

"""
# URL for SAXS data of glassy carbon reference. There are several different onex available. The signal in high Q is nearly the same for all of them. Only in the low Q region they diverge from one another. The urls shown below correspond to the Glassy_Carbon_A, _B and _C samples from ANL. This script uses a Glassy carbon sample measured in another institute as reference.

#url_GCA = 'http://usaxs.xray.aps.anl.gov/docs/glassy_carbon_standard/GlassyCarbonA2.dat'
#url_GCB = 'http://usaxs.xray.aps.anl.gov/docs/glassy_carbon_standard/GlassyCarbonB2.dat'
#url_GCC = 'http://usaxs.xray.aps.anl.gov/docs/glassy_carbon_standard/GlassyCarbonC2.dat'

#sample_GCA = np.loadtxt('/home/zech/FAUbox/PhD/Auswertung/SAXS/reference/USAXS_GC_A.txt')
#sample_GCB = np.loadtxt('/home/zech/FAUbox/PhD/Auswertung/SAXS/reference/USAXS_GC_B.txt')


# Function to correct the thickness of the sample, by measuring an empty cuvette and one filled with water. For that two measurements with transmission and empty beam correspondingly have to be done with H2O and an empty cuvette. The mass attenuation coefficient for water in room temperature is $\frac{\mu}{\rho}=10.37\frac{cm²}{g}$. The sample thickness d can then be calculated by using:
# \vspace{3mm}
# 
# $$d = -\rho_{H_2O}\frac{\rho}{\mu}ln\left(\frac{T_{H_2O+cell}}{T_{cell}}\right)$$
# 
# \vspace{3mm}
# , with T being the transmission factors for an empty cell and water and $\rho_{H_2O}=1\frac{g}{cm²}$.
"""
class sasDataCorrection(object):
    """
    # Übergabe: 
    #    - Transmissionfactor water+cell T_wc
    #    - only cell T_c 
    #    - Anode type, most of the time copper
    """
    def __init__(self):
        pass
    
    def calc_d(self,T_wc,T_c,typ='copper'):
        # mass attenuation coefficient from https://physics.nist.gov/PhysRefData/XrayMassCoef/ComTab/water.html
        if typ=='copper':
            MAC_w = 10.24 #cm²/g, for copper anode mass attenuation coefficient
        elif typ=='gallium':
            MAC_w = 6.72#cm²/g, for gallium jet
            
        rho_w = 1 #g/cm³
        
        d = -np.log(T_wc/T_c)*1/(MAC_w*rho_w) #cm
        return(d)

    def calc_T(self,I_S,I_0):
        return(I_S/I_0)
    
    """
    # This Function calulates the Scaling or Correction Factor with a Glassy Carbon measurement done in your setup and scales it so it fits the intensity of the 'Glassy-Carbon-A' sample from ANL. You can chose whatever reference sample you like. They should turn out more or less the same. For consistency's sake, I will solely use the A sample. The formula for the SF calculation follows from Fan-Paper:
    # \vspace{3mm}
    # $$SF = \frac{\left(\frac{\delta\Sigma}{\delta\Omega}\right)_{st}}{\frac{(I_{st}-BG_{st})}{d_{st}T_{st+cell}}}$$
    # \vspace{3mm}
    # ,with 'st' corresponding to the standard sample, in my case glassy carbon. BG corresponds to the background measurement and T the transmission factor for the GC measurements.
 
    # Übergabe: 
    #    - Intensity of GC
    #    - Q values of measurement for interpolation from Reference sample
    #    - Background of GC measurement
    #    - Transmissionfactor GC
    #    - thickness sample d_GC
    """
    
    def calc_SF(self,Q_GC,I_GC,T_GC,d_GC,t_GC,freg,plot=False):
        
        from scipy.optimize import curve_fit as fit
        def fit_lin(x,a,c):
            return np.exp(a*np.log10(x)+c)
        
        import os 
        dir_path = os.path.dirname(os.path.realpath(__file__))
        sample_GCA = np.loadtxt(dir_path+'/SAXS/reference/GC_APS.txt')
        
        DSC_GC = fit(fit_lin,Q_GC[freg[0]:freg[1]],I_GC[freg[0]:freg[1]]/(d_GC*t_GC*T_GC))[0]
        DSC_Ref = fit(fit_lin,sample_GCA[:35,0],sample_GCA[:35,1])[0]
        #print('Fit Params. Meas: ',np.exp(DSC_GC), ' Fit Params. Ref: ',np.exp(DSC_Ref))
        SF = np.exp(DSC_Ref[1])/(np.exp(DSC_GC[1]))
        #print(SF)
        SF = np.mean(SF)
        if plot:
            import matplotlib.pyplot as plt
            ax = plt.figure().add_subplot(111)
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.plot(Q_GC,fit_lin(Q_GC,DSC_GC[0],DSC_GC[1]),'--b')
            ax.plot(Q_GC,fit_lin(Q_GC,DSC_Ref[0],DSC_Ref[1]),'--k')
            ax.plot(Q_GC,I_GC/(d_GC*t_GC*T_GC),'-r',label='meas. GC')
            ax.plot(Q_GC,SF*I_GC/(d_GC*t_GC*T_GC),'-b',label='meas. GC')
            ax.plot(sample_GCA[:,0],sample_GCA[:,1],'-k',label='meas. GC')
            
        return(SF) 
        
    
    """################################################################################################################
    # Übergabe: 
    #    - Intensity of GC
    #    - Q values of measurement for interpolation from Reference sample
    #    - Background of GC measurement
    #    - Transmissionfactor GC
    #    - thickness sample d_GC
    """
    
    def calc_SF_H2O(H2O,EC,T_H2O,T_EC,d,t_H2O,t_ED):
        
        from scipy.optimize import curve_fit as fit
        def fit_poly(x,a,b,c):
            return b*x**2+a*x+c
        
        fig=plt.figure()
        ax=fig.add_subplot(111)
        ax.set_xscale('log')
        ax.set_yscale('log')
        
        I_CF = 1.69e-2 # 1/cm
        
        bH2O = H2O[:,1]/(d*t_H2O*T_H2O)-EC/(d*t_EC*T_EC)
        
        popt,pcov = fit(fit_poly,H2O[:,0],bH2O)
        
        I_0_H2O = fit_poly(0,popt[0],popt[1],popt[2])
        
        SF_vec = I_0_H2O/I_CF
        
        ax.plot(H2O[:,0],bH2O,label='before calibration',color='b')
        ax.plot(H2O[:,0],bH2O*SF_vec,label='after calibration',color='k')
        ax.plot(H2O[:,0],fit_poly(H2O[:,0],popt[0],popt[1],popt[2]),label='fit',color='r')
        ax.legend(loc='best')
        plt.show()
        return(SF_vec)
        
    """################################################################################################################
    # Übergabe: 
    #    - Dir1 is directory of TM statistics file of Fit2D
    #    - Dir2 is directory of DB statistics file of Fit2D
    """
    
    def calc_T_fromDir(Dir1,Dir2):
        pass
        I_TM = 1
        I_DB = 1
        file_TM = open(Dir1,'r')
        file_DB = open(Dir2,'r')
        for iLine in file_TM.readlines():
            if 'Total intensity = ' in iLine:
                #debug(iLine.split(' ')[4])
                I_TM = float(iLine.split(' ')[4])    
        for iLine in file_DB.readlines():
            if 'Total intensity = ' in iLine:
                #debug(iLine.split(' ')[4])
                I_DB = float(iLine.split(' ')[4])
                pass
        return I_TM/I_DB    
    
    
    # Finally the differential scattering crosssection for sample s will be correctly calculated using all previously determined parameters $SF$ and $d_s$:
    # \vspace{3mm}
    # $$\left(\frac{\delta\Sigma}{\delta\Omega}\right)_s(q) = SF \left(\frac{I_s(q)-BG_s(q)}{d_sT_{s+cell}}\right)$$

    # Übergabe: 
    #    - Intensity of sample
    #    - Background of sample measurement
    #    - Transmissionfactor GC
    #    - thickness sample d_GC
    #    - Scaling factor
    

    def calc_diffScatCross(self,I,BG,T_Sc,T_BG,d,SF,t_Sc=1,t_BG=1,Range=None):        
        I = self.calc_diffScatCrossWBG(I,T_Sc,d,SF,t_Sc)
        BG = self.calc_diffScatCrossWBG(BG,T_BG,d,SF,t_BG)
        if Range is None:
            
            return(I-BG)
        else:
            import approxDatasets as approx
            return(approx(I,BG,Range,Type='subtract').calc())
        
    def calc_diffScatCrossWBG(self,I,T_Sc,d,SF,t=1):
        return(SF*((I)/(d*T_Sc*t)))

    
    def calc_ErrorBars(self,Data,DataInt):
        N = DataInt[:,1]/Data[:,1]
        newData = np.array([Data[:,0],Data[:,1],np.sqrt(Data[:,1])/N]).T
        return newData

            
class approxDatasets(object):
    
    def __init__(self,Data1,Data2,valRange,window=1,Type='combine'):
        self.Data1 = Data1
        self.Data2 = Data2
        self.valRange = valRange
        self.window = window
        self.type = Type
        
    def getIndices(self,data):        
        iVal = self.valRange[0]
        jVal = self.valRange[1]
        i = np.where(np.array(data)>iVal)[0][0]
        j = np.where(np.array(data)<jVal)[0][-1]
        return i,j
    
    def Int(self,x,y):
        integral = 0
        for iR in range(len(x)-1):
            integral+=(1/2.*(x[iR+1]-x[iR])*(y[iR+1]+y[iR]))
        return integral
    
    def combine(self,Data1,Data2,valRange):
        iVal = self.valRange[0]
        jVal = self.valRange[1]
        
        j1 = np.where(np.array(Data1[:,0])<jVal)[0][-1]
    
        i2 = np.where(np.array(Data2[:,0])>iVal)[0][0]
        newData = np.concatenate((Data1[:j1,:],Data2[i2:,:]))
        newData = newData[newData[:,0].argsort()]
        return(newData)
    def polynomial(self,x,*args):
        poly = np.zeros(len(x))
        for i in range(len(args)):
            poly+=args[i]*x**i
        return poly
    
    def medianFilter(self,data):
        import scipy.signal as sgn
        return sgn.medfilt(data,self.window)
        
    def calc(self):
        import scipy.optimize as opt
        def polynomial(x,*args):
            poly = np.zeros(len(x))
            for i in range(len(args)):
                poly+=args[i]*x**i
            return poly
        
        def calcCF(CF,Data2,func,valRange):
            i2,j2 = self.getIndices(Data2[:,0])        
            Int1 = self.Int(Data2[i2:j2,0],func(Data2[i2:j2,0]))
            Int2 = self.Int(Data2[i2:j2,0],Data2[i2:j2,1]*CF)
            #print(self.type)
            #print(Int1-Int2)
            return np.abs(Int1-Int2)
            
        i,j = self.getIndices(self.Data1[:,0])
        popt,pcov = opt.curve_fit(polynomial,self.Data1[i:j,0],self.Data1[i:j,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])
        
        func = lambda x: polynomial(x,*popt)
        
        CF = 0.27
        minInstance = lambda x: calcCF(x,np.array([self.Data2[:,0],self.Data2[:,1]*CF]).T,func,self.valRange)
        CF *= opt.minimize(minInstance,x0=[CF]).x[0]
        self.Data2[:,1:]=self.Data2[:,1:]*CF
        if self.type == 'combine':
            newData = self.combine(self.Data1,self.Data2,self.valRange)
            i,j = self.getIndices(newData[:,0])
            newData[i:,1]=self.medianFilter(newData[i:,1])
            if np.shape(newData)[1]>2:
                newData[i:,2]=self.medianFilter(newData[i:,2])
        elif self.type == 'subtract':
            newData = self.Data1
            newData[:,1] = self.Data1[:,1]-self.Data2[:,1]*0.99
            if np.shape(newData)[1]>2:
                newData[:,2] = np.sqrt(self.Data1[:,2]**2+self.Data2[:,2]**2)            
        return(newData,CF,popt)
                
def main():
    import os
    

if __name__ == "__main__":
    main()

