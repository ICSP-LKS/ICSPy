# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 21:17:59 2018

@author: ZechT
"""

def plotSAS(axis,data,color,label='',title=None,ls='',marker='x',lw=1,ms=3,mew=3,zorder=1,fontsize=14,ylog=True,xlog=True):
    import numpy as np
    
    if title is not None:
        axis.set_title(title,fontsize=fontsize+4)
    if xlog:
        axis.set_xscale("log")
    if ylog:
        axis.set_yscale("log")
    pppl = 0
    if np.shape(data)[1]<=2:
       pppl,= axis.plot(data[:,0],data[:,1],color=color,label=label,zorder=zorder,lw=lw,markersize=ms,mew=mew)
        
    else:
        pppl=axis.errorbar(data[:,0],data[:,1],yerr=data[:,2],color=color,lw=lw,
                 marker=marker,linestyle=ls,label=label,fillstyle='none',zorder=zorder,markersize=ms,mew=mew)
    
    #axis.legend(loc='upper right',labelspacing=0.1,prop={'size':12,'weight':'bold'})
    
    axis.set_xlabel(r'Q ($\rm\mathrm{ \AA^{-1}}$)',fontsize=fontsize+4)
    axis.set_ylabel(r'$\rm\mathrm{ \partial\Sigma/\partial\Omega}$ ($\rm\mathrm{cm^{-1}}$)',fontsize=fontsize+4)
    [i.set_linewidth(2) for i in axis.spines.values()]
    for tick in axis.xaxis.get_major_ticks():
            tick.label.set_fontsize(fontsize) 
            #tick.label.set_fontweight('bold')

    for tick in axis.yaxis.get_major_ticks():
            tick.label.set_fontsize(fontsize)
            #tick.label.set_fontweight('bold')
    
    axis.xaxis.set_tick_params(width=int(fontsize/7),length=int(fontsize/2))
    axis.yaxis.set_tick_params(width=int(fontsize/7),length=int(fontsize/2))
    axis.xaxis.set_tick_params('minor',width=int(fontsize/7),length=int(fontsize/2)-3)
    axis.yaxis.set_tick_params('minor',width=int(fontsize/7),length=int(fontsize/2)-3)
    
    return(pppl) 