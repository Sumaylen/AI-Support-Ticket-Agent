import os
import pandas as pd
from sklearn.model_selection import train_test_split

def load_dataset_split():
    DATASET_PATH = os.path.abspath("data/Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv")

    df = pd.read_csv(DATASET_PATH)
    #.train_test_split(*arrays, test_size=None, train_size=None, random_state=None, shuffle=True, stratify=None)
    #split the data into  training set and test set
    train_df, test_df = train_test_split(df, test_size=0.01, random_state=42)

    return train_df, test_df
