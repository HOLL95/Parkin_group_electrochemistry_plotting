import os
from file_reader import read
from plot_funcs import Electrochem_plots
from matplotlib.pyplot import show, subplots_adjust
loc="/home/henney/Documents/Oxford/Experimental_data/Gamry"
example_file_list=os.listdir(loc) #This is how you can find a list of files in a directory
read_files=read(
        ["my_data_141123_1_Ferricyanide_72Hz_ALAN_BOND_cond.txt"], #List of file names - if not in the directory with master_plotter, and address needs to be provided file_loc
        header=1, #Number of rows to skip - if this not constant between files, you will need to provide a list [x,y...] of the appropriate skipnumber
        footer=0, #Ditto
        file_loc=loc,# File location of your files. Defaults to the current directory if not provided
        desired_cols=[0,1,2],
        ) #If provided, will ignore files without substring in the name

Electrochem_plots(
    read_files.data, 
    order=["time", "potential","current"], #Order of data in the columns. If for whatever reason your files have different ordering, you will need to provide the order for each file
    desired_plots=["time-current","time-potential", "time-harmonics", "Fourier"], #desired plots. Unless it's Fourier then the format is X-Y (for time/potential/current/harmonics)
    one_tail=True, #If True then ignore negative frequencies in FT
    Fourier_harmonic_crop=True, #If True then will crop the Fourier transform to the max harmonic in desired_harmonics
    FourierScale="log", #either "log" or "none" for FT
    FourierFunc="Real", # "Abs", "Real", or "Imag" for FT
    Fourier_frequency_lines=True, #WIll attempt to draw lines on the Fourier transform at the location of the harmonics
    harmonics_box=0.05, #Width of the inverse transform box when calculating the harmonics
    desired_harmonics=list(range(1,12)), #Harmonics to be plotted (it may be that your spectrum does not go up that high, in which case they won't be plotted)
    harmonic_hanning=True, #Whether or not to apply the hanning transform which suprresses the signal at the start and end of the experiment
    harmonic_funcs="Abs", # "Abs", "Real", or "Imag" for harmonics
    current_scaling=1000000, #factor multipy current by (milli micro nano etc)
    potential_scaling=1000, #ditto for potential, 
    harmonic_number=True, #True/False for showing the harmonic number
    labels=["Gamry"], #What you want each trace to be called - needs to be a list, e.g ["exp_1", "exp_2"]
    legend_loc=0,#which plot you want your legend to go in, 
    colour="blue",
    DC_only=False,#If you want to plot the DC component of the potential
    decimation=10,#Degree of plot decimation,
    print_FTV_info=True,
    save_as_csv=False
    
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