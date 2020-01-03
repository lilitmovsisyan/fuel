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
print(df.describe().round(2))

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

print(type(df.index)) # Returns pandas.core.indexes.datetimes.DatetimeIndex
print(df.index) # Inspect the index 
print(df.head())

# %% Sort data:

# With the Timestamp date as the index, you can now slice data by date.
# (but still best to sort the data first, because the index stays in whatever 
# order the data came in!!!)

#df.index = df.index.sort_values()

# Or, alternatively:

df.sort_index(inplace=True)


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

# %% Calculate total for any date slice:
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


# %% Group by month/year and Aggregate functions:

# Group by year and see how many entries in each column per year:

# .count() returns a DataFrame with the number of entries for each column in each group:
print(df.groupby(df.index.year).count())
print(df.groupby([df.index.year, df.index.month]).count())

# .size() returns a Series with the number of rows in each group:
print(df.groupby(df.index.year).size()) 
print(df.groupby([df.index.year, df.index.month]).size())

# Create a new dataframe grouped by year and calculate aggregate functions:
df_annual = df.groupby(df.index.year).agg(
        {'Total':['count', 'sum'],
         'Litres':['count', 'sum'],
         'Price_pL':['count', 'mean'],
         }
        )
# Rename the index as 'Year':
df_annual.index.rename('Year', inplace=True)
# Round results to 2dp:
df_annual = df_annual.round(2)

print(df_annual)

# Create a new dataframe grouped by year and month and calculate aggregate functions:
df_monthly = df.groupby([df.index.year, df.index.month]).agg(
        {'Total':['count', 'sum'],
         'Litres':['count', 'sum'],
         'Price_pL':['count', 'mean'],
         }
        )
# Rename the mulit-level index as 'Year' and 'Month':
df_monthly.index.rename(['Year','Month'], inplace=True)
# Round results to 2dp:
df_monthly = df_monthly.round(2)

print(df_monthly)

# %% Get Monthly Average per year:

#(i.e. not average in each month where some spending occurred, because there 
#were some months where no fuel was bought. That would be the following):
avg_spent_per_month = df.groupby([df.index.year]).Total.mean()


#Instead, we want the annual total divided by 12:

annual_totals = df.groupby([df.index.year]).Total.sum()
# then add a column dividing this result by 12. REMEMBER though, this is a Series object.

#Convert back to DataFrame (also automatically returns the column name):
annual_totals = annual_totals.to_frame()
# create a DataFrame with annual_totals as a column and another column dividing this by 12:
annual_totals['Monthly_avg'] = (annual_totals.Total)/12
#-----
# OK THIS WORKED! I'm gonna try again but this time combine both monthly average methods:
#-----


def monthly_avg():
    return lambda x: x.sum()/12

annual_totals2 = df.groupby([df.index.year]).agg(['sum', 'mean', monthly_avg()])

#inspect column names:
print(annual_totals2.columns.levels[1])
# somehow need to rename the '<lambda>' column!!!!!!!!!!
annual_totals2.rename(level=1, columns={'mean':'mean_per_month', '<lambda>': 'monthly_avg'})
# WHY DOESN'T THIS WORK?? No error is given, but the column is not renamed.

# Round results to 2dp:
annual_totals2 = annual_totals2.round(2) 

print(annual_totals2)

### Could also try doing 2 separate DataFrames, one each for Totals, Litres, Price,
#and here have the month mean and monthly average together
#Could also calculate mean when grouped by month (this would be a separate dataFrame)
annual_total_spend = df.groupby(df.index.year).agg({'Total':['sum','mean', monthly_avg()]})
annual_litres = df.groupby(df.index.year).agg({'Litres':['sum', 'mean', monthly_avg()]})
annual_prices = df.groupby(df.index.year).agg({'Price_pL':['sum', 'mean', monthly_avg()]})

# Round results to 2dp:
annual_total_spend = annual_total_spend.round(2)
annual_litres = annual_litres.round(2)
annual_prices = annual_prices.round(2)


print(annual_total_spend)
print(annual_litres)
print(annual_prices)

#DRAFT
##or maybe:
#monthly_totals = df.groupby([df.index.year, df.index.month]).Total.sum()
##monthly_totals.index.rename(['Year', 'Month'], inplace=True)
#monthly_totals = monthly_totals.unstack()
#avg_per_month = monthly_totals.agg('mean', axis=1) # This takes mean per row, not column (axis=0)
#print(avg_per_month) # BUT uh oh, this average did not take into account the NaN!!! 
##Maybe replace them with 0s, or see if there is a way to get mean including no. of NaN??




# %% Write to Excel:
#
#df_annual.to_excel("fuel_annual.xlsx")
#df_monthly.to_excel("fuel_monthly.xlsx")

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

6. Allow read/write to/from Excel --> lookup how to write to multiple sheets.

7. use DataFrame.round(decimals=2) to round columns to 2 dp 
(provide a dict to specify dp for each column)

8. Find out how best to rename heirarchical columns (count, sum, etc),
especially given dictionary-of-dictionaries- method is deprecated.
Does the method used in explore.py still work? why doesn't it work here?


"""