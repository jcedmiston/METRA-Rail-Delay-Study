from helpers import *
import pandas as pd

train_data = pd.read_csv("data/trip.csv", header=None, na_values='\\N')
train_data.columns = ["time", 
                      "time_formated", 
                      "id", 
                      "route_id", 
                      "vehicle_id", 
                      "vehicle_label", 
                      "delay", 
                      "lat", 
                      "lon", 
                      "general_weather", 
                      "temp", 
                      "temp_min", 
                      "temp_max", 
                      "visibility", 
                      "wind_speed"]
train_data["time_formatted"] = pd.to_datetime(train_data["time_formatted"])

train_data['normalized_delay'] = train_data['delay'] / (train_data['delay'].std() * 1)
train_data['color'] = train_data.apply(colorRange, axis=1)
train_data['time_since_midnight'] = train_data.apply(timeSinceMidnight, axis=1)
train_data['time_group_since_midnight'] = train_data.apply(groupTime, axis=1)
train_data['lat_round'] = train_data.apply(lambda row: round(row['lat'],3), axis=1)
train_data['lon_round'] = train_data.apply(lambda row: round(row['lon'],3), axis=1)

train_data.to_csv('data/train_data.csv')