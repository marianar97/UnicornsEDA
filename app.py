
from pydoc import classname
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dash, dcc
from dash_bootstrap_components._components.Container import Container
import pandas as pd
import numpy as np
import plotly.graph_objects as go

PLOTLY_LOGO = "https://storage.googleapis.com/kaggle-datasets-images/1980436/3269422/4182c369dc3d66b18fb2c9c6c99096a0/dataset-cover.png?t=2022-03-08-10-33-09"

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# data manipulation
df = pd.read_csv('/home/mariana.ramirez/Documents/study/DashPotly/unicorn_eda/unicorn.csv')

#group by country and industry
dfs = []
for column in ['country', 'industry']:
     dfs.append(df.groupby(column).sum().sort_values(by='valuation_in_billions', ascending=False))


# nav-bar dropdowns
countries = ['All countries' ] + sorted(df.country.unique()) 
industries =  ['All industries'] + sorted(df.industry.unique(), key=len)
dropdown_country = dcc.Dropdown(
                        id='dropdown-country',
                        options=
                        [{'label': country, 'value': country} for country in countries],  
                        value='All countries',
                        multi=True
                    )

dropdown_industry = dcc.Dropdown(
                        id='dropdown-industry',
                        options=
                            [{'label': industry, 'value': industry} for industry in industries],
                        value='All industries'
                    )
dropdowns = dbc.Row(
    [
        dbc.Col(dropdown_country, className='p-2', xs=12, md=6),
        dbc.Col(dropdown_industry, className='p-2', xs=12, md=6),   
    ],
    className="g-0 ms-auto mt-3 mt-md-0 nav-header__row",
    align="center",
)

# nav-bar logo
logo =  html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="40px"), className='logo__image'),
                    dbc.Col(dbc.NavbarBrand("", className="nav-header__title ms-2")),
                ],
                align="center",
                className="g-0",
            ),
            href="https://plotly.com",
            style={"textDecoration": "none"},
        )
navbar = dbc.Navbar(
    dbc.Container(
        [
            logo,
            dropdowns,  
        ], fluid=True
    ),
    color="dark",
    dark=True,
    class_name='nav-header'
)


# valuation by country chart
country_valuation_chart = html.Div(
    [ 
       dbc.Row(
           dbc.Col(
                dcc.Graph(
                    id='valuation-by-country'
                )
           )
        )
    ],
     className='chart'
)

# valuation by industry chart
industry_valuation_chart = html.Div(
    [ 
       dbc.Row(
           dbc.Col(
                dcc.Graph(
                    id='valuation-by-industry'
                )
           )
        )
    ], className='chart'
)

# app layout
app.layout = html.Div(
    [
        navbar,
        country_valuation_chart,
        industry_valuation_chart  

    ]
)

#callbacks 

@app.callback(
    Output('valuation-by-country', 'figure'),
    [
        Input('dropdown-country','value'),
        Input('dropdown-industry','value')
    ]
)
def update_country_valuation(selected_countries, selected_industry):
    industry_df = df 

    if selected_industry != 'All industries':
        industry_df = df[df['industry']==selected_industry]

    country_df = industry_df

    if type(selected_countries) == list:
        print("its a list")
        if len(selected_countries) > 1 and 'All countries' in selected_countries:
            selected_countries.remove('All countries')
            country_df = country_df.loc[country_df['country'].isin(selected_countries)]
        elif 'All countries' not in selected_countries:
            country_df = country_df.loc[country_df['country'].isin(selected_countries)]
    
    df_country_valuation = country_df.groupby('country').sum().sort_values(by='valuation_in_billions', ascending=False)
    
   
    bar = go.Bar(
            x=df_country_valuation.index,
            y=df_country_valuation.valuation_in_billions,
            hovertemplate=
                f'<b>Country: </b>%{{x}}</br>' +
                f'<b>Valuation: </b>%{{y}} billions </br>' +
                f'<br> <extra></extra>', 
            name="Valuation"
        )
    layout = go.Layout(
                title = 'Valuation ($B) by country', # Graph title
                xaxis = dict(title = 'Country'), # x-axis label
                yaxis = dict(title = 'Valuation ($B)'), # y-axis label
                hovermode ='closest' # handles multiple points landing on the same vertical
            )

    return {'data': [bar], 'layout': layout}

@app.callback(
    Output('valuation-by-industry', 'figure'),
    [
        Input('dropdown-country','value'),
        Input('dropdown-industry','value')
    ]
)
def update_industry_valuation(selected_countries, selected_industry):
    industry_df = df 

    if selected_industry != 'All industries':
        industry_df = df[df['industry']==selected_industry]

    country_df = industry_df

    if type(selected_countries) == list:
        print("its a list")
        if len(selected_countries) > 1 and 'All countries' in selected_countries:
            selected_countries.remove('All countries')
            country_df = country_df.loc[country_df['country'].isin(selected_countries)]
        elif 'All countries' not in selected_countries:
            country_df = country_df.loc[country_df['country'].isin(selected_countries)]
    
    df_industry_valuation = country_df.groupby('industry').sum().sort_values(by='valuation_in_billions', ascending=False)
    
    bar = go.Bar(
            x=[industry[0:15] for  industry in df_industry_valuation.index],
            y=df_industry_valuation.valuation_in_billions,
            hovertemplate=
                f'<b>Country: </b>%{{x}}</br>' +
                f'<b>Valuation: </b>%{{y}} billions </br>' +
                f'<br> <extra></extra>', 
            name="Valuation"
        )
    layout = go.Layout(
                title = 'Valuation ($B) by country', # Graph title
                xaxis = dict(title = 'Country'), # x-axis label
                yaxis = dict(title = 'Valuation ($B)'), # y-axis label
                hovermode ='closest' # handles multiple points landing on the same vertical
            )

    return {'data': [bar], 'layout': layout}

if __name__ == '__main__':
    app.run_server(debug=True)
