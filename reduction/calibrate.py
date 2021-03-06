#!/usr/bin/python3.8

from PIL import Image
import hdf5plugin
import h5py

from scipy.optimize import curve_fit as cfit
from distutils.util import strtobool

import pyFAI

from os import listdir
from os.path import join, isfile
import sys

import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage 

import argparse

def gaussian(x,x0,sigma,maximum):
  dx = np.subtract(x,x0)
  quotient = -2*sigma**2
  exponent = np.divide(np.power(dx,2),quotient)
  return maximum*np.exp(exponent)

class Masks:
  def _saxans(self, data):
    """Creates a numpy array to be used as mask in pyFAI.
    
    The numpy array contains 0 for pixels that will be used and
    1 for pixels that are masked. The function automatically masks 
    all pixels with counts lower than 0 and the 3 dead pixels in
    the detector.
    """
    mask = np.array(data)
    mask[mask >= 0] = 0 
    mask[mask < 0] = 1 
    mask[666,388] = 1 
    mask[764,409] = 1 
    mask[1006,274] = 1 
    
    return mask

  def _saxspace(self, data):
    mask = np.array(self._twoddata)
    #y = 388
    #x = 398
    #print(mask[x,y])
    #print(mask[x-2:x+2,y-2:y+2])
    mask[mask >= 0] = 0
    mask[mask < 0] = 1
    mask2 = np.array(mask)
    
    radius = 30
    alpha = 45
    coordinates = []
    for x in range(-radius, radius, 1):
      for y in range(-radius, radius, 1):
        if x*x+y*y<=radius*radius:
          if (x>0) or (abs(y) > abs(x*np.tan(alpha*np.pi/180))):
            coordinates.append((x,y))
        
    coordinates = [(x+int(self._com[0])+1,y+int(self._com[1])) for (x,y) in coordinates]
    for (x,y) in coordinates:
      mask2[x,y] = 1000
      
    #plt.imshow(mask2)
    plt.imshow(np.log10(np.multiply(self._twoddata,np.multiply(-1,np.subtract(mask2,1)))))
    plt.show()
    
    #mask2[int(self._com[0])-10:int(self._com[0])+20, int(self._com[1])-10: int(self._com[1])+20] = 1
    #data_temp = np.multiply(self._twoddata, np.multiply(-1,np.subtract(mask2,1)))
    #mask[300,409] = 1 #mask[398,388] = 1 # Works only for my PC at home
    mask[666,388] = 1 
    mask[764,409] = 1 
    mask[1006,274] = 1 
    #mask[:int(self._com[0])]=1 # Works only for my PC at home
    mask[int(self._com[0])+1:]=1
    #np.save('mask.npy', mask)
    if self._VERBOSE:
      plt.imshow(np.log10(np.multiply(self._twoddata,np.multiply(-1,np.subtract(mask,1)))))
      plt.show()
    return mask
  
  def __init__(self, mask_type, data):
    self.supported_types = {'saxans': self._saxans,'saxspace': self._saxspace}
    if not(mask_type in self.supported_types.keys()):
      error_message = 'Supported mask types are:'
      for t in self.supported_types.keys:
        error_message += ' {}'.format(t)
      error_message += '.'
      raise ValueError(error_message)
    self.mask = self.supported_types[mask_type](data)
    
  def mask_outside_circle(self,com,radius):
    new_mask = self.mask
    x,y = self.mask.shape
    x_range = np.array(range(x))
    y_range = np.array(range(y))
    
    for x in x_range:
      for y in y_range:
        dx = x-com[0]
        dy = y-com[1]
        if dx*dx + dy*dy > radius*radius:
          new_mask[x][y]=1
          
    return new_mask

class DataSet:
  def _load_data(self, fn):
    files = [join(fn,f) for f in listdir(fn) 
              if (isfile(join(fn,f))) and (f.endswith('.tif')) and not(f.endswith('corrected.tif'))]

    if len(files) > 0:
      shape = np.array(Image.open(files[0])).shape
      result = np.zeros(shape)
      
      for data in files:
        im = Image.open(data)
        result = np.add(result, np.array(im))

      if self._VERBOSE:
        plt.imshow((result))
        plt.imshow(np.log(result))
        plt.show()
        
    else:
      raise ValueError('Path to data is empty.')
        
    return result
    
  def _gauss(self, x, x0, sigma, maximum):
    dx = np.subtract(x,x0)
    quotient = -2*sigma**2
    exponent = np.divide(np.power(dx,2),quotient)
    return maximum*np.exp(exponent)

  def _find_direct_beam(self):
    xDB = 0
    yDB = 0
    
    maxval = np.max(self._twoddata)
    maxcoord = np.where(self._twoddata == maxval)
    
    xprojection = np.sum(self._twoddata,1)
    yprojection = np.sum(self._twoddata,0)
    maxvalx = np.max(xprojection)
    maxvaly = np.max(yprojection)

    p0 = [maxcoord[0][0],2,maxvalx]
    x0 = list(range(len(xprojection)))
    p1 = [maxcoord[1][0],2,maxvaly]
    x1 = list(range(len(yprojection)))
    
    popt0, cov0 = cfit(f=self._gauss, xdata=x0, ydata=xprojection, p0=p0)
    popt1, cov1 = cfit(self._gauss, x1, yprojection, p1)
    
    if self._VERBOSE:
      points = 10000
      x0_plot = np.multiply(np.divide(list(range(points)),points),len(xprojection))
      x1_plot = np.multiply(np.divide(list(range(points)),points),len(yprojection))
      
      plt.plot(xprojection)
      plt.plot(x0_plot,self._gauss(x0_plot,*p0))
      plt.plot(x0_plot,self._gauss(x0_plot,*popt0))
      plt.xlim(maxcoord[0]-20,maxcoord[0]+20)
      plt.show()
      plt.plot(yprojection)
      plt.plot(x1_plot,self._gauss(x1_plot,*p1))
      plt.plot(x1_plot,self._gauss(x1_plot,*popt1))
      plt.xlim(maxcoord[1]-20,maxcoord[1]+20)
      plt.show()

    xDB = popt0[0]
    yDB = popt1[0]

    return (xDB,yDB)
  
  def _create_mask(self):
    mask = np.array(self._twoddata)
    #y = 388
    #x = 398
    #print(mask[x,y])
    #print(mask[x-2:x+2,y-2:y+2])
    mask[mask >= 0] = 0
    mask[mask < 0] = 1
    mask2 = np.array(mask)
    
    radius = 30
    alpha = 45
    coordinates = []
    for x in range(-radius, radius, 1):
      for y in range(-radius, radius, 1):
        if x*x+y*y<=radius*radius:
          if (x>0) or (abs(y) > abs(x*np.tan(alpha*np.pi/180))):
            coordinates.append((x,y))
        
    coordinates = [(x+int(self._com[0])+1,y+int(self._com[1])) for (x,y) in coordinates]
    for (x,y) in coordinates:
      mask2[x,y] = 1000
      
    #plt.imshow(mask2)
    plt.imshow(np.log10(np.multiply(self._twoddata,np.multiply(-1,np.subtract(mask2,1)))))
    plt.show()
    
    #mask2[int(self._com[0])-10:int(self._com[0])+20, int(self._com[1])-10: int(self._com[1])+20] = 1
    #data_temp = np.multiply(self._twoddata, np.multiply(-1,np.subtract(mask2,1)))
    #mask[300,409] = 1 #mask[398,388] = 1 # Works only for my PC at home
    mask[666,388] = 1 
    mask[764,409] = 1 
    mask[1006,274] = 1 
    #mask[:int(self._com[0])]=1 # Works only for my PC at home
    mask[int(self._com[0])+1:]=1
    #np.save('mask.npy', mask)
    if self._VERBOSE:
      plt.imshow(np.log10(np.multiply(self._twoddata,np.multiply(-1,np.subtract(mask,1)))))
      plt.show()
    return mask
  
  def _write_poni(self, distance):
    with open(self._CALIB, 'w') as of:
      of.write('#pyFAI Calibration file constructed manually\n')
      of.write('#Created never...\n')
      of.write('poni_version: 2\n')
      of.write('Detector: Detector\n')
      of.write('Detector_config: {"pixel1": 7.5e-5, "pixel2": 7.5e-5, "max_shape": null}\n')
      of.write('Distance: {}\n'.format(distance))
      of.write('Poni1: {}\n'.format(self._com[0]*7.5e-5))
      of.write('Poni2: {}\n'.format(self._com[1]*7.5e-5))
      of.write('Rot1: 0\n')
      of.write('Rot2: 0\n')
      of.write('Rot3: 0\n')
      of.write('Wavelength: 1.5406e-10\n')

  def _integrateoned(self,distance, outp):
    self._write_poni(distance)
    ai = pyFAI.load(self._CALIB)
    res1000 = ai.integrate1d(self._twoddata, 1000, unit='q_nm^-1', mask = self._mask, 
                         filename='{}_1000bins.dat'.format(outp), error_model = 'poisson')
    res = ai.integrate1d(self._twoddata, 100, unit='q_nm^-1', mask = self._mask, 
                         filename='{}_100bins.dat'.format(outp), error_model = 'poisson')
    res = ai.integrate1d(self._twoddata, 200, unit='q_nm^-1', mask = self._mask,
                         filename='{}_200bins.dat'.format(outp), error_model = 'poisson')
    return res1000

  def __init__(self, params):
    self._CALIB = 'temp.poni'
    self._VERBOSE = params['verbose']
    
    self._paramlist = ['cf', 'thickness', 'path', 'distance', 'output']
    for i in self._paramlist:
      if not i in params:
        raise ValueError('Parmeters need the following components: {}'.format(self._paramlist)) 
    
    self._twoddata = self._load_data(params['path'])
    
    self._com = self._find_direct_beam() 
    self._mask = self._create_mask() 
    
    self._imagesum = np.sum(np.multiply(self._twoddata,np.multiply(-1,np.subtract(self._mask,1))))
    self._twoddata = np.multiply(self._twoddata, params['cf']/(self._imagesum*params['thickness']))
    
    self._oneddata = self._integrateoned(params['distance'], params['output'])
    
  def image(self):
    return self._twoddata
  
  def curve(self):
    return self._oneddata
  
  def plot_image(self):
    plt.imshow(self._twoddata)
    plt.show()
    
  def plot_curve(self):
    plt.plot(self._oneddata[0], self._oneddata[1])
    plt.show()
    
  def plot_logcurve(self):
    plt.loglog(self._oneddata[0], self._oneddata[1])
    plt.show()

class Workload:
  def _init_setups(self, setup_file):
    _setups = {}
    if not(isfile(setup_file)):
      raise ValueError('The chosen setup file does not exist.')
    else:
      _qualifiers = ['--setup-name', '--sample-detector-distance', '--calibration-factor', '--file-path', '--mask-radius', '--mask-shift-y', '--mask-shift-x']
      with open(setup_file, 'r') as f:
        for line in f:
          if not(line.startswith('#')):
            if line.startswith('!'):
              line = line[1:]
              _qualifiers = list(line.strip().split(','))
            else:
              _setups.update(self._parse_setup(_qualifiers, line))
    return _setups
              
  def _parse_setup(self, qualifiers, line):
    line = list(line.strip().split(','))
    parsing_args = np.array(list(zip(qualifiers,line))).flatten()
    
    parser = argparse.ArgumentParser(description='Parses the setup inputs.')
    
    parser.add_argument('--setup-name', type=str, default ='placeholder setup')
    parser.add_argument('--sample-detector-distance', type=float, default = 1)
    parser.add_argument('--calibration-factor', type=float, default=1)
    parser.add_argument('--file-path', type=str, default='./')
    parser.add_argument('--mask-radius', type=int)
    parser.add_argument('--mask-shift-x', type=int, default=0)
    parser.add_argument('--mask-shift-y', type=int, default=0)
    parser.add_argument('--empty-beam', type=int, default=-1)
      
    args = parser.parse_args(parsing_args)
    
    result = ['-sdd', '{}'.format(args.sample_detector_distance), '-cf', '{}'.format(args.calibration_factor), '-p', args.file_path, '-msx', '{}'.format(args.mask_shift_x), '-msy', '{}'.format(args.mask_shift_y), '-eb', '{}'.format(args.empty_beam)]
    if args.mask_radius:
      result = result+['-r', '{}'.format(args.mask_radius)]
    return {args.setup_name: result}
  
  def _init_workload(self, data_file):
    _workload = {}
    if not(isfile(data_file)):
      raise ValueError('The chosen data file does not exist.')
    else:
      _qualifiers=['--sample-name', '--xdet', '--xstart', '--xend', '--gamma-start', '--gamma-end', '--integration-type']
      with open(data_file, 'r', encoding ='utf-8-sig') as f:
        for line in f:
          if not(line.startswith('#')) :
            print(line)
            if line.startswith('!'):
              line = line[1:]
              _qualifiers = list(line.strip().split(','))
            else:
              new_workload = self._parse_workload(_qualifiers,line)
              if not (0 in new_workload.keys()):
                new_sample = list(new_workload.keys())[0]
                if new_sample in _workload.keys():
                  new_sample_name = self._iterate_sample_name(_workload.keys(), new_sample)
                  _workload.update({new_sample_name: new_workload[new_sample]})
                else:
                  _workload.update(new_workload)
    return _workload
  
  def _iterate_sample_name(self, keys, sample_name):
    new_sample_name = sample_name
    while new_sample_name in keys:
      name_elements = new_sample_name.split('_')
      number = int(name_elements[-1])
      new_sample_name = '{}_{}_{:04d}'.format(name_elements[0], name_elements[1], number+1)
    return new_sample_name
  
  def _clean_parsing_args(self,args):
    args = list(args)
    while('----' in args):
      position = args.index('----')
      args.pop(position)
      args.pop(position-1)
    while('' in args):
      position = args.index('')
      args.pop(position)
      args.pop(position-1)
    while('-' in args):
      position = args.index('-')
      args.pop(position)
      args.pop(position-1)
      
    return np.array(args)
  
  def _parse_workload(self,qualifiers,line):
    line = list(line.strip().split(','))
    parsing_args = np.array(list(zip(qualifiers,line))).flatten()
    parsing_args = self._clean_parsing_args(parsing_args)
    
    print(parsing_args)
    parser = argparse.ArgumentParser(description='Parses the data file input.')
    
    parser.add_argument('--sample-name', type=str, default='no-name-given')
    parser.add_argument('--setup-name', type=str, default='no-name-given')
    parser.add_argument('--xdet', type=float, default = -1)
    parser.add_argument('--xstart', type=int, default = -1)
    parser.add_argument('--xend', type=int, default = -1)
    parser.add_argument('--gamma-start', type=int, default = -1)
    parser.add_argument('--gamma-end', type=int, default = -1)
    parser.add_argument('--integration-type', type=str, default='each', choices=['each', 'mean'])
    
    args = parser.parse_args(parsing_args)
    
    if (args.xstart == -1 and args.xend == -1) or (args.xdet == -1):
      print('Not enough input, skipping line: {}'.format(line))
      return {0:0}
    if (args.sample_name == 'no-name-given'):
      if args.xstart == -1:
        args.sample_name = '{}'.format(args.xend)
      else:
        args.sample_name = '{}'.format(args.xstart)
    if (args.setup_name == 'no-name-given'):
      args.setup_name = '{}'.format(int(args.xdet))
    if args.xstart == -1:
      args.xstart = args.xend
    if args.xend == -1:
      args.xend = args.xstart
    
    setup = self._setups[args.setup_name]
    result = ['-xs', '{}'.format(args.xstart),
              '-xe', '{}'.format(args.xend),
              '-t', args.integration_type] + setup
    if not(args.gamma_start == -1 and args.gamma_end == -1):
      if args.gamma_start == -1:
        args.gamma_start == args.gamma_end
      elif args.gamma_end ==-1:
        args.gamma_end = args.gamma_start
      result = result + ['-gs', '{}'.format(args.gamma_start),
                         '-ge', '{}'.format(args.gamma_end)]
      
    return {'{}_{}_0001'.format(args.sample_name, args.setup_name): result}
      
  def __init__(self, setup_file, data_file):
    self._setups = self._init_setups(setup_file)
    self._workload = self._init_workload(data_file)
    
  def setups(self):
    return self._setups

  def workload(self):
    return self._workload
    
class SAXANSCalibrator:
  def _init_calibrator(self, name, params):
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-xs', type=int)
    parser.add_argument('-xe', type=int)
    parser.add_argument('-gs', type=int,default=-1)
    parser.add_argument('-ge', type=int,default=-1)
    parser.add_argument('-sdd', type=float)
    parser.add_argument('-cf', type=float)
    parser.add_argument('-p', type=str)
    parser.add_argument('-o', type=str)
    parser.add_argument('-t', type=str)
    parser.add_argument('-v', type=str, default='False', choices=['False', 'True'])
    parser.add_argument('-r', type=int)
    parser.add_argument('-msx', type=int)
    parser.add_argument('-msy', type=int)
    parser.add_argument('-eb', type=int)
    
    args = parser.parse_args(params)
    
    self._NAME = name
    self._XSTART = args.xs
    self._XEND = args.xe
    self._GSTART = args.gs
    self._GEND = args.ge
    self._SDD = args.sdd
    self._SOLID_ANGLE = 75e-6*75e-6/(self._SDD*self._SDD)
    self._CF = args.cf
    self._PATH = args.p
    self._VERBOSE = strtobool(args.v)
    self._INTEGRATION_TYPE = args.t
    self._CALIB = 'temp.poni'
    self._OUTP = args.o
    self._MASK_RADIUS = args.r
    self._MASK_SHIFT_X = args.msx
    self._MASK_SHIFT_Y = args.msy
    self._COM = self._find_direct_beam()
    if args.eb == -1:
      self._EB_FLUX = None
    else:
      self._EB_FLUX = self._calculate_flux(args.eb)
    
  def _calculate_flux(self,number):
    data,xdet,time = self._load_data(number)
    mask = self._create_mask(data)
    return np.sum(np.multiply(data,np.multiply(np.subtract(mask,1),-1)))/time
  
  def _load_data(self, number):
    full_path = join(self._PATH, '{:06d}_master.h5'.format(number))
    print(full_path)
    if not isfile(full_path):
      raise ValueError('The given file does not exist.')
    with h5py.File(full_path) as f:
      wavelength = f['entry/instrument/beam/incident_wavelength'][()]
      time = f['entry/instrument/detector/count_time'][()]
      data = np.zeros((1062,1028))
      for DATAFILE in f['entry/data'].keys():
        new_data = np.array(f['entry/data/{}'.format(DATAFILE)][()])
        frames = new_data.shape[0]
        new_data = np.sum(new_data, 0)
        new_data[new_data == int(np.iinfo(np.uint32).max*frames)] = -1
        new_data = new_data.astype(np.int64)
        data = np.add(data, new_data)
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
    maxcoord = np.argwhere(image == maxval)
    maxcoord = maxcoord.flatten()
    
    xprojection = np.sum(image,1)
    yprojection = np.sum(image,0)
    maxvalx = np.max(xprojection)
    maxvaly = np.max(yprojection)

    p0 = [maxcoord[0],2,maxvalx]
    x0 = list(range(len(xprojection)))
    p1 = [maxcoord[1],2,maxvaly]
    x1 = list(range(len(yprojection)))
    
    popt0, cov0 = cfit(gaussian, x0, xprojection, p0)
    popt1, cov1 = cfit(gaussian, x1, yprojection, p1)
    
    if self._VERBOSE:
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
    totalsum = 0 
    totaltime = 0 
    totalpixels = 0 
    result = 0
    if self._GSTART==-1 and self._GEND==-1:
      self._GAMMABG=0
    else:
      if self._GSTART==-1:
        self._GSTART=self._GEND
      elif self._GEND==-1:
        self._GEND=self._GSTART
        
      files = range(self._GSTART, self._GEND+1)

      for number in files:
        data, time = self._load_data(number)
        
        mask = self._create_mask(data)
        totalpixels += len(mask[np.where(mask==0)])
        rev_mask = np.multiply(np.subtract(mask,1),-1)
        data = np.multiply(data, rev_mask)
        
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
    mask = Masks('saxans', data)
    if self._MASK_RADIUS:
      center = (self._COM[1]+self._MASK_SHIFT_Y,self._COM[0]+self._MASK_SHIFT_X)
      mask = mask.mask_outside_circle(center,self._MASK_RADIUS)
    else:
      mask = mask.mask
    
    return mask
  
  def _integrate_each(self):
    result =[]
    for number in range(self._XSTART,self._XEND+1):
      data,time = self._load_data(number)
      
      mask = self._create_mask(data)
      rev_mask = np.multiply(np.subtract(mask,1),-1)
      
      transmitted_intensity = np.sum(np.multiply(data,rev_mask))
      thickness = np.sqrt(2) #TODO Add a way to define this in config file
      
      data = np.subtract(data, self._GAMMABG*time)
      data = np.divide(data,thickness*transmitted_intensity*self._SOLID_ANGLE)
      data = np.multiply(data,self._CF)
      
      name = '{}_{:08d}'.format(self._NAME,number)
      output = join(self._OUTP,name)
      result.append(self._integrate_image(data,mask,output))
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
    thickness = np.sqrt(2) #TODO Add a way to define this in config file
    
    sumdata = np.subtract(sumdata, self._GAMMABG*totaltime)
    sumdata = np.divide(sumdata,thickness*transmitted_intensity*self._SOLID_ANGLE)
    sumdata = np.multiply(sumdata,self._CF)
    
    if self._VERBOSE:
      plt.imshow(np.log(sumdata))
      plt.scatter(self._COM[1],self._COM[0],c='red', marker='x')
      plt.show()
      plt.clf()
      plt.imshow(np.log(np.multiply(sumdata,rev_mask)))
      plt.show()
    
    name = '{}_mean'.format(self._NAME)
    output = join(self._OUTP, name)
    result = self._integrate_image(sumdata,mask,output)
    
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
  
  def __init__(self, name, params):
    self._init_calibrator(name, params)
    self._calculate_gamma_background()
    self._write_poni()
    
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
  def _init_parameters(self, params):
    self._ALLOWED_TYPES = {'saxans':SAXANSCalibrator}
    parser = argparse.ArgumentParser()
    
    parser.add_argument('setup', type=str, help='File containing the setups that will be loaded.')
    parser.add_argument('data', type=str, help='File containing the formatted data information.')
    parser.add_argument('-v', '--verbose', type=bool, help='Display steps along the way.', default=False, const=True, nargs='?')
    parser.add_argument('-t', '--type', type=str,
                        help='Which SAXS data is to be refined.', 
                        default = 'saxans',
                        choices=list(self._ALLOWED_TYPES.keys()))
    parser.add_argument('-o', '--output', type=str, default = './',
                        help='Path were the outputs will be saved.')
    
    args = parser.parse_args(params)
    self._SETUP = args.setup
    self._DATA = args.data
    self._VERBOSE = args.verbose
    self._TYPE = args.type
    self._OUTP = args.output
  
  def __init__(self, params):
    self._init_parameters(params)
    self.workload = Workload(self._SETUP, self._DATA)
    
    if self._VERBOSE:
      print(self.workload.setups())
      print(self.workload.workload())
  
  def work(self):
    for data in self.workload.workload().keys():
      work = self.workload.workload()[data]+['-v',str(self._VERBOSE), '-o', self._OUTP]
      integrator = SAXANSCalibrator(data, work)
      result = integrator.integrate()

if __name__ == '__main__':

  c = Worker(sys.argv[1:])
  c.work()
