import matplotlib.pyplot as plt
import numpy as np
from harmonics_plotter import harmonics
from multiplotter import multiplot
from scipy.signal import decimate
import warnings
import pandas as pd
class Electrochem_plots:
    def __init__(self, data, order, desired_plots, **kwargs):
        num_plots=len(desired_plots)
        
        if len(order)!=len(data):
            order=[order]*len(data)
        elif len(data)==3 and isinstance(order[0], list) is False: 
            order=[order]*3
        if "colour" not in kwargs:
            kwargs["colour"]=[None]*len(data)
        elif kwargs["colour"] is None:
            kwargs["colour"]=[None]*len(data)
        elif len(data)==1:
            if kwargs["colour"] is not list:
                kwargs["colour"]=[kwargs["colour"]]
        elif not isinstance(kwargs["colour"], list) or len(kwargs["colour"]) != len(data):
            raise ValueError("For multiple plots, you need to provide a colour for each plot in the format  [\"colour1\", \"colour2\"]")
        if "init_frequency_guess" not in kwargs:
            kwargs["init_frequency_guess"]=None
        if "one_tail" not in kwargs:
            kwargs["one_tail"]=True
        else:
            self.valid_checker(kwargs["one_tail"], "bool", "one_tail")
        if "labels" not in kwargs:
            kwargs["labels"]=[None for i in range(0, len(data))]
        else:
            if len(kwargs["labels"])!= len(data):
                raise ValueError("Label list ({0}) needs to be as long as the number of data files ({1})".format(len(kwargs["labels"]), len(data)))
        if "legend_loc" not in kwargs:
            kwargs["legend_loc"]=None
        if kwargs["legend_loc"]>num_plots-1:
            raise ValueError("Legend loc needs to be lower than the number of plots")
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
        if "decimation" not in kwargs:
            kwargs["decimation"]=False
        else:
            self.valid_checker(kwargs["decimation"], "int","decimation")
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
        if "DC_only" not in kwargs:
            kwargs["DC_only"]=False
        if "print_FTV_info" not in kwargs:
            kwargs["print_FTV_info"]=False
        if "save_as_csv" not in kwargs:
            kwargs["save_as_csv"]=False
        elif isinstance(kwargs["save_as_csv"], bool) is False:
            raise ValueError("save_as_csv needs to be True or False, not {0}".format(type(kwargs["save_as_csv"])))
        #elif ".csv" not in kwargs["save_as_csv"]:
        #    raise ValueError("Need to provide a csv filename (i.e ending in .csv, not {0})".format(kwargs["save_as_csv"]))
       
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
        scale_list={1:"", 1000:"m", 1e6:"micro ", 1e9:"n", 1e12:"p"}
        plot_units={"current":"A", "potential":"V"}
        plot_labels={"time":"Time(s)"}
        for scaling in ["current", "potential"]:
            scale_factor=kwargs[scaling+"_scaling"]
            if not isinstance(scale_factor, (int, float)):
                raise TypeError(scaling+"_scaling needs to be a number")
            if np.log10(scale_factor)%1!=0:
                raise ValueError(scaling +" needs to be integer powers of ten only")
            plot_labels[scaling]=scaling.title()+" ("+scale_list[scale_factor]+plot_units[scaling]+")"
        if kwargs["save_as_csv"] is not False:
            unit_dict=dict(zip(["current", "potential", "time"],["A", "V", "s"]))
        for j in range(0, len(data)):
            #if isinstance(order[0], str):
            #    order=[order]
            if kwargs["decimation"]==False:
                plot_dict={key:data[j][:,order[j].index(key)] for key in ["current", "potential", "time"]}
            else:
                plot_dict={key:decimate(data[j][:,order[j].index(key)], kwargs["decimation"]) for key in ["current", "potential", "time"]}
            if kwargs["save_as_csv"] is not False:
                save_dict={"{0} ({1})".format(key, unit_dict[key]):plot_dict[key] for key in ["time", "potential","current",]}
                current_save_df=pd.DataFrame(data=save_dict)
            for scaling in ["current", "potential"]:
                plot_dict[scaling]=np.multiply(plot_dict[scaling], kwargs[scaling+"_scaling"])
           

            master_harmonics=kwargs["desired_harmonics"]
            fft=np.fft.fft(plot_dict["current"])
            abs_fft=np.abs(fft)
            fft_freq=np.fft.fftfreq(len(plot_dict["current"]), plot_dict["time"][1]-plot_dict["time"][0])
            if kwargs["init_frequency_guess"] is None:
                look_region=np.where(fft_freq>1)
            else:
                look_region=np.where((fft_freq>0.5*kwargs["init_frequency_guess"]) & (fft_freq<1.5*kwargs["init_frequency_guess"]))
            inspect_fft=abs_fft[look_region]
            max_freq=abs(max(fft_freq[np.where(abs_fft==max(inspect_fft))]))
            highest_harm=kwargs["desired_harmonics"][-1]
            upper_bound=max_freq*(highest_harm+0.25)
            highest_freq=abs(fft_freq[len(fft_freq)//2])
            pot=plot_dict["potential"]

            fft_pot=np.fft.fft(pot)
            zero_harm_idx=np.where((fft_freq>-(0.1*max_freq)) & (fft_freq<(0.1*max_freq)))
            dc_pot=np.zeros(len(fft_pot), dtype="complex")
            dc_pot[zero_harm_idx]=fft_pot[zero_harm_idx]
            time_domain_dc_pot=np.real(np.fft.ifft(dc_pot))
            if kwargs["save_as_csv"] is not False:
                current_save_df["DC_potential ({0}V)".format(scale_list[kwargs["potential_scaling"]])]=time_domain_dc_pot
            if kwargs["DC_only"]==True:
                plot_dict["potential"]=time_domain_dc_pot
            if kwargs["print_FTV_info"]==True:
                E_points=np.divide([min(time_domain_dc_pot), max(time_domain_dc_pot)], kwargs["potential_scaling"])
            
                scan_rate=((E_points[1]-E_points[0])*2)/plot_dict["time"][-1]
                print("Input frequency best guess is {0} Hz".format(max_freq))
                if kwargs["DC_only"]==False:
                    print("For more info set DC_only to True")
                else:
                    print("Estimated scan rate={0} V/s".format(scan_rate))
                    print("Best guess E_start={0} V, E_reverse={1} V".format(E_points[0], E_points[1]))
            if upper_bound>highest_freq:

                highest_harm= int(highest_freq//max_freq)
                master_harmonics=list(range(1,highest_harm))
                upper_bound=max_freq*(highest_harm+0.25)
                warnings.warn("Highest accessible frequency lower than harmonic number")
            for i in range(0, len(desired_plots)):

                if plotting_harmonics==True:
                    if plot_version=="axes_list":
                        axis=ax
                        legend_axis=ax[0]
                    elif plot_version=="axes_dict":
                        axis=figure.axes_dict["col{0}".format(i+1)]
                        if kwargs["legend_loc"]!=None:
                            legend_axis=figure.axes_dict["col{0}".format(kwargs["legend_loc"]+1)][0]
                else:
                    axis=[ax[i]]
                    if kwargs["legend_loc"]!=None:
                        print(ax, kwargs["legend_loc"])
                        legend_axis=ax[kwargs["legend_loc"]]


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
                        axis[0].semilogy(plot_freq, np.abs(plot_Y), label=kwargs["labels"][j], color=kwargs["colour"][j])
                    else:
                        axis[0].plot(plot_freq, np.real(plot_Y), label=kwargs["labels"][j], color=kwargs["colour"][j])
                    if kwargs["save_as_csv"] is not False:
                        fouriersave_dict={"Frequency (Hz)":plot_freq}
                        if kwargs["FourierScale"]=="log":
                            label="log({0}(FFT))".format(kwargs["FourierFunc"])
                            fouriersave_dict[label]=np.log10(np.abs(plot_Y))
                        else:
                            label="{0}(FFT)".format(kwargs["FourierFunc"])
                            fouriersave_dict[label]=np.real(plot_Y)
                        if kwargs["labels"][j] is None:
                            savename_Fourier=str(j)+"_Fourier"
                        else:
                            savename_Fourier=kwargs["labels"][j]+"_Fourier"
                        Fourier_savedf=pd.DataFrame(data=fouriersave_dict)
                        template="{}"
                        with open("{0}.csv".format(savename_Fourier), 'w') as fp:
                            fp.write(template.format(Fourier_savedf.to_csv(index=False, lineterminator='\n')))
        
                    axis[0].set_xlabel("Frequency (Hz)")
                    axis[0].set_ylabel("{0} Magnitude".format(kwargs["FourierFunc"]))
                    #if kwargs["save_as_csv"] is not False:
                    #    current_save_df["Frequency (Hz)"]=plot_freq
                    #    current_save_df[kwargs["FourierFunc"] + " Magnitudes"]=plot_Y
                elif "harmonics" not in desired_plots[i]:
                    x_data=plot_dict[x_axis]
                    y_data=plot_dict[y_axis]
                   
                    axis[0].plot(x_data, y_data, label=kwargs["labels"][j], color=kwargs["colour"][j])
                    axis[0].set_xlabel(plot_labels[x_axis])
                    axis[0].set_ylabel(plot_labels[y_axis])



                elif "harmonics" in desired_plots[i]:
                    hfunc=fourier_funcs[kwargs["harmonic_funcs"]]
                    x_data=plot_dict[x_axis]
                    h_class=harmonics(kwargs["desired_harmonics"], max_freq, kwargs["harmonics_box"])
                    plot_harms=h_class.generate_harmonics(plot_dict["time"], plot_dict["current"], hanning=kwargs["harmonic_hanning"], plot_func=fourier_funcs[kwargs["harmonic_funcs"]])
                    for h in range(0, num_harms):
                        print(h, master_harmonics)
                        if h>=len(master_harmonics):
                            continue
                        else:
                            axis[h].plot(x_data, hfunc(plot_harms[h, :]), label=kwargs["labels"][j], color=kwargs["colour"][j])
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
                            if kwargs["save_as_csv"] is not False:
                                current_save_df["{2} Harmonic {0} ({1})".format(master_harmonics[h], (scale_list[kwargs["current_scaling"]]+"A"), kwargs["harmonic_funcs"])]=hfunc(plot_harms[h, :])
            if kwargs["save_as_csv"] is not False:
                kwarg_keys=list(kwargs.keys())
                new_list=["" for i in range(0, len(kwarg_keys))]
                excluded_args=["desired_harmonics", "colour", "legend_loc", "print_FTV_info", "Fourier", "harmonic_number", "labels", "DC_only", "save_as_csv", "one_tail"]
                for i in range(0, len(kwarg_keys)):
                    true_list=[x in kwarg_keys[i] for x in excluded_args]
                    if True in true_list:
                        continue
                    if i%4==0:
                        end="\r\n"
                    else:
                        end=""
                    new_list[i]="{0}:{1}{2}".format(kwarg_keys[i], kwargs[kwarg_keys[i]], end)
                full_list=(" ").join(new_list)+"\r\n"
                template = full_list+"{}"
                if kwargs["labels"][j] is None:
                    savename=str(j)
                else:
                    savename=kwargs["labels"][j]                    
                with open("{0}.csv".format(savename), 'w') as fp:
                    fp.write(template.format(current_save_df.to_csv(index=False, lineterminator='\n')))
                
            if kwargs["legend_loc"]!=None:
                legend_axis.legend()
    def valid_checker(self, argument, arg_type, key, range=None):
        if arg_type=="bool":
            if not isinstance(argument, bool):
                raise TypeError(key +"needs to be True/False")
        if arg_type=="int":
            if not isinstance(argument, int):
                raise TypeError(key +"needs to be int")
        if arg_type=="Numerical list":
            if argument<range[0] or argument>range[1]:
                raise ValueError(key + "needs to be in the range [{0}, {1}]".format(*range))
        if arg_type=="Option list":
            if argument not in range:
                raise ValueError(key + "needs to be one of {0}".format((" ").join(range)))
                
                
