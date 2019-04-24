from math import floor
import datetime

def colorRange(row):
    colors = [hex_val for hex_val in range(0x99FA00,0x990000,-0x500)]
    if row['normalized_delay'] > 1:
        return 0x000000
    else:
        return colors[floor(len(colors)*row['normalized_delay'])]
    
def colorRangeHex(delay):
    colors = [hex_val for hex_val in range(0x99FA00,0x990000,-0x500)]
    if delay > 1:
        return hex(0x000000)
    else:
        return hex(colors[floor(len(colors)*delay)])
    

def timeSinceMidnight(row):
    time = row['time_formatted']
    midnight = time.replace(hour=0, 
                            minute=0, 
                            second=0, 
                            microsecond=0)
    return (time - midnight).seconds
    
def groupTime(row):
    time_groups = [time for time in range(0,86400,900)]
    time_normalized = row['time_since_midnight'] / 86400
    return time_groups[floor(len(time_groups)*time_normalized)]

def format_time(seconds):
    hours = seconds // 3600
    seconds = seconds - (hours * 3600)

    minutes = seconds // 60
    seconds = seconds - (minutes * 60)

    return "%d-%d-%d" % (hours, minutes, seconds)