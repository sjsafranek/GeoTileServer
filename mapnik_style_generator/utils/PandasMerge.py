#table join
#stefan safranek
import csv, os, sys, time
import pandas as pd

start_time = time.time()    #start time

#File 1
IMPORT_FILE = "Burns_wO_LnLID.csv"
SAVE_FILE = IMPORT_FILE.replace('.csv','') + " MATCHED.csv"

df1 = pd.read_csv("Burns HD 58.csv", index_col=None, usecols=[0,1,2,4], parse_dates=True)
df2 = pd.read_csv(IMPORT_FILE, index_col=None, usecols=[0,1,2], parse_dates=True)

df = pd.merge(df1,df2)
df.to_csv(SAVE_FILE,on='Voters_StateVoterID',how='right')
#df.to_csv(SAVE_FILE,on='Full_Name',how='right')



end_time = time.time()
run_time = end_time - start_time
print run_time

#time.sleep(15)



