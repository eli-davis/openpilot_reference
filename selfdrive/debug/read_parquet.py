import pandas as pd
import os

# dir_ = '/home/deepview/SSD/pathfinder/out.parquet'

# files = os.listdir(dir_)

# files = sorted([os.path.join(dir_, file) for file in files])

# df = pd.DataFrame()

# file = files[-1]
# print(file)
df = pd.read_parquet('out.parquet')
print(df.describe())

print(df.head())
# break