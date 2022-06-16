# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 08:42:54 2021

@authors: GoetzK, ZechT
"""

import os,sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit as cfit
from matplotlib.colors import LogNorm

import pyFAI

import argparse

import hdf5plugin
import h5py
import PIL as Image

def gaussian(x,x0,sigma,maximum):
    dx = np.subtract(x,x0)
    quotient = -2*sigma**2
    exponent = np.divide(np.power(dx,2),quotient)
    return maximum*np.exp(exponent)

class SAXANSCalibrator:

    def __init__(self,data,kwargs):
        
        self._init_calibrator(data,**kwargs)
        self._calculate_gamma_background()
        self._write_poni()
        
    def _init_calibrator(self,data,setup,inpt,output,verbose):        
        
        self._CALIB = 'temp.poni'
        self._OUTP = output
        self._VERBOSE = verbose
        self._NAME = data['name']
        self._XDET = data['xdet']
        self._XSTART = int(data['xraystart'])
        self._XEND = int(data['xrayend'])
        self._GSTART = int(data['gammastart'])
        self._GEND = int(data['gammaend'])
        self._THICKNESS = float(data['thickness'])
        self._INTEGRATION_TYPE = data['integration-type']
        self._SDD = setup['sdd'][self._XDET].astype(float)
        self._CF = setup['cf'][self._XDET].astype(float)
        
        if os.path.isdir(inpt):
            self._PATH = inpt
        else:            
            self._PATH = setup['file-path'][self._XDET]

        if 'empty-beam' in setup:
            self._EB_FLUX = self._calculate_flux(setup['empty-beam'][self._XDET].astype(int))
        else:
            self._EB_Flux = None
            
        if 'beamposx' in setup and 'beamposy' in setup:
            self._COM = [float(setup['beamposx'][self._XDET]),float(setup['beamposy'][self._XDET])]
        else:
            self._COM = self._find_direct_beam()            
        
    def _calculate_flux(self,number):
        data,time = self._load_data(number)
        mask = self._create_mask(data)
        return np.sum(np.multiply(data,np.multiply(np.subtract(mask,1),-1)))/time
    
    def _load_data(self, number):
        full_path = os.path.join(self._PATH, '{:06d}_master.h5'.format(number))
        if not os.path.isfile(full_path):
            raise ValueError('The given file does not exist.')
        with h5py.File(full_path,'r') as f:
            wavelength = f['entry/instrument/beam/incident_wavelength'][()]
            time = f['entry/instrument/detector/count_time'][()]
            data = np.zeros((1062,1028))
            for DATAFILE in f['entry/data'].keys():
                new_data = np.array(f['entry/data/{}'.format(DATAFILE)][()],dtype=np.int)
                #print(type(np.array(f['entry/data/{}'.format(DATAFILE)][()],dtype=np.uint64))
                #frames = new_data.shape[0]
                new_data = np.sum(new_data, 0)
                #new_data[new_data == int(np.iinfo(np.int32).max*frames)] = -1
                new_data = new_data.astype(int)
                data = np.add(data, new_data)
                im = Image.Image.fromarray(data)
                im.save(os.path.join(os.path.dirname(self._PATH),'tiffimages\{:06d}_master.tiff'.format(number)))
        return data, time
    
    def _find_direct_beam(self):
        xDB = 0
        yDB = 0
        
        image,time = self._load_data(self._XSTART)
        
        if self._VERBOSE:
            plt.imshow(np.log(image))
            plt.show()
            plt.clf()
        
        maxval = np.max(image)
        maxcoord = np.where(image == maxval)
        
        xprojection = np.sum(image,1)
        yprojection = np.sum(image,0)
        maxvalx = np.max(xprojection)
        maxvaly = np.max(yprojection)

        p0 = [maxcoord[0][0],2,maxvalx]
        x0 = list(range(len(xprojection)))
        p1 = [maxcoord[1][0],2,maxvaly]
        x1 = list(range(len(yprojection)))
        
        popt0, cov0 = cfit(gaussian, x0, xprojection, p0)
        popt1, cov1 = cfit(gaussian, x1, yprojection, p1)
        
        if self._VERBOSE:
            plt.close('all')
            plt.title('data with direct beam')
            points = 10000
            x0_plot = np.multiply(np.divide(list(range(points)),points),len(xprojection))
            x1_plot = np.multiply(np.divide(list(range(points)),points),len(yprojection))
            
            plt.plot(xprojection, label='data')
            plt.plot(x0_plot,gaussian(x0_plot,*p0),label='start value')
            plt.plot(x0_plot,gaussian(x0_plot,*popt0), label='fit')
            plt.xlim(maxcoord[0]-20,maxcoord[0]+20)
            plt.legend()
            plt.show()
            plt.plot(yprojection, label='data')
            plt.plot(x1_plot,gaussian(x1_plot,*p1),label='start value')
            plt.plot(x1_plot,gaussian(x1_plot,*popt1), label='fit')
            plt.xlim(maxcoord[1]-20,maxcoord[1]+20)
            plt.legend()
            plt.show()
            
            plt.clf()
            plt.imshow(np.log(image))
            print('{} {}'.format(popt0[0],popt1[0]))
            plt.scatter(popt1[0],popt0[0],c='red', marker='x')
            plt.show()

        xDB = popt0[0]
        yDB = popt1[0]

        return (xDB,yDB)
    
    def _calculate_gamma_background(self):
        if self._GSTART==-1 and self._GEND==-1:
            self._GAMMABG=0
        else:
            if self._GSTART==-1:
                self._GSTART=self._GEND
            elif self._GEND==-1:
                self._GEND=self._GSTART
                
            files = range(self._GSTART, self._GEND)
            print(files)
            totalsum = 0 
            totaltime = 0 
            totalpixels = 0 

            for number in files:
                data, time = self._load_data(number)
                
                mask = self._create_mask(data)
                totalpixels += len(mask[np.where(mask==0)])
                rev_mask = np.multiply(np.subtract(mask,1),-1)
                data = np.multiply(data, rev_mask)
                if self._VERBOSE:
                    plt.close('all')
                    print('plotting BG')
                    plt.title('GammaBG')
                    plt.imshow(data)
                    plt.show()
                totaltime += time
                totalsum += np.sum(data)

            result = totalsum/(totaltime*totalpixels)
            self._GAMMABG = result

        if self._VERBOSE:
            print('Sum: {}'.format(totalsum))
            print('Time: {}'.format(totaltime))
            print('Pixels: {}'.format(totalpixels))
            print('Counts per pixel per second: {}'.format(result))

    
    def _write_poni(self):
        with open(self._CALIB, 'w') as of:
            of.write('#pyFAI Calibration file constructed manually\n')
            of.write('#Created never...\n')
            of.write('poni_version: 2\n')
            of.write('Detector: Detector\n')
            of.write('Detector_config: {"pixel1": 7.5e-5, "pixel2": 7.5e-5, "max_shape": null}\n')
            of.write('Distance: {}\n'.format(self._SDD))
            of.write('Poni1: {}\n'.format(self._COM[0]*7.5e-5))
            of.write('Poni2: {}\n'.format(self._COM[1]*7.5e-5))
            of.write('Rot1: 0\n')
            of.write('Rot2: 0\n')
            of.write('Rot3: 0\n')
            of.write('Wavelength: 1.5406e-10\n')
    
    def _create_mask(self, data):
        mask = np.zeros(shape=np.shape(data))
        mask[data < 0] = 1 
        mask[666,388] = 1 
        mask[764,409] = 1 
        mask[1006,274] = 1 
          
        return mask
    
    def _integrate_each(self):
        result =[]
        for number in range(self._XSTART,self._XEND+1):
            data,time = self._load_data(number)
            
            mask = self._create_mask(data)
            rev_mask = np.multiply(np.subtract(mask,1),-1)
            
            transmitted_intensity = np.sum(np.multiply(data,rev_mask))
            thickness = np.sqrt(2)*self._THICKNESS
            
            data = np.subtract(data, self._GAMMABG*time)
            data = np.divide(data,thickness*transmitted_intensity)
            data = np.multiply(data,self._CF)
            
            name = '{}_{:08d}'.format(self._NAME,number)
            output = os.path.join(self._OUTP,name)
            result.append(self._integrate_image(data,mask,output))
            print("\t...subfile {} integrated...".format(name))
        return result
        
    def _integrate_mean(self):
        result = 0
        sumdata = 0
        totaltime = 0
        
        for number in range(self._XSTART,self._XEND+1):
            data,time = self._load_data(number)
            totaltime += time
            if number == self._XSTART:
                sumdata=data
            else:
                sumdata = np.add(sumdata,data)
       
        mask = self._create_mask(data)
        rev_mask = np.multiply(np.subtract(mask,1),-1)
        
        transmitted_intensity = np.sum(np.multiply(sumdata,rev_mask))
        thickness = np.sqrt(2)*self._THICKNESS
        
        sumdata = np.subtract(sumdata, self._GAMMABG*totaltime)
        if self._VERBOSE:
            plt.close('all')
            plt.title('data after mask')
            plt.imshow(np.log(sumdata))
            plt.scatter(self._COM[1],self._COM[0],c='red', marker='x')
            plt.show()
            plt.clf()
            plt.imshow(np.log(np.multiply(sumdata,rev_mask)))
            plt.show()
        sumdata = np.divide(sumdata,thickness*transmitted_intensity)
        sumdata = np.multiply(sumdata,self._CF)
        
        if self._VERBOSE:
            plt.imshow(np.log(sumdata))
            plt.title('data after correction')
            plt.scatter(self._COM[1],self._COM[0],c='red', marker='x')
            plt.show()
            plt.clf()
            plt.imshow(np.log(np.multiply(sumdata,rev_mask)))
            plt.show()
        
        name = '{}_{:08d}'.format(self._NAME,self._XSTART)
        output = os.path.join(self._OUTP, name)
        result = self._integrate_image(sumdata,mask,output)
        
        return(result)
        
    def _integrate_image(self, image, mask, outp):    
        ai = pyFAI.load(self._CALIB)
        #TODO Implement way to put bins into config
        res1000 = ai.integrate1d(image, 1000, unit='q_A^-1', mask = mask, 
                                                 filename='{}_1000bins.dat'.format(outp), error_model = 'poisson')
        res = ai.integrate1d(image, 100, unit='q_A^-1', mask = mask, 
                                                 filename='{}_100bins.dat'.format(outp), error_model = 'poisson')
        res = ai.integrate1d(image, 200, unit='q_A^-1', mask = mask,
                                                 filename='{}_200bins.dat'.format(outp), error_model = 'poisson')
        return res1000    
        
    def integrate(self):
        self.print_info()
        if self._INTEGRATION_TYPE == 'mean':
            result = self._integrate_mean()
        elif self._INTEGRATION_TYPE == 'each':
            result = self._integrate_each()
            
        return result
    
    def print_info(self):
        text = 'Reducing sample {}:\n'.format(self._NAME)
        if self._EB_FLUX:
            text += 'Transmission: {}'.format(self._calculate_flux(self._XSTART)/self._EB_FLUX)
        else:
            text += 'No empty beam, Transmission calculation not possible.'
        
        print(text)   

class Worker:
    
    def __init__(self, params):
        
        self._ALLOWED_TYPES = {'saxans':SAXANSCalibrator}
        parser = argparse.ArgumentParser()
        
        parser.add_argument('setup', type=str, help='File containing the setups that will be loaded.')
        parser.add_argument('data', type=str, help='File containing the formatted data information.')
        parser.add_argument('-v', '--verbose', type=bool, help='Display steps along the way.', default=False, const=True, nargs='?')
        
        parser.add_argument('-o', '--output', type=str, default = './',
                                                help='Path were the outputs will be saved.')
        parser.add_argument('-i', '--input', type=str, default = 'None',
                                                help='Path were the outputs will be saved.')
        
        args = parser.parse_args(params)
        self._DATA = pd.read_csv(args.data)
        self._kwargs = {'setup' : pd.read_csv(args.setup,skiprows=1,index_col='setup-name'),
                        'inpt' : args.input,
                        'output' : args.output,
                        'verbose' : args.verbose}
    
    def work(self):
        for index,data in self._DATA.iterrows():
            print("reducing data {}...".format(data['name']))
            integrator = SAXANSCalibrator(data, self._kwargs)
            integrator.integrate()
            print("... reducing of data {} finished!".format(data['name']))

if __name__ == '__main__':    

    c = Worker(sys.argv[1:])
    c.work()