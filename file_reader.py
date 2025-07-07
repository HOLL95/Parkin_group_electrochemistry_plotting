from numpy import loadtxt, column_stack
import re
from pandas import read_csv, read_excel ,read_sql_query
import os
import platform
import sqlite3
class read:
    def __init__(self, name, **kwargs):
        if "header" not in kwargs:
            kwargs["header"]=0
        if "footer" not in kwargs:
            kwargs["footer"]=0
        if "file_loc" not in kwargs:
            directory=os.getcwd()
        else:   
            directory=kwargs["file_loc"]
        if "substring" not in kwargs:
            kwargs["substring"]=None
        if "desired_cols" not in kwargs:
            kwargs["desired_cols"]=False
        if "sql_table" not in kwargs:
            kwargs["sql_table"]="point"
        if "sql_mapping" not in kwargs:
            init_mapping={"t":"time", "y":"current", "z":"potential"}
            kwargs["sql_mapping"]={init_mapping[key]:key for key in init_mapping.keys()}
       
        elif isinstance(kwargs["desired_cols"], list) is False:
            raise TypeError("desired_cols needs to be of type list")
        self.sql_mapping=kwargs["sql_mapping"]
        self.sql_table=kwargs["sql_table"]
        if isinstance(name,str):
            filetype=self.detect_filetype(name)
            if filetype==None:
                raise ValueError("No files of the right type found")
            total_address=os.path.join(directory, name)
            file=self.read_file(total_address, filetype, header=kwargs["header"], footer=kwargs["footer"])
            if kwargs["desired_cols"] is not False:
                file=column_stack(([file[:,x] for x in kwargs["desired_cols"]]))
            self.data=[file]
        elif isinstance(name,list):
            data_list=[]
            if isinstance(kwargs["header"], int):
                kwargs["header"]=[kwargs["header"]]*len(name)
            if isinstance(kwargs["footer"], int):
                kwargs["footer"]=[kwargs["footer"]]*len(name)
            if kwargs["desired_cols"] is not False:
                if isinstance(kwargs["desired_cols"][0], list) is False:
                    kwargs["desired_cols"]=[kwargs["desired_cols"]]*len(name)
            if kwargs["substring"]!=None:
                self.name_list=[]
            else:
                self.name_list=name
            exclude_list=[]
            for i in range(0, len(name)):
                if kwargs["substring"]!=None:
                    if kwargs["substring"] not in name[i]:
                        continue
                    else:
                        self.name_list.append(name[i])
                
                filetype=self.detect_filetype(name[i])
               
                if filetype!=None:
                    
                    already_in=False
                    if filetype=="cv_":
                        true_name=re.findall( ".+(?=cv_)", name[i])[0]
                        
                        for element in exclude_list:
                            if true_name in element:
                                already_in=True
                    if already_in is not True:  
                        
                        total_address=os.path.join(directory, name[i])
                        
                        file=self.read_file(total_address, filetype, header=kwargs["header"][i], footer=kwargs["footer"][i])
                        if kwargs["desired_cols"] is not False:
                            file=column_stack(([file[:,x] for x in kwargs["desired_cols"][i]]))
                        data_list.append(file)
                        if filetype=="cv_":
                            exclude_list.append(name[i])
                       
                          

            self.data=data_list
        else:
            raise TypeError("Needs to either be a file or list of files")
    def get_data(self):
        return self.data
    
    def detect_filetype(self, file):
        filetype=None
        accepted_files=[".csv", ".txt", ".xlsx", "cv_", ".sqlite"]
        for extension in accepted_files:
            if extension in file:
                filetype=extension
                break
        if filetype==None:
           print("File needs to be {0}, skipping {1}".format(("/").join(accepted_files), file) )
        return  filetype
    def read_file(self, name, filetype, header, footer):
        print("Reading {0}".format(name))
        if filetype==".txt":
            data=loadtxt(name, skiprows=header)
        elif filetype==".csv":
            pd_data=read_csv(name, sep=",", encoding="utf-16", engine="python", skiprows=header, skipfooter=footer)
            data=pd_data.to_numpy(copy=True, dtype='float')
        elif filetype==".xlsx":
            pd_data = read_excel(name,engine='openpyxl', skiprows=header, skipfooter=footer)
            data = pd_data.to_numpy(copy=True, dtype='float')
        elif "cv_" in name:
            true_name=re.findall( ".+(?=cv_)", name)[0]
            current=loadtxt(true_name+"cv_current")
            potential=loadtxt(true_name+"cv_voltage")
            data=column_stack((current, potential[:,1]))    
            print("Warning - Monash intrument data stored as time-current-potential")
        elif ".sqlite" in name:
            conn = sqlite3.connect(name)
            cursor=conn.cursor()
            table_name=self.sql_table
            
            df = read_sql_query("SELECT {0} FROM {1}".format(", ".join([self.sql_mapping[x] for x in ["time", "current","potential"]]), table_name), conn)
            data=df.to_numpy()
            conn.close()
        return data
