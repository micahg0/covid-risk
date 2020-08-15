import pandas as pd
import altair as al


fips_dict = {
'Washington':53,
'Illinois':17,
'California':6,
'Arizona':4,
'Massachusetts':25,
'Wisconsin':55,
'Texas':48,
'Nebraska':31,
'Utah':49,
'Oregon':41,
'Florida':12,
'New York':36,
'Rhode Island':44,
'Georgia':13,
'New Hampshire':33,
'North Carolina':37,
'New Jersey':34,
'Colorado':8,
'Maryland':24,
'Nevada':32,
'Tennessee':47,
'Hawaii':15,
'Indiana':18,
'Kentucky':21,
'Minnesota':27,
'Oklahoma':40,
'Pennsylvania':42,
'South Carolina':45,
'District of Columbia':11,
'Kansas':20,
'Missouri':29,
'Vermont':50,
'Virginia':51,
'Connecticut':9,
'Iowa':19,
'Louisiana':22,
'Ohio':39,
'Michigan':26,
'South Dakota':46,
'Arkansas':5,
'Delaware':10,
'Mississippi':28,
'New Mexico':35,
'North Dakota':38,
'Wyoming':56,
'Alaska':2,
'Maine':23,
'Alabama':1,
'Idaho':16,
'Montana':30,
'Puerto Rico':72,
'Virgin Islands':78,
'Guam':66,
'West Virginia':54,
'Northern Mariana Islands':69,
}

# download population
pop = pd.read_csv('https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv',
                  usecols=['STATE', 'COUNTY', 'POPESTIMATE2019'])
pop['county_padded'] = pop.COUNTY.apply(lambda x: str(x).zfill(3))
pop['fips'] = (pop.STATE.astype(str) + pop.county_padded).astype(int)
pop = pop[pop['STATE']!='Puerto Rico']
pop.rename({'POPESTIMATE2019': 'population',
           'STATE': 'state-code',
           'COUNTY': 'county-code'}, axis=1, inplace=True)
pop['fips'] = pop.apply(lambda x: x['state-code'] if x['county-code']==0 else x['fips'], axis=1)
pop.drop(['county_padded'], axis=1, inplace=True)

us_pop = pop[pop['county-code']==0]['population'].sum()
us_pop_df = pd.DataFrame({'state-code': [0],
                          'county-code': [0],
                          'population': [us_pop],
                          'fips': [0]})
pop = pd.concat([pop, us_pop_df], axis=0)
pop.to_csv('./data/census-population.csv', index=False)

# download nytimes covid data - county
county = pd.read_csv('https://github.com/nytimes/covid-19-data/raw/master/us-counties.csv')
county['date'] = county['date'].astype('datetime64[D]')
county['fips'] = county['fips'].fillna(0)
county['fips'] = county['fips'].astype('int64')
county['fips'] = county.apply(lambda x: -fips_dict[x['state']] if x['fips']==0 else x['fips'], axis=1)

# download nytimes covid data - state
state = pd.read_csv('https://github.com/nytimes/covid-19-data/raw/master/us-states.csv')
state['date'] = state['date'].astype('datetime64[D]')
state['county'] = '(all)'
state = state[state['fips']<57] # drop non-50 states

# create country column
country = state.groupby('date', as_index=False )['cases', 'deaths'].sum()
country['state'] = '(all)'
country['county'] = 'USA'
country['fips'] = 0

# combine into one dataset

df = pd.concat([county, state, country], axis=0)
df = df.merge(pop, on='fips', how='left')
df = df.dropna()
df.to_csv('./data/nytimes-covid.csv', index=False)

# calculate rolling sum
df['population'] = df['population'].astype('int64')
df['state-code'] = df['state-code'].astype('int64')
df['county-code'] = df['county-code'].astype('int64')
df['label'] = df.apply(lambda x: '{} County, {}'.format(x['county'], x['state']), axis=1)
df.head()

df_diff = df.groupby('fips')[['cases', 'deaths']].diff().fillna(0).astype('int64')
df_diff.rename(columns={'cases':'new_cases', 'deaths':'new_deaths'}, inplace=True)
df = pd.concat([df, df_diff], axis=1)

rolling_window=14

df_roll = df[['fips', 'new_cases', 'new_deaths']].groupby('fips')[['new_cases', 'new_deaths']].rolling(rolling_window).sum().fillna(0).astype('int64').reset_index(0, drop=True)

# df_roll = df_roll.rolling(rolling_window).sum().fillna(0).astype('int64').reset_index(0, drop=True)


df_roll.rename(columns={'new_cases':'roll_cases', 'new_deaths':'roll_deaths'}, inplace=True)
df = pd.concat([df, df_roll], axis=1)

df['cases_min'] = 2*df['roll_cases']
df['cases_max'] = 13*df['roll_cases']

df['population'] = df['population'].fillna(0).astype('int64')
df['cases_pcap'] = df['cases']/df['population']
df['deaths_pcap'] = df['deaths']/df['population']
df['new_cases_pcap'] = df['new_cases']/df['population']
df['new_deaths_pcap'] = df['new_deaths']/df['population']
df['roll_cases_pcap'] = df['roll_cases']/df['population']
df['roll_deaths_pcap'] = df['roll_deaths']/df['population']

df['cases_min_pcap'] = df['cases_min']/df['population']
df['cases_max_pcap'] = df['cases_max']/df['population']

# reduce down to rolling average
df_out = df[['date', 'label', 'county', 'state', 'fips', 'cases', 'deaths', 'roll_cases_pcap']]

df_out.to_csv('./data/rolling-14-day-sum.csv', index=False)

