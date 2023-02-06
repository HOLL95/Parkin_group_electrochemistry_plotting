import matplotlib.pyplot as plt
import numpy as np
from harmonics_plotter import harmonics
from multiplotter import multiplot
import warnings
class Electrochem_plots:
    def __init__(self, data, order, desired_plots, **kwargs):
        num_plots=len(desired_plots)
        if len(order)!=len(data):
            order=[order]*len(data)
        if "one_tail" not in kwargs:
            kwargs["one_tail"]=True
        else:
            self.valid_checker(kwargs["one_tail"], "bool", "one_tail")
        if "harmonic_number" not in kwargs:
            kwargs["harmonic_number"]=True
        else:
            self.valid_checker(kwargs["harmonic_number"], "bool", "harmonic_number")
        if "FourierFunc" not in kwargs:
            kwargs["FourierFunc"]="Abs"
        else:
            self.valid_checker(kwargs["FourierFunc"], "Option list", "FourierFunc", ["Abs", "Real", "Imag"])
        if "FourierScale" not in kwargs:
            kwargs["FourierScale"]="log"
        else:
            self.valid_checker(kwargs["FourierScale"], "Option list", "FourierScale", ["log", "none"])
        if "Fourier_harmonic_crop" not in kwargs:
            kwargs["Fourier_harmonic_crop"]=False
        else:
            self.valid_checker(kwargs["Fourier_harmonic_crop"], "bool", "Fourier_harmonic_crop")
        if "harmonics_box" not in kwargs:
            kwargs["harmonics_box"]=0.1
        else:
            self.valid_checker(kwargs["harmonics_box"], "Numerical list","harmonics_box", [0.01, 0.5])
        if "harmonic_hanning" not in kwargs:
            kwargs["harmonic_hanning"]=False
        else:
            self.valid_checker(kwargs["harmonic_hanning"], "bool","harmonic_hanning")
        if "harmonic_funcs" not in kwargs:
            kwargs["harmonic_funcs"]="Real"
        else:
            self.valid_checker(kwargs["harmonic_funcs"], "Option list", "harmonic_funcs", ["Abs", "Real", "Imag"])
        if "Fourier_frequency_lines" not in kwargs:
            kwargs["Fourier_frequency_lines"]=False
        else:
            self.valid_checker(kwargs["Fourier_frequency_lines"], "bool","Fourier_frequency_lines")
        if "current_scaling" not in kwargs:
            kwargs["current_scaling"]=1
        if "potential_scaling" not in kwargs:
            kwargs["potential_scaling"]=1
       
        fourier_funcs={"Abs":np.abs, "Real":np.real, "Imag":np.imag}
        if "time-harmonics" in desired_plots or "potential-harmonics" in desired_plots:
            harm_loc=[x for x in range(0, num_plots) if desired_plots[x]=="time-harmonics" or desired_plots[x]=="potential-harmonics"]
            plotting_harmonics=True
            if "desired_harmonics" not in kwargs:
                kwargs["desired_harmonics"]=list(range(1, 7))
            num_harms=len(kwargs["desired_harmonics"])
            if num_plots==1:
                fig, ax=plt.subplots(num_harms, 1)
                plot_version="axes_list"
            else:
                figure=multiplot(1, num_plots, harmonic_position=harm_loc, plot_width=4, orientation="portrait", num_harmonics=num_harms)
                plot_version="axes_dict"
        else:
            plotting_harmonics=False
            kwargs["desired_harmonics"]=[10]
            fig, ax=plt.subplots(1, num_plots)
            if num_plots==1:
                ax=[ax]
        scale_list={1:"", 1000:"m", 1e6:"$$\\mu", 1e9:"n", 1e12:"p"}
        plot_units={"current":"A", "potential":"V"}
        plot_labels={"time":"Time(s)"}
        for scaling in ["current", "potential"]:
            scale_factor=kwargs[scaling+"_scaling"]
            if not isinstance(scale_factor, (int, float)):
                raise TypeError(scaling+"_scaling needs to be a number")
            if np.log10(scale_factor)%1!=0:
                raise ValueError(scaling +" needs to be integer powers of ten only")
            plot_labels[scaling]=scaling.title()+" ("+scale_list[scale_factor]+plot_units[scaling]+")"
        for j in range(0, len(data)):
            
            plot_dict={key:data[j][:,order[j].index(key)] for key in ["current", "potential", "time"]}
            for scaling in ["current", "potential"]:
                plot_dict[scaling]=np.multiply(plot_dict[scaling], kwargs[scaling+"_scaling"])
            master_harmonics=kwargs["desired_harmonics"]
            fft=np.fft.fft(plot_dict["current"])
            fft_freq=np.fft.fftfreq(len(plot_dict["current"]), plot_dict["time"][1]-plot_dict["time"][0])
            max_freq=abs(max(fft_freq[np.where(fft==max(fft))]))
            highest_harm=kwargs["desired_harmonics"][-1]
            upper_bound=max_freq*(highest_harm+0.25)
            highest_freq=abs(fft_freq[len(fft_freq)//2])
            if upper_bound>highest_freq:

                highest_harm= int(highest_freq//max_freq)
                master_harmonics=list(range(1,highest_harm))
                upper_bound=max_freq*(highest_harm+0.25)
                warnings.warn("Highest accessible frequency lower than harmonic number")
            for i in range(0, len(desired_plots)):

                if plotting_harmonics==True:
                    if plot_version=="axes_list":
                        axis=ax
                    elif plot_version=="axes_dict":
                        axis=figure.axes_dict["col{0}".format(i+1)]
                else:
                    axis=[ax[i]]


                Fourier_plot=False
                if "-" not in desired_plots[i]:
                    if desired_plots[i].lower()!="fourier":
                        raise ValueError("Need to provide a dash (i.e. X-Y) in the plot definition" )
                    else:
                        Fourier_plot=True
                if Fourier_plot==False:
                    dash_idx=desired_plots[i].index("-")
                    x_axis=desired_plots[i][:dash_idx]
                    y_axis=desired_plots[i][dash_idx+1:]
               
                if "Fourier" in desired_plots[i]:
                    func=fourier_funcs[kwargs["FourierFunc"]]
                    if kwargs["one_tail"]==True:
                        if kwargs["Fourier_harmonic_crop"]==True:
                            idx=np.where((fft_freq>0)&(fft_freq<upper_bound))
                            plot_freq=fft_freq[idx]
                            plot_Y=func(fft[idx])
                        else:
                            plot_freq=fft_freq[:len(fft_freq)//2]
                            plot_Y=func(fft[:len(fft_freq)//2])
                    else:
                        if kwargs["Fourier_harmonic_crop"]==True:
                            idx=np.where((fft_freq>-upper_bound)&(fft_freq<upper_bound))
                            plot_freq=fft_freq[idx]
                            plot_Y=func(fft[idx])
                        else:
                            plot_freq=fft_freq
                            plot_Y=func(fft)
                    if kwargs["Fourier_frequency_lines"]==True:
                        for i in range(1, highest_harm+1):
                            axis[0].axvline(i*max_freq, color="black", linestyle="--")
                    if kwargs["FourierScale"]=="log":
                        axis[0].semilogy(plot_freq, np.abs(plot_Y))
                    else:
                        axis[0].plot(plot_freq, plot_Y)
                    axis[0].set_xlabel("Frequency (Hz)")
                    axis[0].set_ylabel("Magnitude")
                elif "harmonics" not in desired_plots[i]:
                    x_data=plot_dict[x_axis]
                    y_data=plot_dict[y_axis]
                    axis[0].plot(x_data, y_data)
                    axis[0].set_xlabel(plot_labels[x_axis])
                    axis[0].set_ylabel(plot_labels[y_axis])
                elif "harmonics" in desired_plots[i]:
                    hfunc=fourier_funcs[kwargs["harmonic_funcs"]]
                    x_data=plot_dict[x_axis]
                    h_class=harmonics(kwargs["desired_harmonics"], max_freq, kwargs["harmonics_box"])
                    plot_harms=h_class.generate_harmonics(plot_dict["time"], plot_dict["current"], hanning=kwargs["harmonic_hanning"], plot_func=fourier_funcs[kwargs["harmonic_funcs"]])
                    for h in range(0, num_harms):
                        axis[h].plot(x_data, hfunc(plot_harms[h, :]))
                        if h==num_harms-1:
                             axis[h].set_xlabel(plot_labels[x_axis])
                        else:
                            axis[h].set_xticks([])
                        if h ==num_harms//2:
                            axis[h].set_ylabel(plot_labels["current"])
                        if kwargs["harmonic_number"]==True:
                            if j==0:
                                twinx=axis[h].twinx()
                                twinx.set_ylabel(master_harmonics[h], rotation=0)
                                twinx.set_yticks([])
    def valid_checker(self, argument, arg_type, key, range=None):
        if arg_type=="bool":
            if not isinstance(argument, bool):
                raise TypeError(key +"needs to be True/False")
        if arg_type=="Numerical list":
            if argument<range[0] or argument>range[1]:
                raise ValueError(key + "needs to be in the range [{0}, {1}]".format(*range))
        if arg_type=="Option list":
            if argument not in range:
                raise ValueError(key + "needs to be one of {0}".format((" ").join(range)))
                
                