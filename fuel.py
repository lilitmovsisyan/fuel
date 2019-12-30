# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 16:22:14 2019

@author: lilit
"""

import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# %% Read data and get initial info:

file = "fuel_data.csv" ###MAYBE CHANGE THIS TO EXCEL, AND ALSO ALLOW READ/WRITE???
df = pd.read_csv(file)

print(df.head())
print(df.info())
print(df.columns)
print(df.shape)
print(df.describe())

# %% Convert dates to Timestamp and set dates as index:

# Create a new column by converting data.Date to a Series containing Timestamp objects:
#df['date'] = pd.to_datetime(df['Date'], infer_datetime_format=True)
# ^ This method did not work: automatically infers US date system of 
#MM/DD/YYYY >> YYYY-MM-DD

# Use dayfirst=True to specif European style, not US style date!
df['date'] = pd.to_datetime(df['Date'], dayfirst=True)

# Using format=... would also work:
#df['date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

print(df.head())
print(type(df.date[0])) # Returns pandas._libs.tslibs.timestamps.Timestamp

# Remove old 'Date' column and set new Timestamp date column as index.
df.drop(['Date'], axis=1, inplace=True)
df = df.set_index('date')
print(df.head())

# %% Sort data:

# With the Timestamp date as the index, you can now slice data by date.
# (but still best to sort the data first, because the index stays in whatever 
# order the data came in!!!)

df.index = df.index.sort_values()

# %% Count nulls:

def count_null(dataframe):
    nulls = dataframe.isnull().any()
    nulls_sum = dataframe.isnull().sum()
    counts = dataframe.count()
    percentage = (nulls_sum / counts)*100
    null_count = pd.concat([nulls, nulls_sum, counts, percentage], 
                           keys=['missing data', 'total missing', 'total data', '% missing'],
                           axis=1,
                           ).round({'% missing':2})
    return null_count


print(count_null(df))


# %% Get Totals:

print(round(df.Total.sum(), 2))
print(round(df.Litres.sum(), 2))
print(round(df.Price_pL.mean(), 2))

"""
#NB: This function uses defaults of start=None and end=None for good reason:
 df[:] returns the entire set.
 df['2019-01-01':] returns everything from 2019 onwards
 df[:'2018-01-01'] returns everything up to 2019
 BUT
 If instead we used start=0 and end=-1, then:
     - It would take an EXCLUSIVE set, i.e. would NOT include the last item
     i.e. df[0:-1] EXCLUDES the final item
     
     So, instead, df[0:] would work: it would include the last item.
     - But then you can't mix the default start with date selection:
         i.e. df[0:'2018-01-01'] WOULD NOT WORK: 
         instead, need to use df[:'2018-01-01] to get everything up to 2019.  
"""

def total_spent(start=None, end=None):
    """
    Returns total money spent on fuel within a certain period
    as a float to 2 decimal places.
    Takes start date and end date as string arguments.
    If no arguments given, returns the total spent over entire dataframe period.
    """
    
    total = df[start:end].Total.sum()
    return round(total, 2)

print(total_spent())
print(total_spent('2014-12-12','2016-02-08'))
print(total_spent(start='2018-01-01', end=None))
print(total_spent(start=None, end='2018-01-01'))


# %% TO DO:

"""

INFO:
- how best to round to 2dp and keep as a float: 
    python round(number[, ndigits])
  An alternative method that has other more flexible options:
      format(number, '.2f')
      .2 means 2dp, and f means float. Look up other permutations!!


- how to select a slice with inclusive end: use end=None, NOT end=-1!!!
- slice for date period IS inclusive
- BUT can't use 0 and a mis of date indexing. Instead, use None.
----

1. Maybe I shouldn't remove the old 'Date' column in terms of
writing data back to the file later?

2. Sort out Null values and the inferred prices (calculated from total and litres)
    - what to do about the inferred prices? 
        - delete the ones calculated in excel and replace with pandas function?
        - make sure there is a function that will calculate the price per litre
        for any future entry which contains total and litres but not price.
        - write the values back into Ecel/ CSV file.
    - do stats comparing whether using dataset that:
        (a) ignores rows with null values
        (b) replaces them with some sort of guess (average? mode? based on spend)

3. Create graphs:
    - Time v spend
    - Time v price
    - histogram of Litres x frequency
    - bar chart of average price x location
    - bar chart of average price x company
    - histogram of prices x frequency per location
4. Add lines/spots on the graph indicating dates I was in bristol/london or 
on trips like Bball/Lydney/etc. 

5. Do some string formatting to make outputs look nice

6. Allow read/write to/from Excel.

7. use DataFrame.round(decimals=2) to round columns to 2 dp 
(provide a dict to specify dp for each column)

"""