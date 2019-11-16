import pandas as pd
pd.options.display.max_columns = 200

if __name__ == "__main__":
    data = pd.read_csv('data.csv')
    data = data[['EmploymentField', 'EmploymentStatus',
                 'Gender', 'LanguageAtHome',
                 'JobWherePref', 'SchoolDegree',
                 'Income']]
    data = data[data['Gender'].isin(['male', 'female'])]
    data.dropna(inplace=True)
    for i in data:
        print(i, data[i].unique())
