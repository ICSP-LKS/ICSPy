# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 21:17:59 2018

@author: ZechT
"""



def plotSAS(axis,data,label,color,title,ls='',marker='x',fontsize=14):
    
    import numpy as np
    import matplotlib.pyplot as plt
                    
    #axis.set_title(title,fontweight='bold',fontsize=16)
    axis.set_xscale("log")
    axis.set_yscale("log")
    
    if data[0,2]==-1.0:
        axis.plot(data[:,0],data[:,1],'-r',label='')
        
    else:
        axis.errorbar(data[:,0],data[:,1],yerr=data[:,2],
                 marker=marker,linestyle=ls,color=color,label=label)
    
    axis.legend(loc='upper right',labelspacing=0.1,prop={'size':fontsize-2,'weight':'bold'})
    
    axis.set_xlabel(r'Q [$\mathbf{nm^{-1}}$]',fontweight='bold',fontsize=fontsize)
    axis.set_ylabel(r'$\mathbf{\partial\Sigma/\partial\Omega}$ $\mathbf{[cm^{-1}]}$',fontweight='bold',fontsize=fontsize)
    for tick in axis.xaxis.get_major_ticks():
            tick.label.set_fontsize(fontsize-int(fontsize/7)) 
            tick.label.set_fontweight('bold')

    for tick in axis.yaxis.get_major_ticks():
            tick.label.set_fontsize(fontsize-int(fontsize/7))
            tick.label.set_fontweight('bold')
    
    axis.xaxis.set_tick_params(width=int(fontsize/7),length=int(fontsize/2))
    axis.yaxis.set_tick_params(width=int(fontsize/7),length=int(fontsize/2))
    axis.xaxis.set_tick_params('minor',width=int(fontsize/7),length=int(fontsize/2)-3)
    axis.yaxis.set_tick_params('minor',width=int(fontsize/7),length=int(fontsize/2)-3)
        
    plt.tight_layout()

def plotSAS(axis,data,label,color,title=None,ls='',marker='x',lw=1,zorder=1):

    if title is not None:
        axis.set_title(title,fontweight='bold',fontsize=16)
    axis.set_xscale("log")
    axis.set_yscale("log")
    pppl = 0
    if np.shape(data)[1]<=2:
       pppl,= axis.plot(data[:,0],data[:,1],color=color,label=label,zorder=zorder,lw=lw)
        
    else:
        pppl,=axis.errorbar(data[:,0],data[:,1],yerr=data[:,2],color=color,lw=lw,
                 marker=marker,linestyle=ls,label=label,fillstyle='none',zorder=zorder)
    
    #axis.legend(loc='upper right',labelspacing=0.1,prop={'size':12,'weight':'bold'})
    
    axis.set_xlabel(r'Q ($\rm\mathbf{ nm^{-1}}$)',fontsize=22,fontweight='bold')
    axis.set_ylabel(r'$\rm\mathbf{ \partial\Sigma/\partial\Omega}$ ($\rm\mathbf{cm^{-1}}$)',fontsize=22,fontweight='bold')
    [i.set_linewidth(2) for i in axis.spines.values()]
    for tick in axis.xaxis.get_major_ticks():
            tick.label.set_fontsize(18) 
            tick.label.set_fontweight('bold')

    for tick in axis.yaxis.get_major_ticks():
            tick.label.set_fontsize(18)
            tick.label.set_fontweight('bold')
    
    axis.xaxis.set_tick_params(width=int(fontsize/7),length=int(fontsize/2))
    axis.yaxis.set_tick_params(width=int(fontsize/7),length=int(fontsize/2))
    axis.xaxis.set_tick_params('minor',width=int(fontsize/7),length=int(fontsize/2)-3)
    axis.yaxis.set_tick_params('minor',width=int(fontsize/7),length=int(fontsize/2)-3)
    
    return(pppl) 