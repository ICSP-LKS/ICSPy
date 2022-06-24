# -*- coding: utf-8 -*-

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import subprocess
import time as time

class AgBehCalib(object):
    
    def __init__(self,type,file,SDD,points=None,macro=None,newMacro=False):
        if type=='Fit2D':
            self.fit2Dexe = 'fit2d_beta_18_002_Windows7_intel32.exe'
            
        self.AgBeh = file
        self.Calibration = {}
        self.logFile = str(np.datetime64('today','D'))+'.log'
        self.fit2Dexe = fit2Dexe
        self.MacroPath = macro
        if not newMacro:
            self.parse(macro)
        else:
            self.SDD = SDD
            self.points = points
            self.length=0
            
            self.fig = plt.figure()
            self.ax = self.fig.add_subplot(111)
            def Finished(event):
                if self.length>10:
                    self.compute()
            axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
            self.bnext = Button(axnext, 'Finish (>15 points)')        
            self.bnext.on_clicked(Finished)    
                
            if points is None:
                self.points=[]
                self.getPoints()

    def downloadFit2D(self):
        urlWindows="http://ftp.esrf.eu/pub/expg/FIT2D/fit2d_beta_18_002_Windows7_intel32.exe"
        urlLinux="hhttp://ftp.esrf.eu/pub/expg/FIT2D/fit2d_beta_18_002_Debian7_intel64"
        if sys.platform == 'win32':
            subprocess.call(urlWindows,shell=True)
        else:
            subprocess.call(urlLinux,shell=True)

    def setFit2Dexe(self,exe):
        self.fit2Dexe = exe
            
    def getPoints(self):
        
        def onclick(event):   
            if event.dblclick:
                print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                      ('double' if event.dblclick else 'single', event.button,
                       event.x, event.y, event.xdata, event.ydata))
                self.ax.plot(event.xdata,event.ydata,marker='x',ls='',color='red',markersize='5')
                plt.draw()
                self.points.append(event.xdata)
                self.points.append(event.ydata)
                self.length+=1
        
        im = Image.open(self.AgBeh)
        self.fig.canvas.mpl_connect('button_press_event', onclick)        
        image = np.flipud(np.array(im))
        self.ax.imshow(np.log10(image))      
        
    def showPoints(self):
        im = Image.open(self.AgBeh)
        image = np.flipud(np.array(im))
        self.ax.imshow(np.log10(image)) 
        points=self.parsePoints()
        arrPoints = []
#        for i in range(len(points[11:])/2):
#            arrPoints.append([float(points[i*2]),float(points[i*2+1])])
#        arrPoints=np.array(arrPoints)
#        print(arrPoints)
#        self.ax.plot(arrPoints[:,0],arrPoints[:,1],marker='x',ls='',color='red',markersize='5')
#        plt.draw()
    
    def parsePoints(self,string=None):
        if string is None:
            string=self.points
        strPoints = ''
        for iP in string:
            strPoints+=str(iP)+'\n'
        return strPoints
        
    def compute(self):
        p = subprocess.Popen([self.fit2Dexe,"-com"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True)
        parsed_string = ''
        parsed_string+='SAXS / GISAXS\nINPUT\n'+self.AgBeh+'\n'
        parsed_string+='Z-SCALING\nLOG SCALE\nEXIT\nCALIBRANT\nSILVER BEHENATE\nDISTANCE\n'+str(self.SDD)+'\n'
        parsed_string+='WAVELENGTH\n1.34\nREFINE WAVELENGTH\nNO\nX-PIXEL SIZE\n172\nY-PIXEL SIZE\n172\nREFINE BEAM X/Y\nYES\nREFINE DISTANCE\nYES\nO.K.\n'+str(self.length)+'\n'
        parsed_string+=self.parsePoints()  
        parsed_string+='EXIT\n'
        stdout= p.communicate(parsed_string)[0]
        #print(stdout.split('\n')[165:])
        f = open(self.MacroPath,'w')
        f.write(parsed_string)
        f.close()
        self.extractParams(stdout)

    def parse(self,macro):
        #self.showPoints()
        p = subprocess.Popen([self.fit2Dexe,"-com"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,universal_newlines=True)
        parsed_string = open(macro,'r').read()        
        stdout= p.communicate(parsed_string)[0]
        self.extractParams(stdout)
    
    def extractParams(self,stdout):
        #print(stdout.split('\n'))
        if 'ERROR' in stdout:
                self.error(self.AgBeh,stdout)
        elif 'WARNING' in stdout:
            self.warning(self.AgBeh,stdout)
        else:
            self.status(self.AgBeh)
        beamPos = []
        sdd = []
        for iString in stdout.split('\n'):
            if 'INFO: Refined Beam centre =' in iString:
                beamPos.append(iString)
            if 'INFO: Refined sample to detector distance =' in iString:
                sdd.append(iString)
        for iString in sdd[-1].split(' '):
            try:
                self.Calibration['SDD'] = float(iString)
            except: pass
        beamCenterStrings = ['BeamXpix','BeamYpix','BeamXmm','BeamYmm']
        for iString in beamPos[-2].split(' '):
            try: 
                FL = float(iString)
                self.Calibration[beamCenterStrings.pop(0)]=FL
            except: pass
        for iString in beamPos[-1].split(' '):
            try: 
                FL = float(iString)
                self.Calibration[beamCenterStrings.pop(0)]=FL
            except: pass

        print(self.Calibration)
        
    def getCalibration(self):
        return self.Calibration
    

    def error(self,file,stdout):
        print('ERROR: '+str(file)+' failed to process!!! SDD calibration is probably incorrect!!! look up logfile: '+self.logFile)
        f = open(self.logFile,'a')
        f.write(stdout)
        f.close()
    def warning(self,file,stdout):
        print('WARNING: '+str(file)+' probably did not process correctly, because of some error in the given parameters or specified filenames. Please Check! SDD calibration may be incorrect! look up logfile: '+self.logFile)
        f = open(self.logFile,'a')
        f.write(stdout)
        f.close()
    def status(self,file):
        print('File '+str(file)+' was used to calibrate SDD...')