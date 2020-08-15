import altair as alt
import pandas as pd
from altair import datum

fips_of_interest = [53033, 53, 0]
# fips_of_interest = [38105, 38, 0]

df = pd.read_csv('./data/rolling-14-day-sum.csv')

data = df[df['fips'].isin(fips_of_interest)]
data = 'https://raw.githubusercontent.com/micahg0/covid-risk/make-csv/data/rolling-14-day-sum.csv'
line_county = alt.Chart(data, height=250, width=250).mark_line().encode(
    x='date:T',
    y=alt.Y(
        'roll_cases_pcap:Q',
        # 'cases:Q',
        title='Positive COVID test rate within 14 days',
    ),
    tooltip='date:T',
    color=alt.Color(
        'label:N',
        title='Region',
    ),
).transform_filter(
    (datum.fips == 53033)
).interactive()


line_county.save('chart.json')
line_county.save('chart.html')
