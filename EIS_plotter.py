import numpy as np
import matplotlib.pyplot as plt
import copy
import time
import collections
import math
import random
import warnings
from collections import deque
from uuid import uuid4

#TODO->paralell in series+ gerischer
class EIS_plots:
    def __init__(self,  data,**kwargs,):
        if "negative_flag" not in kwargs:
            kwargs["negative_flags"]=True
        if "desired_plots" not in kwargs:
            kwargs["desired_plots"]=["nyquist", "bode"]
        elif isinstance(kwargs["desired_plots"], list) is not True:
            kwargs["desired_plots"]=[kwargs["desired_plots"]]
        if "orthonormal" not in kwargs:
            kwargs["orthonormal"]=False
        if "scatter" not in kwargs:
            kwargs["scatter"]=1
        elif kwargs["scatter"]==True:
            kwargs["scatter"]=1
        elif kwargs["scatter"]==False:
            kwargs["scatter"]=0
        if "order" not in kwargs or isinstance(kwargs["order"], dict) is not True:
            return ValueError("Need to define the order of real, imaginary and frequencies in this format {\"Real\":x,\"Imaginary\":y,\"Frequency\":z }")
        if "labels" not in kwargs:
            kwargs["labels"]=[None for x in range(0, len(data))]
        fig, ax=plt.subplots(1, len(kwargs["desired_plots"]))
        if len(kwargs["desired_plots"])==1:
            label_loc=kwargs["desired_plots"][0]
            ax=[ax]
        else:
            label_loc="nyquist"
        for i in range(0, len(kwargs["desired_plots"])):
            
            axis=ax[i]
            if kwargs["desired_plots"][i]=="bode":
                twinxis=ax[i].twinx()
            for j in range(0, len(data)):
                
                plot_dict={key:data[j][:,kwargs["order"][key]] for key in ["Real", "Imaginary", "Frequency"]}
                if kwargs["negative_flags"]==True:
                    plot_dict["Imaginary"]=np.multiply(plot_dict["Imaginary"], -1)
                spectra=np.column_stack((plot_dict["Real"], plot_dict["Imaginary"]))
                freqs=plot_dict["Frequency"]
                if kwargs["desired_plots"][i]=="bode":
                    if label_loc=="bode":
                        label=kwargs["labels"][i]
                    else:
                        label=None
                    self.bode(spectra, freqs, scatter=kwargs["scatter"], ax=axis, twinx=twinxis, label=label, compact_labels=True)
                elif kwargs["desired_plots"][i]=="nyquist":
                    if label_loc=="nyquist":
                        label=kwargs["labels"][j]
                    else:
                        label=None
                    self.nyquist(spectra, ax=axis, scatter=kwargs["scatter"], orthonormal=kwargs["orthonormal"], label=label)
                else:
                    raise ValueError("Needs to be bode or nyqusit, not {0}".format(kwargs["desired_plots"][i]))

    def convert_to_bode(self,spectra):
        spectra=[complex(x, y) for x,y in zip(spectra[:,0], spectra[:,1])]
        phase=np.angle(spectra, deg=True)#np.arctan(np.divide(-spectra[:,1], spectra[:,0]))*(180/math.pi)
        #print(np.divide(spectra[:,1], spectra[:,0]))
        magnitude=np.log10(np.abs(spectra))
        return np.column_stack((phase,magnitude))
    def nyquist(self, spectra, **kwargs):
        if "ax" not in kwargs:
            _,kwargs["ax"]=plt.subplots(1,1)
        if "scatter" not in kwargs:
            kwargs["scatter"]=0
        if "label" not in kwargs:
            kwargs["label"]=None
        if "linestyle" not in kwargs:
            kwargs["linestyle"]="-"
        if "marker" not in kwargs:
            kwargs["marker"]="o"
        if "colour" not in kwargs:
            kwargs["colour"]=None
        if "orthonormal" not in kwargs:
            kwargs["orthonormal"]=True

        ax=kwargs["ax"]
        imag_spectra_mean=np.mean(spectra[:,1])
        if imag_spectra_mean<0:

            ax.plot(spectra[:,0], -spectra[:,1], label=kwargs["label"], linestyle=kwargs["linestyle"], color=kwargs["colour"])
        else:
            ax.plot(spectra[:,0], spectra[:,1], label=kwargs["label"], linestyle=kwargs["linestyle"], color=kwargs["colour"])
        ax.set_xlabel("$Z_{Re}$ ($\\Omega$)")
        ax.set_ylabel("$-Z_{Im}$ ($\\Omega$)")
        total_max=max(np.max(spectra[:,0]), np.max(-spectra[:,1]))
        if kwargs["orthonormal"]==True:
            ax.set_xlim([0, total_max+0.1*total_max])
            ax.set_ylim([0, total_max+0.1*total_max])
        if kwargs["scatter"]!=0:
            if imag_spectra_mean<0:
                ax.scatter(spectra[:,0][0::kwargs["scatter"]], -spectra[:,1][0::kwargs["scatter"]], marker=kwargs["marker"], color=kwargs["colour"])
            else:
                ax.scatter(spectra[:,0][0::kwargs["scatter"]], spectra[:,1][0::kwargs["scatter"]], marker=kwargs["marker"], color=kwargs["colour"])
        if kwargs["label"] is not None:
            ax.legend()
    def bode(self, spectra,frequency, **kwargs):
        if "ax" not in kwargs:
            _,kwargs["ax"]=plt.subplots(1,1)
        if "label" not in kwargs:
            kwargs["label"]=None
        if "type" not in kwargs:
            kwargs["type"]="both"
        if "twinx" not in kwargs:
            kwargs["twinx"]=kwargs["ax"].twinx()
        if "data_type" not in kwargs:
            kwargs["data_type"]="complex"
        if "compact_labels" not in kwargs:
            kwargs["compact_labels"]=False
        if "lw" not in kwargs:
            kwargs["lw"]=1.5
        if "alpha" not in kwargs:
            kwargs["alpha"]=1
        if "scatter" not in kwargs:
            kwargs["scatter"]=False
        if kwargs["data_type"]=="complex":
            spectra=[complex(x, y) for x,y in zip(spectra[:,0], spectra[:,1])]
            phase=np.angle(spectra, deg=True)#np.arctan(np.divide(-spectra[:,1], spectra[:,0]))*(180/math.pi)
            #print(np.divide(spectra[:,1], spectra[:,0]))
            magnitude=np.log10(np.abs(spectra))#np.add(np.square(spectra[:,0]), np.square(spectra[:,1]))
        elif kwargs["data_type"]=="phase_mag":
            phase=spectra[:,0]
            magnitude=spectra[:,1]
            if "data_is_log" not in kwargs:
                kwargs["data_is_log"]=True
            if kwargs["data_is_log"]==False:
                magnitude=np.log10(magnitude)
            
            
        ax=kwargs["ax"]
        ax.set_xlabel("$\\log_{10}$(Frequency)")
        x_freqs=np.log10(frequency)
        if kwargs["type"]=="both":
            twinx=kwargs["twinx"]
            ax.plot(x_freqs, phase, label=kwargs["label"], lw=kwargs["lw"], alpha=kwargs["alpha"])
            
            if kwargs["compact_labels"]==False:
                ax.set_ylabel("-Phase")
                twinx.set_ylabel("Magnitude")
            else:
                ax.text(x=-0.05, y=1.05, s="$-\\psi$", fontsize=12, transform=ax.transAxes)
                ax.text(x=0.96, y=1.05, s="$\\log_{10}(|Z|) $", fontsize=12, transform=ax.transAxes)
            twinx.plot(x_freqs, magnitude, linestyle="--", lw=kwargs["lw"], alpha=kwargs["alpha"])
            if kwargs["scatter"] is not False:
                ax.scatter(x_freqs, phase)
                twinx.scatter(x_freqs, magnitude, marker="v")
            
        elif kwargs["type"]=="phase":
            if kwargs["compact_labels"]==False:
                ax.set_ylabel("Phase")
            else:
                 ax.text(x=-0.05, y=1.05, s="$\\psi$", fontsize=12, transform=ax.transAxes)
            ax.plot(x_freqs, -phase, label=kwargs["label"], lw=kwargs["lw"], alpha=kwargs["alpha"])

        elif kwargs["type"]=="magnitude":
            
            ax.plot(x_freqs, magnitude, label=kwargs["label"], lw=kwargs["lw"], alpha=kwargs["alpha"])
            if kwargs["compact_labels"]==False:
                ax.set_ylabel("Magnitude")
            else:
                 ax.text(x=-0.05, y=1.05, s="$|Z|$", fontsize=12, transform=ax.transAxes)
        if kwargs["label"]!=None:
            kwargs["ax"].legend()




