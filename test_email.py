import pandas as pd

df = pd.read_csv("./test_email.csv")

print(len(df['Email'].to_list()))