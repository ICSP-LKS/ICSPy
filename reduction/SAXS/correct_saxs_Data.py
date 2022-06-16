
# coding: utf-8

# # Script for the Correction of differential scattering cross section in SAXS experiments (cooking book)

# In[137]:

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# URL for SAXS data of glassy carbon reference. There are several different onex available. The signal in high Q is nearly the same for all of them. Only in the low Q region they diverge from one another. The urls shown below correspond to the Glassy_Carbon_A, _B and _C samples from ANL. This script uses a Glassy carbon sample measured in another institute as reference.

# In[138]:

url_GCA = 'http://usaxs.xray.aps.anl.gov/docs/glassy_carbon_standard/GlassyCarbonA2.dat'
url_GCB = 'http://usaxs.xray.aps.anl.gov/docs/glassy_carbon_standard/GlassyCarbonB2.dat'
url_GCC = 'http://usaxs.xray.aps.anl.gov/docs/glassy_carbon_standard/GlassyCarbonC2.dat'

sample_GCA = np.loadtxt('/home/zech/FAUbox/PhD/Auswertung/SAXS/reference/USAXS_GC_A.txt')
sample_GCB = np.loadtxt('/home/zech/FAUbox/PhD/Auswertung/SAXS/reference/USAXS_GC_B.txt')


# Function to correct the thickness of the sample, by measuring an empty cuvette and one filled with water. For that two measurements with transmission and empty beam correspondingly have to be done with H2O and an empty cuvette. The mass attenuation coefficient for water in room temperature is $\frac{\mu}{\rho}=10.37\frac{cm²}{g}$. The sample thickness d can then be calculated by using:
# \vspace{3mm}
# 
# $$d = -\rho_{H_2O}\frac{\rho}{\mu}ln\left(\frac{T_{H_2O+cell}}{T_{cell}}\right)$$
# 
# \vspace{3mm}
# , with T being the transmission factors for an empty cell and water and $\rho_{H_2O}=1\frac{g}{cm²}$.

# In[139]:

# Übergabe: 
#    - Transmissionfactor water+cell T_wc
#    - only cell T_c 
#    - Anode type, most of the time copper


def calc_d(T_wc,T_c,typ='copper'):
    
    if typ=='copper':
        MAC_w = 10.37 #cm²/g, for copper anode
        
    rho_w = 1 #g/cm³
    
    d = -np.log(T_wc/T_c)*1/(MAC_w*rho_w) #cm
    return(d)


# %display latex
# Function to calculate the transmission factor for intensity of sample S and empty beam intensity $I_0$:
# \vspace{3mm}
# $$T_S=\frac{I_S}{I_0}$$

# In[140]:

def calc_T(I_S,I_0):
    return(I_S/I_0)


# This Function calulates the Scaling or Correction Factor with a Glassy Carbon measurement done in your setup and scales it so it fits the intensity of the 'Glassy-Carbon-A' sample from ANL. You can chose whatever reference sample you like. They should turn out more or less the same. For consistency's sake, I will solely use the A sample. The formula for the SF calculation follows from Fan-Paper:
# \vspace{3mm}
# $$SF = \frac{\left(\frac{\delta\Sigma}{\delta\Omega}\right)_{st}}{\frac{(I_{st}-BG_{st})}{d_{st}T_{st+cell}}}$$
# \vspace{3mm}
# ,with 'st' corresponding to the standard sample, in my case glassy carbon. BG corresponds to the background measurement and T the transmission factor for the GC measurements.

# In[141]:

# Übergabe: 
#    - Intensity of GC
#    - Q values of measurement for interpolation from Reference sample
#    - Background of GC measurement
#    - Transmissionfactor GC
#    - thickness sample d_GC


def calc_SF(I_GC,Q_GC,BG_GC,T_GC,d_GC):
    
    from scipy.optimize import curve_fit as fit
    def fit_lin(x,a,c):
        return a*x+c
    
    
    sample_GCA = np.loadtxt('/home/zech/FAUbox/PhD/Auswertung/SAXS/reference/GC_APS.txt')
    
    DSC_GC = fit(fit_lin,Q_GC[:6],I_GC[:6])[0][1]
    DSC_Ref = fit(fit_lin,sample_GCA[:39,0],sample_GCA[:39,1])[0][1]
    
    SF_vec = DSC_Ref/((DSC_GC)/(d_GC*T_GC))
    return(SF_vec)
    
    


# Finally the differential scattering crosssection for sample s will be correctly calculated using all previously determined parameters $SF$ and $d_s$:
# \vspace{3mm}
# $$\left(\frac{\delta\Sigma}{\delta\Omega}\right)_s(q) = SF \left(\frac{I_s(q)-BG_s(q)}{d_sT_{s+cell}}\right)$$

# In[142]:

# Übergabe: 
#    - Intensity of sample
#    - Background of sample measurement
#    - Transmissionfactor GC
#    - thickness sample d_GC
#    - Scaling factor

def calc_diffScatCross(I_s,BG_s,T_sc,d_s,SF):
    return(SF*(I_s-BG_s)/(d_s*T_sc))


# # From here on follows an example

# From here follows an example using sample TiS710 and data measured on our Anton Paar machine. First the intensities are extracted from .stat files. This process will not be discussed further, because it's simply parsing the files contained in the in 'dir' specified folder automatically. This step corresponds to  <span class="girk">point (1)</span> in the cooking book. Calculate the transmission factors.

# In[143]:

import os

dir = '/home/zech/FAUbox/PhD/Auswertung/SAXS/test_data/'

l_EB_Stats = []
l_TR_Stats = []

table = pd.DataFrame(columns = ['TR','EB','I_TR','I_EB','T'])
pairs = pd.DataFrame(columns = ['typ','samp'])

for iFile in os.listdir(dir):
    if os.path.isfile(os.path.join(dir, iFile)):
        if '.stat' in iFile:
            enum = iFile.split('_')[0]
            typ = iFile.split('_')[2]
            samp = iFile.split('_')[1]
            pairs.loc[str(enum)] = [str(typ),str(samp)]

for iFile in os.listdir(dir):
    if os.path.isfile(os.path.join(dir, iFile)):
        #print(os.path.join(dir,iFile))
        if '.stat' in iFile:
            for line in open(os.path.join(dir,iFile),'r'):
                if 'Total intensity' in line:
                    inty = line.split()[3]
                    enum = iFile.split('_')[0]
                    samp = pairs.loc[str(enum),'samp']
                    typ = pairs.loc[str(enum),'typ']
                    if str(samp) not in table.index:
                        table.loc[str(samp)] = [0,0,0,0,0]
                    if typ == 'TR':
                        table.loc[str(samp),'TR'] = enum
                        table.loc[str(samp),'I_TR'] = inty
                    elif typ == 'EB' or 'DB':
                        table.loc[str(samp),'EB'] = enum
                        table.loc[str(samp),'I_EB'] = inty
                    
for iInd in table.index:
    table.loc[iInd,'T'] = calc_T(float(table.loc[iInd,'I_TR']),float(table.loc[iInd,'I_EB']))
    
table


# 
# In the next step the SF will be determined via the glassy carbon measurement. This is <span class="girk">step (2)</span>.

# In[144]:

data_GC = np.loadtxt('/home/zech/FAUbox/PhD/Auswertung/SAXS/test_data/01719_GC.chi')
sample_GCA = np.loadtxt('/home/zech/FAUbox/PhD/Auswertung/SAXS/reference/GC_APS.txt')

plt.loglog(data_GC[:,0],data_GC[:,1],'xg', label='measured GC')
plt.loglog(sample_GCA[:,0],sample_GCA[:,1],'xr',label='reference GC')

data_BG_GC = np.zeros(shape=(len(data_GC[:,0])))
SF = calc_SF(I_GC=data_GC[:,1],
             BG_GC=data_BG_GC,
             Q_GC=data_GC[:,0],
             T_GC=table.loc['GC','T'],
             d_GC=0.001)
d_GC=0.001
T_GC=table.loc['GC','T']
plt.loglog(data_GC[:,0],data_GC[:,1]/(d_GC*T_GC)*SF,'xb',label='corrected GC')
plt.legend(loc='best')
plt.grid()
plt.show()
print('calculated scaling factor SF = ' +str(SF))


# In <span class="girk">step (3)</span>  the thickness of the samples will be calculated from H2O and empty cell measurements.

# In[145]:

T_wc = table.loc['H2O','T']
T_c = table.loc['EC','T']

d_s = calc_d(T_wc=T_wc,T_c=T_c)
print('thickness of sample d_s = %f01 ; (should be about 0.1 cm)' % d_s)


# In the end of this procedure (<span class="girk">step (4)</span>) the differential scattering cross section of the sample will be calculated, by using the parameters determined in the steps above.

# In[146]:

T_sc = table.loc['SGNR','T']

data_s = np.loadtxt('/home/zech/FAUbox/PhD/Auswertung/SAXS/test_data/01725_S_GNR.chi')
data_H2O = np.loadtxt('/home/zech/FAUbox/PhD/Auswertung/SAXS/test_data/01745_H2O.chi')

I_s = data_s[:,1]
BG_s = data_H2O[:,1]

DSC_s = SF*(I_s-BG_s)/(d_s*T_sc)


# In[147]:

plt.loglog(data_s[:,0],DSC_s,'xk',label='corrected DSC for GNRs');
plt.legend()
plt.grid()
plt.show()


# In[ ]:



