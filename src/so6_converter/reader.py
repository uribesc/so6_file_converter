"""Readers that convert SO6 flight files into pandas DataFrames."""

import pandas as pd

__all__ = ["add_country_flow", "so6_to_df", "so6_to_df_simple", "so6_to_df_waypoints", "time_to_seconds"]


def add_country_flow(i):
    """Add a ``country_flow`` column (e.g. ``EG_LE``) built from the ICAO prefixes of origin and destination."""
    i['country_flow'] = i.apply(lambda row: sorted([row['origin'][0:2], row['destination'][0:2]]) , axis=1)
    i['country_flow'] = i['country_flow'].str[0] + '_' + i['country_flow'].str[-1]
    i['country_flow'] = i['country_flow'].replace('EI_GC', 'EG_GC') #add ireland to eg flow
    return i

def _to_datetime(date, time):
    """Combine SO6 date (YYMMDD) and time (HHMMSS) series into datetimes."""
    return pd.to_datetime(date.astype(str).str.zfill(6) + time.astype(str).str.zfill(6), format='%y%m%d%H%M%S')

def time_to_seconds(df, date_col='date', time_col='time', out_col='time_s', t0=None):
    """Add a new column with seconds starting from initial time + date (time_s = 0)

    By default the reference instant ``t0`` is the earliest date/time in the DataFrame.
    """
    dt = _to_datetime(df[date_col], df[time_col])
    if t0 is None: t0 = dt.min()
    df = df.copy()
    df[out_col] = (dt - t0).dt.total_seconds().astype(int)
    return df

def so6_to_df(route): #line x line as so6
    """Read a raw SO6 file into a DataFrame with one row per segment, as in the original file."""
    columns = ['segment_id', 'origin', 'destination', 'actype', 'time_ini_seg', 'time_end_seg', 'fl_ini', 'fl_end', 'status', 'callsign',\
               'date_ini', 'date_end', 'lat_ini', 'lon_ini', 'lat_end', 'lon_end', 'flightid', 'sequence', 'segment_length', 'segment_color']
    data = []

    with open(route) as doc:
        for line in doc:
            line = line.split()
            data.append(line)

    df = pd.DataFrame(data, columns=columns)

    #transform coordinates into decimal
    df['lat_ini'] = df['lat_ini'].astype(float)/60
    df['lat_end'] = df['lat_end'].astype(float)/60
    df['lon_ini'] = df['lon_ini'].astype(float)/60
    df['lon_end'] = df['lon_end'].astype(float)/60

    #transform numeric values into numeric
    df['segment_length'] = df['segment_length'].astype(float)
    df['fl_ini']  = df['fl_ini'].astype(int)
    df['fl_end']  = df['fl_end'].astype(int)
    df['status']  = df['status'].astype(int)
    df['sequence']  = df['sequence'].astype(int)
    df['segment_color']  = df['segment_color'].astype(int)

    #create new column total_distance
    dist_sum = df.groupby('flightid')['segment_length'].sum().reset_index()
    df = df.merge(dist_sum, on='flightid', suffixes=('', '_sum'))
    df = df.rename(columns={'segment_length_sum': 'flown_distance'})
    df1 = add_country_flow(df)
    #seconds for segment start and end, both from the same reference instant
    t0 = _to_datetime(df1['date_ini'], df1['time_ini_seg']).min()
    df2 = time_to_seconds(df1, 'date_ini', 'time_ini_seg', 'time_ini_s', t0)
    df2 = time_to_seconds(df2, 'date_end', 'time_end_seg', 'time_end_s', t0)
    return df2

def so6_to_df_simple(route): #one line x flight list with lat, lon, alt, no segments, simplifyed
    """Read an SO6 file into a DataFrame with one row per flight; lat/long/alt/time/date are lists."""
    columns = ['callsign', 'flightid', 'origin', 'destination', 'lat', 'long', 'alt', 'time', 'date', 'total_distance', 'actype']
    data = []
    last = ''
    with open(route) as doc:
        tmp = []
        for line in doc:
            line = line.split()
            if line[16] != last:
                if len(tmp)>0: data.append(tmp)
                tmp = []
                tmp.append(line[9])
                tmp.append(line[16])
                tmp.append(line[1])
                tmp.append(line[2])
                tmp.append([float(line[12])/60])
                tmp.append([float(line[13])/60])
                tmp.append([int(line[6])])
                tmp.append([line[4]])
                tmp.append([line[10]])
                tmp.append(float(line[18]))
                tmp.append(line[3])
                last = line[16]

            else:
                tmp[4].append(float(line[12])/60)
                tmp[5].append(float(line[13])/60)
                tmp[6].append(int(line[6]))
                tmp[7].append(line[4])
                tmp[8].append(line[10])
                tmp[9]+= float(line[18])
        if len(tmp)>0: data.append(tmp) #last flight

    df = pd.DataFrame(data, columns=columns)
    df1 = add_country_flow(df)
    #time and date are lists per flight, so time_s is also a list
    points = df1[['date', 'time']].explode(['date', 'time'])
    seconds = time_to_seconds(points)['time_s']
    df1['time_s'] = seconds.groupby(level=0).agg(list)
    return df1

def so6_to_df_waypoints(route): #structured x waypints, one line x wpt
    """Read an SO6 file into a DataFrame with one row per waypoint, removing duplicates."""
    columns = ['callsign', 'flightid', 'waypoint', 'origin', 'destination', 'lat', 'lon', 'alt', 'time', 'date', 'actype']
    data = []
    with open(route) as doc:
        for line in doc:
            tmp = [] #first wpt
            line = line.split()
            wpt1, wpt2 = line[0].split("_")
            tmp.append(line[9]) #callsign
            tmp.append(line[16]) #flightid
            tmp.append(wpt1)
            tmp.append(line[1]) #ori
            tmp.append(line[2]) #dest
            tmp.append(float(line[12])/60) #lat
            tmp.append(float(line[13])/60) #lon
            tmp.append(int(line[6])) #alt
            tmp.append(line[4]) #time
            tmp.append(line[10]) #date
            tmp.append(line[3]) #actype
            data.append(tmp)

            tmp = [] #secondwpt
            tmp.append(line[9]) #callsign
            tmp.append(line[16]) #flightid
            tmp.append(wpt2)
            tmp.append(line[1]) #ori
            tmp.append(line[2]) #dest
            tmp.append(float(line[14])/60) #lat
            tmp.append(float(line[15])/60) #lon
            tmp.append(int(line[7])) #alt
            tmp.append(line[5]) #time
            tmp.append(line[11]) #date
            tmp.append(line[3]) #actype
            data.append(tmp)

    df = pd.DataFrame(data, columns=columns)
    df1 = add_country_flow(df)
    df2 = time_to_seconds(df1)

    return df2.drop_duplicates()
