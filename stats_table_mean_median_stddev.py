import pandas as pd

data = pd.read_csv('all_data.csv')
stats = data.groupby(['Condition', 'Texture']).agg({'Ratings': ['mean', 'median', 'std']})
stats.columns = ['Mean Rating', 'Median Rating', 'Standard Deviation']
print(stats)
