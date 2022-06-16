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