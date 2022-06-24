# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import subprocess
import time as time


class ReduceData(object):
    
    def __init__(self,fit2Dexe,InDir,OutDir,List,Mask,Calib,prefix = 'im_00', suffix = '_craw.tiff',compute=True):
        self.logFile = str(np.datetime64('today','D'))+'.log'
        self.InDir = InDir
        self.OutDir = OutDir
        self.List = List
        self.Mask = Mask
        self.Calib = Calib
        self.prefix = prefix
        self.suffix = suffix
        self.p = subprocess.Popen([fit2Dexe,"-com"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True,shell=False)
        if compute:
            self.compute()
        
    def compute(self):
        for iData in self.List:
            parsed_string = ''
            parsed_string+='SAXS / GISAXS\nINPUT\n'+self.InDir+self.prefix+str(iData)+self.suffix+'\n'
            parsed_string+='MASK\nLOAD MASK\n'+self.Mask+'\nEXIT\n'
            parsed_string+='INTEGRATE\nX-PIXEL SIZE\n172.0\nY-PIXEL SIZE\n172.0\nDISTANCE\n'+str(self.Calib['SDD'])+'\nWAVELENGTH\n1.34\n'
            parsed_string+='X-BEAM CENTRE\n'+str(self.Calib['BeamXpix'])+'\nY-BEAM CENTRE\n'+str(self.Calib['BeamYpix'])
            parsed_string+='\nTILT ROTATION\n0.0\nANGLE OF TILT\n0.0\nDETECTOR ROTATION\n0.0\n'
            parsed_string+='O.K.\nSCAN TYPE\nQ-SPACE\nCONSERVE INT.\nNO\nPOLARISATION\nNO\nGEOMETRY COR.\nYES\nSCAN BINS\n'+str(self.Calib['Bins'])+'\n'
            parsed_string+='PARAMETER FILE\n'+self.OutDir+str(iData)+'.par\nO.K.\nOUTPUT\nCHIPLOT\n'
            parsed_string+='FILE NAME\n'+self.OutDir+str(iData)+'.chi\nO.K.\nEXCHANGE\n'
            parsed_string+='INTEGRATE\nX-PIXEL SIZE\n172.0\nY-PIXEL SIZE\n172.0\nDISTANCE\n'+str(self.Calib['SDD'])+'\nWAVELENGTH\n1.34\n'
            parsed_string+='X-BEAM CENTRE\n'+str(self.Calib['BeamXpix'])+'\nY-BEAM CENTRE\n'+str(self.Calib['BeamYpix'])
            parsed_string+='\nTILT ROTATION\n0.0\nANGLE OF TILT\n0.0\nDETECTOR ROTATION\n0.0\n'
            parsed_string+='O.K.\nSCAN TYPE\nQ-SPACE\nCONSERVE INT.\nYES\nPOLARISATION\nNO\nGEOMETRY COR.\nNO\nSCAN BINS\n'+str(self.Calib['Bins'])+'\n'
            parsed_string+='PARAMETER FILE\n'+self.OutDir+str(iData)+'_Int.par\nO.K.\nOUTPUT\nCHIPLOT\n'
            parsed_string+='FILE NAME\n'+self.OutDir+str(iData)+'_Int.chi\nO.K.\nEXIT\n'            
            stdout= self.p.stdin.write(parsed_string)[0]
            
            #print(stdout.split('\n'))
            
            if 'ERROR' in stdout:
                self.error(iData,stdout)
            elif 'WARNING' in stdout:
                self.warning(iData,stdout)
            else:
                self.status(iData)
        self.p.communicate('EXIT\n')
        
    def error(self,file,stdout):
        print('ERROR: '+self.OutDir+'\\'+self.prefix+str(file)+self.suffix+' failed to process!!!')
        f = open(self.logFile,'a')
        f.write(stdout)
        f.close()
    def warning(self,file,stdout):
        print('WARNING: '+self.OutDir+'\\'+self.prefix+str(file)+self.suffix+' probably did not process correctly, because of some error in the given parameters or specified filenames. Please Check!')
        f = open(self.logFile,'a')
        f.write(stdout)
        f.close()
    def status(self,file):
        print('File '+self.prefix+str(file)+self.suffix+' done...')
        
class ReduceDataWBeamCenter(object):
#    def __init__(self,fit2Dexe,InDir,OutDir,List,Mask,Calib,prefix = 'im_00', suffix = '_craw.tiff',compute=True):
#        self.logFile = str(np.datetime64('today','D'))+'.log'
#        self.InDir = InDir
#        self.OutDir = OutDir
#        self.List = List
#        self.Mask = Mask
#        self.Calib = Calib
#        self.prefix = prefix
#        self.suffix = suffix
#        self.p = subprocess.Popen([fit2Dexe,"-com"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True,shell=False)
#        if compute:
#            self.compute()
    def __init__(self,prefix='im_00',suffix='_craw.tiff',InDirTrans=None,compute=True,**kwargs):
        self.logFile = str(np.datetime64('today','D'))+'.log'
        self.InDir = kwargs['InDir']
        self.InDirTrans = InDirTrans
        if InDirTrans is None:
            self.InDirTrans=self.InDir
        self.OutDir = kwargs['OutDir']
        self.List = kwargs['List']
        self.ListTrans = kwargs['ListTrans']
        self.Mask = kwargs['Mask']
        self.Calib = kwargs['Calib']
        self.fit2Dexe = kwargs['fit2Dexe']
        self.prefix = prefix
        self.suffix = suffix
        if compute:
            self.compute()
        
    def compute(self):
        parsed_string = ''
        p = subprocess.Popen([self.fit2Dexe,"-com"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True)
        for i,iData in enumerate(self.List):
            #p = subprocess.Popen([self.fit2Dexe,"-com"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True)
            #parsed_string = ''
            #print(self.InDirTrans+self.prefix+str(self.ListTrans[i])+self.suffix)
            parsed_string+='SAXS / GISAXS\nINPUT\n'+self.InDirTrans+self.prefix+str(self.ListTrans[i])+self.suffix+'\nMASK\nCLEAR MASK\nEXIT\n'
            parsed_string+='BEAM CENTRE\n2-D GAUSSIAN FIT\n1\n'+str(self.Calib['BeamXpix'])+'\n'+str(self.Calib['BeamYpix'])+'\n'
            parsed_string+='INPUT\n'+self.InDir+self.prefix+str(iData)+self.suffix+'\n'
            parsed_string+='MASK\nLOAD MASK\n'+self.Mask+'\nEXIT\n'
            parsed_string+='INTEGRATE\nX-PIXEL SIZE\n172.0\nY-PIXEL SIZE\n172.0\nDISTANCE\n'+str(self.Calib['SDD'])+'\nWAVELENGTH\n1.34\n'
            parsed_string+='TILT ROTATION\n0.0\nANGLE OF TILT\n0.0\nDETECTOR ROTATION\n0.0\n'
            parsed_string+='O.K.\nSCAN TYPE\nQ-SPACE\nCONSERVE INT.\nNO\nPOLARISATION\nNO\nGEOMETRY COR.\nYES\nSCAN BINS\n'+str(self.Calib['Bins'])+'\n'
            parsed_string+='PARAMETER FILE\n'+self.OutDir+str(iData)+'.par\nO.K.\nOUTPUT\nCHIPLOT\n'
            parsed_string+='FILE NAME\n'+self.OutDir+str(iData)+'.chi\nO.K.\nEXCHANGE\n'      
            parsed_string+='INTEGRATE\nX-PIXEL SIZE\n172.0\nY-PIXEL SIZE\n172.0\nDISTANCE\n'+str(self.Calib['SDD'])+'\nWAVELENGTH\n1.34\n'
            parsed_string+='TILT ROTATION\n0.0\nANGLE OF TILT\n0.0\nDETECTOR ROTATION\n0.0\n'
            parsed_string+='O.K.\nSCAN TYPE\nQ-SPACE\nCONSERVE INT.\nYES\nPOLARISATION\nNO\nGEOMETRY COR.\nNO\nSCAN BINS\n'+str(self.Calib['Bins'])+'\n'
            parsed_string+='PARAMETER FILE\n'+self.OutDir+str(iData)+'_Int.par\nO.K.\nOUTPUT\nCHIPLOT\n'
            parsed_string+='FILE NAME\n'+self.OutDir+str(iData)+'_Int.chi\nO.K.\nEXCHANGE\n' 
            #stdout= p.communicate(parsed_string)[0]
            #print(stdout.split('\n'))
            
#            if 'Error' in stdout:
#                self.error(iData,stdout)
#            elif 'WARNING' in stdout:
#                self.warning(iData,stdout)
#            else:
#                self.status(iData)
        p.communicate(parsed_string)
    def error(self,file,stdout):
        print('ERROR: '+self.OutDir+'\\'+self.prefix+str(file)+self.suffix+' failed to process!!!')
        f = open(self.logFile,'a')
        f.write(stdout)
        f.close()
    def warning(self,file,stdout):
        print('WARNING: '+self.OutDir+'\\'+self.prefix+str(file)+self.suffix+' probably did not process correctly, because of some error in the given parameters or specified filenames. Please Check!')
        f = open(self.logFile,'a')
        f.write(stdout)
        f.close()
    def status(self,file):
        pass
        #print('File '+self.prefix+str(file)+self.suffix+' done...')        
        
class GetStatData(object):
    def __init__(self,fit2Dexe,InDir,OutDir,List,prefix = 'im_00', suffix = '_craw.tiff',compute=True):
        self.logFile = str(np.datetime64('today','D'))+'.log'
        self.InDir = InDir
        self.OutDir = OutDir
        self.List = List
        self.prefix = prefix
        self.suffix = suffix
        self.fit2Dexe = fit2Dexe
        self.Int = []
        if compute:
            self.compute()
        
    def compute(self):
        for iData in self.List:
            p = subprocess.Popen([self.fit2Dexe,"-com"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True)
            parsed_string = ''
            parsed_string+='SAXS / GISAXS\nINPUT\n'+self.InDir+self.prefix+str(iData)+self.suffix+'\n'
            parsed_string+='MATHS\nSTATISTICS\nKEYBOARD\n0\n619\nKEYBOARD\n487\n0\nENTER COORDINATES TO DEFINE POLYGON REGION\n'
            parsed_string+='SAVE\n'+self.OutDir+str(iData)+'.txt\nO.K.\nEXIT\n'   
            stdout= p.communicate(parsed_string)[0]
            #stdout = subprocess.run([self.fit2Dexe,"-com"],stdout=subprocess.PIPE,input=parsed_string,encoding='ascii').stdout
            #self.p.stdin.write(parsed_string)
            #time.sleep(2)
            #stdout = self.p.stdout.read()
            #print(stdout.split('\n'))
            
            if 'ERROR' in stdout:
                self.error(iData,stdout)
                self.Int.append(np.nan)
            elif 'WARNING' in stdout:
                self.warning(iData,stdout)
                self.Int.append(np.nan)
            else:
                self.status(iData)   
                self.parseInt(iData)
        
    def parseInt(self,name):
        
        f = open(self.OutDir+name+'.txt','r')
        stdout=f.read()
        f.close()
        for iString in stdout.split('\n'):
            if 'Total intensity =' in iString:
                for jString in iString.split(' '):
                    #print(jString)
                    try:
                        self.Int.append(float(jString))
                        break
                    except: pass
    
    def getInt(self):
        return(self.Int)                            
                
    def error(self,file,stdout):
        print('ERROR: '+self.OutDir+'\\'+self.prefix+str(file)+self.suffix+' failed to process!!!')
        f = open(self.logFile,'a')
        f.write(stdout)
        f.close()
    def warning(self,file,stdout):
        print('WARNING: '+self.OutDir+'\\'+self.prefix+str(file)+self.suffix+' probably did not process correctly, because of some error in the given parameters or specified filenames. Please Check!')
        f = open(self.logFile,'a')
        f.write(stdout)
        f.close()
    def status(self,file):
        pass
        #print('File '+self.prefix+str(file)+self.suffix+' done...')


def main():
    import sys,os
    fit2Dexe = r"C:\Users\ZechT\Desktop\fit2d_beta_18_002_Windows7_intel32.exe"
    AgBehMacroPath = r"M:\Vaxster\181119_ILLProben\macro1600.my"
    if not os.path.isfile(AgBehMacroPath):
        c = AgBehCalib(fit2Dexe,r'M:\\Vaxster\\181119_ILLProben\\images\\im_0066708_craw.tiff',250)
    else:
        c = AgBehCalib(fit2Dexe,r'M:\\Vaxster\\181119_ILLProben\\images\\im_0066708_craw.tiff',250,
           macro=AgBehMacroPath)
    Calib1500 = c.getCalibration()
    InDir = r'M:\\Vaxster\\181119_ILLProben\\images\\'
    OutDir = r'C:\\Users\\ZechT\\Documents\\test\\data\\'
    StatOutDir = r'C:\\Users\\ZechT\\Documents\\test\\stat\\'
    Mask1500 = r'M:\\Vaxster\\181119_ILLProben\\181119_SDD1500_mask.msk'
    Mask150 = r'M:\\Vaxster\\181119_ILLProben\\181119_SDD150_mask.msk'
    
    ListID150 = [67101,66978,66981,66984,66987]
    ListID1500 = [67104,66993,66996,66999,67002]
    
    ListStat1500 = [67098,67099,66976,6977,66979,66980,66982,66983,66985,66986]
    ListStat150 = [67102,67103,66991,66992,66994,66995,66997,66998,67000,67001]
    
    r = ReduceData(fit2Dexe,InDir,OutDir,ListID1500,Mask1500,Calib1500)
    r = GetStatData(fit2Dexe,InDir,OutDir,ListStat1500)
    
if __name__ == "__main__":
    main()