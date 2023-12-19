from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import pandas as pd
import warnings
import regex as re

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.preprocessing import LabelEncoder
import pandas as pd

def remove_text_between_parentheses(text):
    pattern = r'\([^)]*\)'
    result = re.sub(pattern, '', text)
    return result

def calculate_r_squared(df, numerical_column, categorical_column):
    le = LabelEncoder()
    df[categorical_column] = le.fit_transform(df[categorical_column])
    X = df[[numerical_column]]
    y = df[categorical_column]
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    r_squared = r2_score(y, y_pred)
    return r_squared

# -------------------
# Adatbeolvasás
#--------------------

run_mode = input("E: egyetemi, K: Középiskolás, A: Közös: ")

main_dir = 'C:\\Users\\Zeke Gábor\\Desktop\\123\\Szakdoga\\'
question_file = main_dir + '\\data\\11_15.xlsx'

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

df_metrics = df_question_data.iloc[:,1:]

df_metrics.rename(columns={'Pénzügyi-könyvelési': 'Pu_konyv', 'Weboldal-szerkesztő': 'Weboldal_szerk'}, inplace=True)
categorical_variables = df_metrics.columns[1:]

results_df = pd.DataFrame(columns=['Valtozo', 'F_ertek', 'P_ertek'])

numerical_col = df_metrics.iloc[:,0]

numerical_column_name = 'Kor'
categorical_columns = df_metrics.columns[1:]
results = []

for cat_col in categorical_columns:
    r_squared_value = calculate_r_squared(df_metrics, numerical_column_name, cat_col)
    results.append({'numerical_column': numerical_column_name, 'categorical_column': cat_col, 'r_squared': r_squared_value})

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Save results to a CSV file
results_df.to_csv(f'{main_dir}//data//r_squared_{run_mode}.csv', index=False)