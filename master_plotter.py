import os
from file_reader import read
from plot_funcs import Electrochem_plots
from matplotlib.pyplot import show, subplots_adjust
loc="/home/henney/Documents/Oxford/Experimental_data/Alice/Immobilised_Fc/GC-1/Fc/Exported/"
example_file_list=os.listdir(loc) #This is how you can find a list of files in a directory
sub_str="PSV"
read_files=read(
        example_file_list, #List of file names - if not in the directory with master_plotter, and address needs to be provided file_loc
        header=1, #Number of rows to skip - if this not constant between files, you will need to provide a list [x,y...] of the appropriate skipnumber
        footer=0, #Ditto
        file_loc=loc,# File location of your files. Defaults to the current directory if not provided
        substring=sub_str) #If provided, will ignore files without substring in the name

Electrochem_plots(
    read_files.data, 
    order=["time",  "current","potential",], #Order of data in the columns. If for whatever reason your files have different ordering, you will need to provide the order for each file
    desired_plots=["potential-current","time-potential", "potential-harmonics", "Fourier"], #desired plots. Unless it's Fourier then the format is X-Y (for time/potential/current/harmonics)
    one_tail=True, #If True then ignore negative frequencies in FT
    Fourier_harmonic_crop=True, #If True then will crop the Fourier transform to the max harmonic in desired_harmonics
    FourierScale="log", #either "log" or "none" for FT
    FourierFunc="Real", # "Abs", "Real", or "Imag" for FT
    Fourier_frequency_lines=True, #WIll attempt to draw lines on the Fourier transform at the location of the harmonics
    harmonics_box=0.5, #Width of the inverse transform box when calculating the harmonics
    desired_harmonics=list(range(1,12)), #Harmonics to be plotted (it may be that your spectrum does not go up that high, in which case they won't be plotted)
    harmonic_hanning=False, #Whether or not to apply the hanning transform which suprresses the signal at the start and end of the experiment
    harmonic_funcs="Real", # "Abs", "Real", or "Imag" for harmonics
    current_scaling=1000, #factor multipy current by (milli micro nano etc)
    potential_scaling=1000, #ditto for potential, 
    harmonic_number=True, #True/False for showing the harmonic number
    labels=[""], #What you want each trace to be called - needs to be a list, e.g ["exp_1", "exp_2"]
    legend_loc=0,#which plot you want your legend to go in, 
    colour='red',
    DC_only=False,#If you want to plot the DC component of the potential
    decimation=32,#Degree of plot decimation
    print_FTV_info=True,
    
)
subplots_adjust(
                top=0.992, 
                left=0.05, 
                right=0.960, 
                bottom=0.105, 
                wspace=0.85,
                hspace=0.0,
)
show()