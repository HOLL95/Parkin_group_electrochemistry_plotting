import os
from file_reader import read
from plot_funcs import Electrochem_plots
from matplotlib.pyplot import show, subplots_adjust
example_file_list=os.listdir("Examples") #This is how you can find a list of files in a directory
read_files=read(
        example_file_list, #List of file names - if not in the directory with master_plotter, and address needs to be provided file_loc
        header=1, #Number of rows to skip - if this not constant between files, you will need to provide a list [x,y...] of the appropriate skipnumber
        footer=0, #Ditto
        file_loc="Examples",# File location of your files. Defaults to the current directory if not provided
        substring=None) #If provided, will ignore files without substring in the name
Electrochem_plots(
    read_files.data, 
    order=["time", "current", "potential"], #Order of data in the columns. If for whatever reason your files have different ordering, you will need to provide the order for each file
    desired_plots=["potential-current", "potential-harmonics", "Fourier", "time-harmonics"], #desired plots. Unless it's Fourier then the format is X-Y (for time/potential/current/harmonics)
    one_tail=True, #If True then ignore negative frequencies in FT
    Fourier_harmonic_crop=True, #If True then will crop the Fourier transform to the max harmonic in desired_harmonics
    FourierScale="none", #either "log" or "none" for FT
    FourierFunc="Real", # "Abs", "Real", or "Imag" for FT
    Fourier_frequency_lines=True, #WIll attempt to draw lines on the Fourier transform at the location of the harmonics
    harmonics_box=0.25, #Width of the inverse transform box when calculating the harmonics
    desired_harmonics=list(range(1, 4)), #Harmonics to be plotted (it may be that your spectrum does not go up that high, in which case they won't be plotted)
    harmonic_hanning=True, #Whether or not to apply the hanning transform which suprresses the signal at the start and end of the experiment
    harmonic_funcs="Real", # "Abs", "Real", or "Imag" for harmonics
    current_scaling=1000, #factor multipy current by (milli micro nano etc)
    potential_scaling=1000, #ditto for potential, 
    harmonic_number=True #True/False for showing the harmonic number
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