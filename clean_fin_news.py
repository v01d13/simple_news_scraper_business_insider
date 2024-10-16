import glob
import pandas as pd
import re

all_files = glob.glob("data/*.csv")
print('all_files',all_files)

df_from_each_file = (pd.read_csv(f) for f in all_files)
concatenated_df = pd.concat(df_from_each_file, ignore_index=True)

concatenated_df.head()

concatenated_df['details'] = concatenated_df.apply(lambda row: re.sub(re.escape(str(row['source'])), '', str(row['details'])) if str(row['source']) in str(row['details']) else row['details'], axis=1)

concatenated_df.head()

concatenated_df = concatenated_df.drop(['Unnamed: 0.1', 'Unnamed: 0'], axis=1)

concatenated_df.head()

concatenated_df['details'] = concatenated_df['details'].str.replace(r'EQS-News: Kaplan Fox \/ Key word\(s\):', '', regex=True)
concatenated_df['details'] = concatenated_df['details'].str.replace(r'EQS Newswire \/ \d{2}/\d{2}/\d{4} / \d{2}:\d{2} CET\/CEST', '', regex=True)
concatenated_df['details'] = concatenated_df['details'].str.replace(r'Stock Market News, Stock Advice & Trading Tips', '', regex=True)
concatenated_df['details'] = concatenated_df['details'].str.replace(r'^.* \d{2}, \d{4} \/PRNewswire\/ -', '', regex=True)
concatenated_df['details'] = concatenated_df['details'].str.replace(r'Rating Action:', '', regex=True)
concatenated_df['details'] = concatenated_df['details'].str.replace(r'(Pre|Post) Stabilisation NoticeNEW YORK,? NY.*\d{4} \/ HSBC', '', regex=True)
concatenated_df['details'] = concatenated_df['details'].str.replace(r'\(\) - ', '', regex=True)


for source in concatenated_df['source'].unique():
  print(source)
  row = concatenated_df[concatenated_df['source'] == source].head(5)
  print(row['details'])

row_23056 = concatenated_df.loc[23056]
details_truncated = (row_23056['details'][:500] + '..') if len(row_23056['details']) > 100 else row_23056['details']
# print(details_truncated)

row_23204 = concatenated_df.loc[23204]
details_truncated = (row_23204['details'][:500] + '..') if len(row_23204['details']) > 100 else row_23204['details']
# print(details_truncated)

## TODO:
    # 1. Check the last two printed rows
    # 2. What are those?
    # 3. Clean?????