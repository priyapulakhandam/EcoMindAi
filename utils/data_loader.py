import pandas as pd

def load_energy_data():
    return pd.read_csv("data/energydata_complete.csv")

def load_occupancy_data():
    return pd.read_csv("data/occupancy/datatraining.txt")