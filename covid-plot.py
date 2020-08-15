import altair as alt
fips_of_interest = [53033, 53, 0]
# fips_of_interest = [38105, 38, 0]

data = df[df['fips'].isin(fips_of_interest)]

line_county = alt.Chart(height=250, width=250).mark_line().encode(
    x='date',
    y=alt.Y(
        'roll_cases_pcap',
        title='Positive COVID test rate within 14 days',
    ),
#     b='cases_pcap',
#     y2='new_cases_pcap',
    tooltip='date',
    color=alt.Color(
        'label',
        title='Region',
    ),
)
bar = alt.Chart().mark_bar(opacity=0.7).encode(
    x='date',
    y=alt.Y(
        'new_cases_pcap',
        stack=False,
    ),
    tooltip='new_cases_pcap',
    color='label'
)
test_rate = alt.layer(
    line_county,
    bar,
    data=data,
).properties(
    title=''
).facet(
    'label'
).interactive()

test_rate.save('chart.html')