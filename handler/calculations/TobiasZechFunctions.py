# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 21:15:48 2018

@author: ZechT
"""

import numpy as np

def const(x,a):
    return a

def lin(x,a,b):
    return x*a+b

def poly(x,Consts):
    Sum = 0
    for i in range(len(Consts)):
        Sum+=x**i*Consts[i]
    return Sum

def Gaussian(x,N,mu,s):
    from scipy.special import erf
    c=np.sqrt(np.pi/2)*s*(1+erf(mu/(np.sqrt(2)*s)))
    return np.array(N/c*np.exp(-(x-mu)**2/(s**2*2)))

def NGaussian(x,**kwargs):    
    N,mu,s=[]
    
    [N.append(kwargs[a]) for a in kwargs if 'N' in a]
    [mu.append(kwargs[a]) for a in kwargs if 'mu' in a]
    [s.append(kwargs[a]) for a in kwargs if 's' in a]
    
    Sum=np.zeros(shape=len(x))
    for i in range(len(N)):
        Sum+=Gaussian(x,N[i],mu[i],s[i])
            
    return Sum

def VoigtGaussian(x,mu,s):
    return 1/(np.sqrt(2*np.pi)*s)*np.exp(-((x-mu)/(2*s))**2)

def Lorentzian(x,mu,s):
    return s/(np.pi*((x-mu)**2+s**2))


class ErrorFunc():
    def __init__(self,tau):
        self.tau = float(tau)
    def errorFunc(self,x,t0,sigma,N):
        import scipy as sci
        
        return(1/2*N*(sci.special.erf((x-t0-self.tau)/((sigma)*np.sqrt(2)))+1))

def LogisticFunction(x,t0,k,N):
    return(N/(1+np.exp(-1/k*(x-t0))))
    

"""
Normal Auto Catalytic Function to determine the reaction rate of gold ions that are being reduced on the
Gold surface during AuNP and AuNR growth, when the atoms inside the gold nanoparticle are assumed to
somehow contribute to the autocatalytic reaction.
"""
def AutocatalyticFunction(x,cAu00,cAu10,k):
    return((cAu00+cAu10)/(1+cAu10/cAu00*np.exp(-1/k*(x)*(cAu10+cAu00))))
def AutocatalyticFunction2(x,cAu10,k,tau):
    cAu00= 120/5000*0.2/8.3*10000
    return((cAu00+cAu10)/(1+cAu10/cAu00*np.exp(-1/k*(x-tau)*(cAu10+cAu00))))


"""
Surface Auto Catalytic Function to determine the reaction rate of gold ions that are being reduced on the
Gold surface during AuNP and AuNR growth.
"""
class SACFMinimize():
    def __init__(self,data=None,dt=1):
        self.dt = dt
        self.steps=len(data)
        self.data = data
    def calcCAu0(self,x,cAu00,cAu10,k,tau):
        #cAu00= 120/5000*0.2/8.3*10000
        #alpha=1.0
        dt=self.dt
        steps = self.steps#*int(1/dt)
        
        cAu0 = [cAu00]
        cAu1 = [cAu10]
        time = 0
        for i in range(steps-1):
            cAu0.append(cAu0[i]+1/k*cAu0[i]**(2/3)*cAu1[i]*dt)
            cAu1.append(cAu1[i]-1/k*cAu0[i]**(2/3)*cAu1[i]*dt)
        return(cAu0-self.data[tau:len(self.data)])



'''
 psoido voigt profil
'''
def Eta(sg,sl):
    f = (sg**5+2.69269*sg**4*sl+2.42843*sg**3*sl**3+4.47163*sg**2*sl**4+sl**5)**(1/5.)
    eta = 1.36603*(sl/f)-0.47719*(sl/f)**2+0.11116*(sl/f)**3
    return eta,f
def PseudoVoigt(x,N,mu,s1,s2,c):    
    eta,f = Eta(s1,s2)
    Gauss = VoigtGaussian(x,mu,f)
    Lorentz = Lorentzian(x,mu,f) 
    return N*(eta*Lorentz+(1-eta)*Gauss)+c

"""
Return a Pearson7 lineshape.
Using the wikipedia definition:
pearson7(x, center, sigma, expon) =
    amplitude*(1+arg**2)**(-expon)/(sigma*beta(expon-0.5, 0.5))
where arg = (x-center)/sigma
and beta() is the beta function.
"""
def pearson7(x, amplitude=1.0, center=0.0, sigma=1.0, expon=1.0, bg=0.0):
    
    from scipy.special import gamma as gamfcn
    arg = (x-center)/sigma
    scale = amplitude * gamfcn(expon)/(gamfcn(0.5)*gamfcn(expon-0.5))
    return scale*(1+arg**2)**(-expon)/sigma+bg
"""
#This function returns the density of a CTAB stabilization shell from SLDs 
"""   
def calcdensityShell(sld):
    sld_miz = -.26
    sld_d2o = 6.33
    return((1-(sld-sld_miz)/(sld_d2o-sld_miz))*100)

"""
#Concentration of micelles inside the solution
"""
def calcMizConc(volfrac,x_core,radius,shell=7): #return in mol/l
    length=x_core*(radius)
    volell = 4.0/3*np.pi*((radius+shell)*1e-9)**2*((length+shell)*1e-9)
    Na = 6.0221409e+23
    #return(volfrac/((1-volfrac)*volell*Na))
    N_ell = volfrac*1/volell # 1= 1l
    return(N_ell/(1*Na)) # 1=1l

"""
#aggregationsnumber aus tilos dissertation, berechnet über die molare masse eine C13.5H28 molekuels im kern der Mizelle
"""
def calcNagg(radius,x_core,volfrac=1.0):    
    volellcore = 4.0/3*np.pi*((radius))**2*x_core*(radius)*volfrac
    return(0.79*6.022e23*volellcore/190.36)

"""    
#molar concentration of CTAB incorporated in micelles
"""
def calcMicellarCTAB(volfrac,x_core,radius,pd=0.35,stutzstellen=35,nsigma=3):
    def gaussian(x,mu,sigma):
        return(1/(sigma*np.sqrt(2*np.pi))*np.exp(-1/2*((x-mu)/sigma)**2))
    sumC = 0
    sigma = pd*radius
    sigma_list = np.linspace(-sigma*3,sigma*3,35)
    for i in range(stutzstellen):
        r = radius+sigma_list[i]
        sumC+=calcNagg(r,x_core)*calcMizConc(gaussian(r,radius,sigma)*volfrac,x_core,r)
    return(sumC)

"""
#This function returns how much CTAB is incorporated into the shell. It returns the Aggregation number in 32A thick shell
"""     
def calcShellCTAB(densityShell,rRod,lRod,shell=32):
    shellVolume = (np.pi*(rRod+shell)**2*(lRod+2*shell)-np.pi*(rRod)**2*(lRod))
    shellVolumeLiter = (np.pi*(rRod*1e-9+shell*1e-9)**2*(lRod*1e-9+2*shell*1e-9)-np.pi*(rRod*1e-9)**2*(lRod*1e-9))
    CTABVolume = densityShell*0.01*shellVolume
    V_tail = 458 #A^3
    V_head = 130 #A^3
    V_Br = 37 #A^3
    Na = 6.0221409e+23
    NAgg = CTABVolume/(V_tail+V_head+V_Br)
    conc = NAgg/(Na*shellVolumeLiter)
    return(NAgg,conc)

"""    
#This function returns the amount of CTAB per nm^2 on top of the AuNR   
"""
def calcSurfaceDensityCTAB(naggCTABShell,rRod,lRod):
    AuNRSurface = 2*np.pi*(rRod/10)**2+2*np.pi*rRod/10*lRod/10    
    return(naggCTABShell/AuNRSurface)

"""
#This function returns the molar concentration of AuNR in the solution calculated from the Volume Fraction
"""
def calcAuNRConcentration(volfrac,length,radius):
    volcyl =np.pi*((radius)*1e-9)**2*((length)*1e-9)
    Na = 6.0221409e+23
    #return(volfrac/((1-volfrac)*volell*Na))
    N_cyl = volfrac*1/volcyl # 1= 1l
    return(N_cyl/(1*Na)) # 1=1l

def calcAuNSConcentration(volfrac,radius):
    volsphere =4/3*np.pi*((radius)*1e-9)**3
    Na = 6.0221409e+23
    #return(volfrac/((1-volfrac)*volell*Na))
    N_cyl = volfrac*1/volsphere # 1= 1l
    return(N_cyl/(1*Na)) # 1=1l

"""

"""
def calcTotalCTABShellVolfrac(CTABVolPerc,volfracAuNR,volfracAuNRShell):
    volfracShell = volfracAuNRShell-volfracAuNR
    return(volfracShell*CTABVolPerc*0.01)

"""

"""    
def calcCTABShellMicelleRatio(amountMiz,AuNRConc,MizConc):
    mizConcAuNR = amountMiz*AuNRConc
    return(mizConcAuNR/MizConc)
   
def volfrac2conc_Miz(volfrac,radius):
    return((volfrac/(4/3*np.pi*radius**3))/6.022e23)
    
    
"""
#This function returns the molar concentration of Au0 per second that is reduced from Au3, also returns the total molar amount of Au0
"""    
def calcAu0ReductionFromSAXS(conc,length,radius,timestep=1):
    #Na = 6.0221409e+23
    V_Au0 = (4.08*1e-10)**3 #Angstrom
    c_Au0 = 4*(np.pi*(radius*1e-10)**2*length*1e-10)/V_Au0*conc
    c_Au0perSecond = np.gradient(c_Au0,timestep)
    return(c_Au0perSecond,c_Au0)
    
"""
#This function returns the molar concentration of AuNR per second, also returns the total molar amount of AuNR
"""    
def calcAuNRIncreaseFromSAXS(volfrac,length,radius,timestep=1):
    c_AuNR = calcAuNRConcentration(volfrac,length,radius)
    c_AuNRperSecond = np.gradient(c_AuNR,timestep)
    return(c_AuNRperSecond,c_AuNR)
    
def calcAuNSIncreaseFromSAXS(volfrac,radius,timestep=1):
    c_AuNR = calcAuNSConcentration(volfrac,radius)
    c_AuNRperSecond = np.gradient(c_AuNR,timestep)
    return(c_AuNRperSecond,c_AuNR)


"""
Plotting functions for SAS data
"""
def plotSAS(axis,data,label,color,title=None,ls='',marker='x',markersize=15,markerwidth=2,omitYLabel=False,omitXLabel=False,zorder=2,lw=2,offset=1):
                  
    if title is not None:
        axis.set_title(title,fontweight='bold',fontsize=16)
    axis.set_xscale("log")
    axis.set_yscale("log")
    
    if len(data[0,:])>=3:
        axis.errorbar(data[:,0],data[:,1]*offset,yerr=data[:,2],
                     marker=marker,linestyle=ls,color=color,label=label,zorder=zorder,lw=lw,fillstyle='none') 
    else:
        axis.plot(data[:,0],data[:,1]*offset,
                     marker=marker,linestyle=ls,color=color,label=label,zorder=zorder,lw=lw,markeredgewidth=markerwidth,ms=markersize,fillstyle='none')
        
    if not omitXLabel:
        axis.set_xlabel(r'Q ($\mathrm{\AA^{-1}}$)',fontsize=20)
    if not omitYLabel:
        axis.set_ylabel(r'$\mathrm{\partial\Sigma/\partial\Omega}$ ($\mathrm{cm^{-1}}$)',fontsize=20)
    for tick in axis.xaxis.get_major_ticks():
            tick.label.set_fontsize(16) 
            #tick.label.set_fontweight('bold')

    for tick in axis.yaxis.get_major_ticks():
            tick.label.set_fontsize(16)
            #tick.label.set_fontweight('bold')
    
    axis.xaxis.set_tick_params(width=2,length=6)
    axis.yaxis.set_tick_params(width=2,length=6)
    axis.xaxis.set_tick_params('minor',width=2,length=3)
    axis.yaxis.set_tick_params('minor',width=2,length=3)
    
def plotSASInset(axis,data,label,color,title=None,ls='',marker='x',omitYLabel=False,omitXLabel=False,zorder=2,lw=2):
                  
    if title is not None:
        axis.set_title(title,fontweight='bold',fontsize=16)
    axis.set_xscale("log")
    axis.set_yscale("log")
    
    if len(data[0,:])>=3:
        axis.errorbar(data[:,0],data[:,1],yerr=data[:,2],
                     marker=marker,linestyle=ls,color=color,label=label,zorder=1,lw=lw) 
    else:
        axis.plot(data[:,0],data[:,1],
                     marker=marker,linestyle=ls,color=color,label=label,zorder=zorder,lw=lw)
        
    #if not omitXLabel:
    #    axis.set_xlabel(r'[Q] = $\mathrm{\AA^{-1}}$',fontsize=20)
    #if not omitYLabel:
    #    axis.set_ylabel(r'[$\mathrm{\partial\Sigma/\partial\Omega}$] = $\mathrm{cm^{-1}}$',fontsize=20)
    for tick in axis.xaxis.get_major_ticks():
            tick.label.set_fontsize(12) 
    for tick in axis.xaxis.get_minor_ticks():
            tick.label.set_fontsize(12) 
            #tick.label.set_fontweight('bold')

    for tick in axis.yaxis.get_major_ticks():
            tick.label.set_fontsize(12)
    for tick in axis.yaxis.get_minor_ticks():
            tick.label.set_fontsize(12)
            #tick.label.set_fontweight('bold')
    
    axis.xaxis.set_tick_params(width=2,length=6)
    axis.yaxis.set_tick_params(width=2,length=6)
    axis.xaxis.set_tick_params('minor',width=2,length=3)
    axis.yaxis.set_tick_params('minor',width=2,length=3)



"""
Standardized formatting for plots of Tobias Zech
"""
def formatAxis(ax,xlabel,ylabel,ax2=None,y2label=None,hideX=False,YColor='k',Y2Color='k',xlabelorientation='horizontal'):
    
    fsAxis = 20
    fsTicks = 16
    fsTitle = 20
    fsLegend = 18
    if not hideX and not ax2:
        ax.set_xlabel(xlabel,fontsize=fsAxis)
    
    ax.set_ylabel(ylabel,fontsize=fsAxis,color=YColor)
    for tick in ax.xaxis.get_major_ticks():
            if not hideX:
                tick.label.set_fontsize(fsTicks) 
                #tick.label.set_fontweight('bold')
                tick.label.set_rotation(xlabelorientation)
            else:
                tick.label.set_visible(False)
    for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(fsTicks)
            #tick.label.set_fontweight('bold')
            tick.label.set_color(YColor)
    if ax2:
        for tick in ax.axes.get_yticklabels():
                tick.set_fontsize(fsTicks)
                #tick.set_fontweight('bold') 
                tick.set_color(Y2Color)        
        ax.set_ylabel(ylabel,fontsize=fsAxis,color=Y2Color)
    

    ax.xaxis.set_tick_params(width=2,length=8)
    ax.yaxis.set_tick_params(width=2,length=8)

    return(ax)


"""
This function creates a pandas dataset for a time resolved UV-Vis dataset recorded with the standard software 
of the Tidas UV-Vis Spectrometer, when the data has been exported in a 2D file.
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