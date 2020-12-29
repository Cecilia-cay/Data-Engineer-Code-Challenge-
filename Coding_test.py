import json
from urllib.request import Request, urlopen
import pandas as pd
import time
import datetime
from sodapy import Socrata
import matplotlib.pyplot as plt

# problem 1: load data
# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("data.pa.gov", None)

# Example authenticated client (needed for non-public datasets):
# client = Socrata(data.pa.gov,
#                  MyAppToken,
#                  userame="user@example.com",
#                  password="AFakePassword")


results = client.get("mcba-yywm", limit=3085255)

# Convert to pandas DataFrame
application_in = pd.DataFrame.from_records(results)

# problem 2: Remove all rows from application_in that contain null values in ANY column and
# place them in a data structure (data type of your choosing) named “invalid_data”

invalid_data = application_in[application_in.T.isnull().any()]
application_in = application_in.dropna(how='any',axis=0).copy()

# problem 3: Convert all state senate district (senate) entries in application_in to snake case

application_in['senate'] = application_in['senate'].apply(lambda x: x.lower().replace(" ","_"))

# problem 4: Create a new field in application_in, “yr_born”, that contains each voter’s year of birth (dateofbirth).
# The data type should be an integer. The yr_born field should appear immediately right of “dateofbirth”.

col_name = application_in.columns.tolist()
col_name.insert(col_name.index('dateofbirth') + 1, 'yr_born')
application_in['yr_born'] = application_in['dateofbirth'].apply(lambda x: int(x[:4]))
application_in = application_in.reindex(columns=col_name)

# problem 5: How does applicant age (in years) and party designation (party) relate to overall vote by mail requests?

application_in.groupby('yr_born')['mailapplicationtype'].agg('count').plot.bar(figsize=(30,8))
plt.show()
application_in.groupby('party')['mailapplicationtype'].agg('count').plot.bar(figsize=(30,8),fontsize=5)
plt.show()

# problem 6: What was the median latency from when each legislative district (legislative)
# issued their application and when the ballot was returned?

valid_data = application_in.copy()
valid_data['latency'] = pd.to_datetime(valid_data['ballotreturneddate'],errors='coerce',format='%Y-%m-%dT%H:%M:%S.%f') - pd.to_datetime(valid_data['appissuedate'],errors='coerce',format='%Y-%m-%dT%H:%M:%S.%f')
valid_data = valid_data.dropna(how='any',axis=0).copy()
valid_data['latency'] = valid_data['latency'].apply(lambda x : int(str(x).split()[0]))
valid_data.groupby('legislative')['latency'].agg('median')

# problem 7: What is the congressional district (congressional) that has the highest frequency of ballot requests?

congressional_district = application_in.groupby('congressional')['appissuedate'].agg('count').idxmax()
print("congressional district")
print(congressional_district)


# problem 8: Create a visualization demonstrating the republican and democratic application counts in each county.
party = application_in.groupby(['countyname','party'])['party'].agg('count').unstack()
party = party[['D','R']]
party.plot.bar(figsize=(30,7))
plt.xlabel('county')
plt.ylabel('counts')
plt.show()
