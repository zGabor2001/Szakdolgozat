# -------------------
# Szakdolgozat kérdőív elemzés
# A Z generáció tanulási szokásai és informatikai hozzáértése
# Készítette: Zeke Gábor
# Utoljára frissítve: 2023.11.23
#--------------------

# -------------------
# Package-k
#--------------------

import pandas as pd
from scipy.stats import chi2_contingency
import researchpy as rp
import statistics
import numpy as np
import regex as re
import warnings

# -------------------
# Függvények
#--------------------

def process_column(column, num_columns):
    column = column.str.replace(r'\(.*\)', '')
    column = column.str.split(',', n=num_columns - 1, expand=True)
    return column

def cramers_v(df, col1, col2):
    # Create a contingency table
    contingency_table = pd.crosstab(df[col1], df[col2])

    data = np.array([df[col1], df[col2]])
    
    X2 = chi2_contingency(contingency_table)[0]
    n = contingency_table.sum().sum()
    min_dim = min(data.shape)-1
    v = np.sqrt((X2/n) / min_dim)
    
    return v

def get_categorical_metrics(df, col1, col2):
    #Khi-négyzet
    contingency_table = pd.crosstab(df[col1], df[col2])    
    chi2, p, _, _ = chi2_contingency(contingency_table) 
    
    #Cramer együttható
    cramer_v = cramers_v(df, col1, col2)
    results = [chi2, p, cramer_v]
    return results

def get_descriptive_stat(df, col):
    freq_table = pd.crosstab(index=df[col], columns=col)
    relative_freq_table = freq_table / freq_table.sum()
    mode = statistics.mode(df[col])
    return freq_table, relative_freq_table, mode

# Function to remove text between parentheses
def remove_text_between_parentheses(text):
    pattern = r'\([^)]*\)'
    result = re.sub(pattern, '', text)
    return result

# -------------------
# Adatbeolvasás
#--------------------

run_mode = input("E: egyetemi, K: Középiskolás, A: Közös: ")

main_dir = 'C:\\Users\\Zeke Gábor\\Desktop\\123\\Szakdoga\\'
question_file = main_dir + '\\data\\kerdoiv_adatok.xlsx'

if run_mode == 'E':
    df_question_data = pd.read_excel(question_file, sheet_name='Egyetem')
    df_question_data.drop(['Tanulmanyok'], axis='columns', inplace=True)
elif run_mode == 'A':
    df_question_data = pd.read_excel(question_file, sheet_name='Közös')
elif run_mode == 'K':
    df_question_data = pd.read_excel(question_file, sheet_name='Középsuli')
    df_question_data.drop(['Tanulmanyok'], axis='columns', inplace=True)
else:
    print("Hibás bemenet.")
    exit()

# -------------------
# Adattisztítás, rendszerezés
#--------------------

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

df_question_data = df_question_data[(df_question_data['Kor'] >= 15) & (df_question_data['Kor'] <= 25)]

df_question_data['RAW_szoftverek'] = df_question_data['RAW_szoftverek'].apply(remove_text_between_parentheses)
df_collab = df_question_data['Kollaboracio_modszerek'].str.get_dummies(sep=', ')
df_softwares = df_question_data['RAW_szoftverek'].str.get_dummies(sep=', ')
df_feedback = df_question_data['Tanar_visszajelz'].str.get_dummies(sep=', ')

df_question_data = pd.concat([df_question_data, df_collab], axis=1)
df_question_data = pd.concat([df_question_data, df_softwares], axis=1)
df_question_data = pd.concat([df_question_data, df_feedback], axis=1)

df_question_data.columns = df_question_data.columns.str.strip()
df_question_data.columns = df_question_data.columns.str.replace(' ', '_', regex=True)

df_question_data.drop(['Tanar_visszajelz', 'Kollaboracio_modszerek', 'RAW_szoftverek'], axis='columns', inplace=True)

df_metrics = df_question_data.iloc[:,2:]
col_list = df_metrics.columns.tolist()

# -------------------
# Leíró statisztika
#--------------------

df_freq_list = []
df_rel_freq_list = []
df_mode_list = []

descriptive_stats_all = df_metrics.describe(include='all')
frequency = df_metrics.apply(lambda x: x.value_counts())
relative_frequency = df_metrics.apply(lambda x: x.value_counts(normalize=True))
    
# -------------------
# Kapcsolatvizsgálat
#--------------------

result_cols_conn = ['Khi_negyzet', 'P-ertek', 'Cramer_eh']
df_results = pd.DataFrame({}, index=result_cols_conn)
rev_col = col_list[::-1]
for count, col in enumerate(col_list):
    for count_rev, col_num in enumerate(range(count + 1, len(rev_col))):
        rev_col_instance = rev_col[col_num]
        if col != rev_col_instance:
            df_results[f'{col}_{rev_col[col_num]}'] = get_categorical_metrics(df=df_metrics, col1=col, col2=rev_col[col_num])
        else:
            continue
        
df_results = df_results.T

# -------------------
# Fájlba íratás
#--------------------

relative_frequency.to_csv(main_dir + f'//data//relative_freq_{run_mode}.csv')
frequency.to_csv(main_dir + f'//data//freq_{run_mode}.csv')
descriptive_stats_all.to_csv(main_dir + f'//data//descriptive_stats_all_{run_mode}.csv', encoding='utf-8-sig')

df_results.to_csv(main_dir + f'//data//mutatok_{run_mode}.csv', encoding='utf-8-sig')
df_question_data.to_csv(main_dir + f'//data//adatok_{run_mode}.csv', encoding='utf-8-sig')

print('Complete')