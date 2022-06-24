#!/usr/bin/python
#title           :d8redXrr.py
#description     :This will generate reduced XRR data, measured at a Bruker D8
#author          :Hans-Georg Steinrück
#mod			 :Michail Goldes
#e-mail		 :hansgeorgsteinrueck@gmail.com
#date            :26. Feb. 2015
#version         :0.2
#usage           :./d8redXrr.py REFL_PARAMETERS REFL_SCANS_{xx..yy}.txt BG_SCANS_{xx..yy}.txt (+ optional arguments)
#			these optional arguments are the beam-size, sample-size, primary intensity, output-file and the option to quiet the graphical output
#			these have default values
#notes           :
#python_version  :3.4.2 
#version date	 :19.07.2018
#==============================================================================

# Zeile 70 reflPar angeben
# python d8redXrr_mod.py Pfad_fuer_daten xrr bkg -b 0.2 -s 10 -i 13e6 -o xrr 


#==============================================================
#===> Import the modules needed to run the script
#==============================================================
from pylab import *
import pylab as P
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
#plt.rcParams['font.family']='M+ 2c'

#==============================================================
#===> Argparse to use optional command line parameters
#==============================================================
import argparse

parser = argparse.ArgumentParser(description='reduce reflectivity data.')

#parser.add_argument('paramFile',    metavar='PARAMFILE',  type=str, help='reflectivity parameter file from D8')
parser.add_argument('inputFilesPath',    metavar='inputFilesPath',  type=str, help='path of the input files')
parser.add_argument('inputFiles',   metavar='INPUTFILE', type=str, nargs='+',   help='all Data files (refl and background)')
parser.add_argument('-b',           dest='beam',          type=float, default=0.2, help='beam height')
parser.add_argument('-s',           dest='size',          type=float, default=10,  help='sample size')
#parser.add_argument('-i',           dest='I0',            type=float, default=1,   help='incident inentsity')
parser.add_argument('-o',           dest='outputFile',    type=str, default="output.xrr",   help='output File')
parser.add_argument('-q', dest='quiet', action='store_false', help='quiet output')

args = parser.parse_args()
#print("args: ",args)

#==============================================================
#===> Set parameters for the plots & colors etc.
#==============================================================
plt.rc("font", size=14)

rcParams['figure.figsize'] = 8, 5

#rc('text', usetex=True)

close('all')

fig, ((ax1))=subplots(nrows=1,ncols=1)
ax1.set_xlabel("2\u03b8")
ax1.set_ylabel("Intensity")


#==============================================================
#===> Load the refl-parameter file, from which counting times
#===> and absorber values are read in to scale the data
#==============================================================
#reflPar=np.loadtxt(args.paramFile,delimiter=",")

##Path of ReflParam (\\)
reflPar=np.loadtxt('C:\\Users\\michail\\Documents\\D8_Advanced_test\\reflParameters_3.txt',delimiter=",")
#print(reflPar)
#==============================================================
#===> This contains the absorber values as an array
#==============================================================
absorbers=[1,7.5,67.84,3800]

#==============================================================
#===> Empty arrays for the angles, intensities, and errors for
#===> refl and bg scans
#==============================================================
refl_int=np.array([])
refl_ang=np.array([])
bg_int=np.array([])
bg_ang=np.array([])
bar=np.array([])

#print(len(reflPar))
def getScallingFactors():
	IntArray = np.empty((len(reflPar),2), dtype=double)
	# Temporal Array
	ScFacArray_Temp = np.ones(len(reflPar))
	# Final Array of Scaling Factors | j-th entry scaling j-th interval as defined in "reflPar"
	ScFacArray_Fin = np.ones(len(reflPar))
	## Get Data Files, Save First and Last Value
	for j in range(len(reflPar)-1):
		for i,params in enumerate(reflPar):
			#print(ScFacArray_Temp)
			a1, b1=np.loadtxt(args.inputFilesPath+'\\'+args.inputFiles[0]+"_"+str(i+1)+".txt",unpack=True)
			b1=(b1/params[3]) / ScFacArray_Fin[i]
			#print(b1)
			IntArray[i] = [b1[len(b1)-1],b1[0]]
		#print(IntArray)
		## Get Quotient (/) between last and first values of neighboring files
		for i in range(len(IntArray)-1):
			ScFacArray_Temp[i] = IntArray[i][0] / IntArray[i+1][1]
		#print(j, "Temp:		", ScFacArray_Temp)
		#print("Fin:		", ScFacArray_Fin)
		ScFacArray_Fin = np.multiply(ScFacArray_Fin , ScFacArray_Temp)
		
		#print("Fin_Mult:	", ScFacArray_Fin)
		#ScFacArray_Fin[len(ScFacArray_Fin)-2-j] = ScFacArray_Temp[len(ScFacArray_Fin)-2-j]
		#print("FinFin:", ScFacArray_Fin)
	return ScFacArray_Fin
	
def getScallingFactorsBG():
	IntArray_BG = np.empty((len(reflPar),2), dtype=double)
	# Temporal Array
	ScFacArray_Temp_BG = np.ones(len(reflPar))
	# Final Array of Scaling Factors | j-th entry scaling j-th interval as defined in "reflPar"
	ScFacArray_Fin_BG = np.ones(len(reflPar))
	## Get Data Files, Save First and Last Value
	for j in range(len(reflPar)-1):
		for i,params in enumerate(reflPar):
			#print(ScFacArray_Temp)
			c1,d1=np.loadtxt(args.inputFilesPath+'\\'+args.inputFiles[1]+"_"+str(i+1)+".txt",unpack=True)
			d1=(d1/params[3]) / ScFacArray_Fin_BG[i]
			#print(b1)
			IntArray_BG[i] = [d1[len(d1)-1],d1[0]]
		#print(IntArray)
		## Get Quotient (/) between last and first values of neighboring files
		for i in range(len(IntArray_BG)-1):
			ScFacArray_Temp_BG[i] = IntArray_BG[i][0] / IntArray_BG[i+1][1]
		#print(j, "Temp:", ScFacArray_Temp)
		#print("Fin:", ScFacArray_Fin)
		ScFacArray_Fin_BG = np.multiply(ScFacArray_Fin_BG , ScFacArray_Temp_BG)
		
		#print("Fin_Mult:", ScFacArray_Fin)
		#ScFacArray_Fin[len(ScFacArray_Fin)-2-j] = ScFacArray_Temp[len(ScFacArray_Fin)-2-j]
		#print("FinFin:", ScFacArray_Fin)
	return ScFacArray_Fin_BG
	
ScFac = getScallingFactors()
ScFacBG = getScallingFactorsBG()

for i,params in enumerate(reflPar):
	#==============================================================
	#===> Load refls from individual sub-scans
	#==============================================================
	a1,b1=np.loadtxt(args.inputFilesPath+'\\'+args.inputFiles[0]+"_"+str(i+1)+".txt",unpack=True)
	#==============================================================
	#===> Load bgs from individual sub-scans
	#==============================================================
	c1,d1=np.loadtxt(args.inputFilesPath+'\\'+args.inputFiles[1]+"_"+str(i+1)+".txt",unpack=True)

	#==============================================================
	#===> Calculate error-bars
	#==============================================================
	err=np.sqrt(b1+d1)

	#==============================================================
	#===> Scale refls, bgs & error-bars
	#==============================================================
	#print(ScFacBG.sum())
	
	b1=(b1/params[3])/ScFac[i]
	d1=(d1/params[3])/ScFacBG[i]
	err=err/params[3]
		
	#ScFac = ScFac[1:]
	#ScFacBG = ScFacBG[1:]
		
	#ScFac = np.delete(ScFac, [ScFac[i]])
	#==============================================================
	#===> Put individual sub-scans into a single arrays
	#==============================================================                
	refl_ang=np.concatenate((refl_ang,a1))
	refl_int=np.concatenate((refl_int,b1))
	bg_ang=np.concatenate((bg_ang,c1))
	bg_int=np.concatenate((bg_int,d1))
	bar=np.concatenate((bar,err))
''' Version 1
for i,params in enumerate(b):
	
	#print("i:",i)
	#print("params:",params)
	#==============================================================
	#===> Load refls from individual sub-scans
	#==============================================================
	a1,b1=np.loadtxt(args.inputFilesPath+'\\'+args.inputFiles[len(reflPar)-1-i],unpack=True)
	#print("a1",a1)
	#print("b1",b1)
	#==============================================================
	#===> Load bgs from individual sub-scans
	#==============================================================
	c1,d1=np.loadtxt(args.inputFilesPath+'\\'+args.inputFiles[2*len(reflPar)-1-i],unpack=True)
	#print("c1",c1)
	#print("d1",d1)
	#==============================================================
	#===> Calculate error-bars
	#==============================================================
	err=np.sqrt(b1+d1)

	#==============================================================
	#===> Scale refls, bgs & error-bars
	#==============================================================
	b1=b1/params[3]#*absorbers[int(params[4])]
	d1=d1/params[3]#*absorbers[int(params[4])]
	err=err/params[3]#*absorbers[int(params[4])]

	#==============================================================
	#===> Put individual sub-scans into a single arrays
	#==============================================================                
	refl_ang=np.concatenate((refl_ang,a1[::-1]))
	refl_int=np.concatenate((refl_int,b1[::-1]))
	#print(refl_ang)
	bg_ang=np.concatenate((bg_ang,c1[::-1]))
	bg_int=np.concatenate((bg_int,d1[::-1]))
	bar=np.concatenate((bar,err[::-1]))
'''

#==============================================================
#===> Substract bg from int
#==============================================================
bgCorr=(refl_int-bg_int)


#==============================================================
#===> Plot refl and bg scan VS angle
#==============================================================
title('Scaled for counting \u0026 time absorbers')
ax1.semilogy(refl_ang,refl_int ,linestyle='None', marker='o', markerfacecolor='None', markeredgecolor='k', markersize=2, markeredgewidth=1.2, label="refl")
ax1.semilogy(bg_ang,bg_int ,linestyle='None', marker='o', markerfacecolor='None', markeredgecolor='b', markersize=2, markeredgewidth=1.2,label="bg")


#==============================================================
#===> Plot refl-bg VS angle
#==============================================================
ax1.semilogy(refl_ang,bgCorr ,linestyle='None', marker='o', markerfacecolor='None', markeredgecolor='r', markersize=2, markeredgewidth=1.2,label="bg-substracted")
ax1.errorbar(refl_ang,bgCorr, yerr=bar, linestyle='None', color='r', elinewidth=1.5)

lg = ax1.legend(loc=7, numpoints = 1)
lg.draw_frame(False)

tight_layout(w_pad=0.2)

if args.quiet: show()



#==============================================================
#===> Convert to q
#==============================================================
q=4*3.1415/0.709*np.sin(refl_ang/2*3.1415/180)


#==============================================================
#===> Plot bgCorr vs q
#==============================================================
close('all')
fig, ((ax1))=subplots(nrows=1,ncols=1)
title('Bg-corrected vs q')

ax1.set_xlabel("q$_\mathregular{z}$")
ax1.set_ylabel("Intensity")

ax1.semilogy(q,bgCorr ,linestyle='None', marker='o', markerfacecolor='None', markeredgecolor='r', markersize=2, markeredgewidth=1.2)
ax1.errorbar(q,bgCorr, yerr=bar, linestyle='None', color='r', elinewidth=1.5)

tight_layout(w_pad=0.2)

if args.quiet: show()

'''
#==============================================================
#===> Normalize to I0
#==============================================================
I0=args.I0

i0_corr=bgCorr#/bgCorr[0]#I0

i0_bar=bar/I0


#==============================================================
#===> Plot IO corrected vs q
#==============================================================
close('all')
fig, ((ax1))=subplots(nrows=1,ncols=1)
title('I0-corrected vs q')

ax1.set_xlabel("q$_\mathregular{z}$")
ax1.set_ylabel("Intensity")

ax1.semilogy(q,i0_corr ,linestyle='None', marker='o', markerfacecolor='None', markeredgecolor='r', markersize=2, markeredgewidth=1.2)
ax1.errorbar(q,i0_corr, yerr=i0_bar, linestyle='None', color='r', elinewidth=1.5)

tight_layout(w_pad=0.2)

if args.quiet: show()

'''
#==============================================================
#===> Correct footprint
#==============================================================
size=args.size
beam=args.beam

fp_corr=bgCorr
fp_bar=bar

x=beam*4*3.1415/0.709/q
fp_corr[x>=size]=(fp_corr*(x/size))[x>=size]
fp_bar[x>=size]=(fp_bar*(x/size))[x>=size]
# Normalize Footprint-correct
fp_bar = fp_bar / max(fp_corr)
fp_corr = fp_corr / max(fp_corr)#[0]

#print(fp_corr)
#==============================================================
#===> Plot footprint corrected vs q
#==============================================================
close('all')
fig, ((ax1))=subplots(nrows=1,ncols=1)
title('(Footprint+I_0)-corrected vs q: final results')

ax1.set_xlabel("q")
ax1.set_ylabel("I")

ax1.semilogy(q,fp_corr ,linestyle='None', marker='o', markerfacecolor='None', markeredgecolor='r', markersize=2, markeredgewidth=1.2)
ax1.errorbar(q,fp_corr, yerr=fp_bar, linestyle='None', color='r', elinewidth=1.5)

tight_layout(w_pad=0.2)

if args.quiet: show()

#==============================================================
#===> Save it!
#==============================================================
output = np.column_stack((q,fp_corr,fp_bar))
np.savetxt(args.inputFilesPath+'\\'+args.outputFile,output)











