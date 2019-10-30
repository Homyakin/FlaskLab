import pandas as pd
pd.options.display.max_columns = 999
if __name__ == "__main__":
    print(pd.read_csv("data.csv").shape)
