import plotly.graph_objects as go
import plotly.io as pio
from genpeds import Admissions
import pandas as pd

THEME_LAYOUT = go.Layout(
    # FONT/TEXT
    font={
        'color': '#1e4a4a',
        'family': 'Georgia, serif'
        
    },
    title={
        'font': {
            'size': 24,
            'weight': 'bold'
        },
        'x': .2
    },
    #MAPS
    geo={
        'scope': 'usa',
        'bgcolor': '#ffffff',
        'landcolor': '#ffffff',
        'subunitcolor': '#1e4a4a'
    },
    #NON-GEO PLOTS
    plot_bgcolor='#ffffff',
    paper_bgcolor='#ffffff',
    scattermode='overlay',
    #HOVER
    # annotations= {
    #     'font': {'family': 'Georgia, serif'}
    # },
    #GENERAL
    showlegend=True
)

THEME = go.layout.Template(layout=THEME_LAYOUT)

if __name__=='__main__':
    pio.templates['THEME'] = THEME
    pio.templates.default='THEME'

    adm22 = Admissions(2022).run(merge_with_char=True,rm_disk=True)
    adm22 = adm22.dropna(subset=['act_comp_50', 'act_comp_25', 'act_comp_75', 'tot_enrolled'])
    adm22['act_avg'] = adm22.eval('(act_comp_50 + act_comp_25 + act_comp_75)/3')
    adm22 = adm22.query('act_avg > 10 and act_avg < 36')
    adm22['std_pop'] = (adm22['tot_enrolled'] - adm22['tot_enrolled'].mean()) / adm22['tot_enrolled'].std()
    adm22['std_pop'] = adm22['std_pop']

    labels = [f'{i}th perc.' if i > 2 else f'{i}st perc.' for i in range(1,11)]
    adm22['act_perc'] = pd.qcut(adm22['act_avg'], 10, labels=labels)
    adm22['text'] = ('<b>' + adm22['name'] + '</b>' +
    '<br>' + adm22['city'] + ', ' + adm22['state']  + 
    '<br>Total Enrolled: ' + adm22['tot_enrolled'].astype(int).astype(str) + 
    '<br><b>Median ACT Composite</b>: ' + adm22['act_avg'].round(2).astype(str))

    fig = go.Figure()

    greens = ["#003300",  "#004d00","#006600","#008000", "#009900",
              "#00b200","#00cc00","#00e500","#00ff00",  "#e6ffe6"]
    oranges = ["#3d1e00", "#663300", "#804000", "#995000", "#ff6600", 
               "#ff8533", "#ffad66", "#ffc299", "#ffdab3", "#ffe5cc"]

    
    for i in range(10):
        df_filtered = adm22.loc[adm22['act_perc'].astype(str) == labels[i]].copy()
        fig.add_trace(go.Scattergeo(
        locationmode= 'USA-states',
        lon=df_filtered['longitude'],
        lat=df_filtered['latitude'],
        text=df_filtered['text'],
        marker={
        'color': oranges[i],
        'line_color': 'black',
        'opacity': .75,
        'size' : df_filtered['tot_enrolled'] / 120, 
        'sizemode': 'diameter'
        },
        name=labels[i]
    ))

    fig.update_layout(
        title={'text': 'TEST', 'subtitle': {'text': 'Average ACT scores by School (2023)'}}
    )
    fig.add_annotation(text='hey there this is a figure note blah blah blah blah hey there<br>Source: <a href="https://aibm.org" style="color:#1e4a4a"><u>aibm',
                       showarrow=False,
                       x=0.15,
                       xanchor='left',
                       y=-.03)
    pio.write_json(fig, '../test.json')
    
    
    