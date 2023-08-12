
import pandas as pd
import numpy as np


df = pd.DataFrame([[np.nan, 1.0, 'A'], [2.0, np.nan, 3.0]])
# df.style.format(na_rep = 'MISS', precision = 3)
df = df.style.format('{:.2f}', na_rep = 'MISS', subset = [0,1])

print(df)