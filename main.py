# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 01:30:18 2019

@author: ZechT
"""
#import ResonanceData

import sys,os


from PyQt5.QtWidgets import *

import ui.MainFramework as MainFramework

import configparser

def write_config(name,ver):
    config = configparser.RawConfigParser()
        
        # When adding sections or items, add them in the reverse order of
        # how you want them to be displayed in the actual file.
        # In addition, please note that using RawConfigParser's and the raw
        # mode of ConfigParser's respective set functions, you can assign
        # non-string values to keys internally, but will receive an error
        # when attempting to write to a file or when you get it in non-raw
        # mode. SafeConfigParser does not allow such assignments to take place.
    config.add_section('dirs')
    
    config.set('dirs','home_directory',os.getcwd())
    config.set('dirs','working_directory',os.path.expanduser('~'))
    config.set('dirs','saving_directory',os.path.expanduser('~'))
    if os.name=='nt':
        config.set('dirs','icon_directory',r'\ui\icons'+'\\')
    if os.name=='posix':
        config.set('dirs','icon_directory','/ui/icons/')
        
       
    config.add_section('info')
    config.set('info', 'version', ver)
    config.set('info', 'name', 'LKSPy')
    config.set('info', 'description', 'semi-automated reduction and evaluation of X-ray and neutron scattering datasets')
    config.set('info', 'authors', 'ToZe')
    config.set('info', 'copyright', 'MIT Licence')
    
    # Writing our configuration file to 'example.cfg'
    with open(name, 'w') as configfile:
        config.write(configfile)    

def main():
    
    version = '0.1'###
        #Create initial config when no config existing
    
    if not (os.path.isfile("nt_config.cfg") and os.name=='nt') or (os.path.isfile("posix_config.cfg") and os.name=='posix'):
        write_config(os.name+'_config.cfg',version)
           
        # Create an PyQT4 application object.
    a = QApplication(sys.argv)

        # The QWidget widget is the base class of all user interface objects in PyQt4.
    w = MainFramework.MainFramework()
    #w = QMainWindow()


        # Set window title
    w.setWindowTitle("PloPo V"+version)

        # Show window
    w.show()

    sys.exit(a.exec_())


if __name__ == "__main__":
    main()