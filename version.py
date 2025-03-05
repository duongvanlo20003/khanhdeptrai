import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

with open("q_table_player1.pkl", "rb") as f:
    data = pickle.load(f)

if isinstance(data, dict):
    for key, value in data.items():
        print(f"{key}: {type(value)}")  # Xem kiểu dữ liệu từng phần
elif isinstance(data, list):
    print(f"List có {len(data)} phần tử. Phần tử đầu tiên là {type(data[0])}")
print("_______________________________________________________________")
with open("q_table_player2.pkl", "rb") as f:
    data = pickle.load(f)

if isinstance(data, dict):
    for key, value in data.items():
        print(f"{key}: {type(value)}")  # Xem kiểu dữ liệu từng phần
elif isinstance(data, list):
    print(f"List có {len(data)} phần tử. Phần tử đầu tiên là {type(data[0])}")