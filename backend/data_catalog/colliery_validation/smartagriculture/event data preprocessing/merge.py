import pandas as pd
import glob


list_of_dict = []
# setting the path for joining multiple files
files = "in_log/*.csv"

# list of merged files returned
files = glob.glob(files)

df = pd.concat(map(pd.read_csv, files), ignore_index=True)

# sort events by time
df['time'] = pd.to_datetime(df['time'])
df = df.sort_values(by='time')


mfile = "MRS.csv"
df.to_csv(mfile, index=False)

