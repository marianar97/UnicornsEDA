
from pydoc import classname
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dash, dcc
from dash_bootstrap_components._components.Container import Container
import pandas as pd
import numpy as np
import plotly.graph_objects as go

PLOTLY_LOGO = "https://storage.googleapis.com/kaggle-datasets-images/1980436/3269422/4182c369dc3d66b18fb2c9c6c99096a0/dataset-cover.png?t=2022-03-08-10-33-09"
PLOTLY_LOGO = 'assets/images/unicorn.png'


app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ]
    )
app.title = 'Unicorn Dataset Analysis'

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


def data_bars(df, column):
    n_bins = 100
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    ranges = [
        ((df[column].max() - df[column].min()) * i) + df[column].min()
        for i in bounds
    ]
    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        max_bound_percentage = bounds[i] * 100
        styles.append({
            'if': {
                'filter_query': (
                    '{{{column}}} >= {min_bound}' +
                    (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                'column_id': column
            },
            'background': (
                """
                    linear-gradient(90deg,
                    #0074D9 0%,
                    #0074D9 {max_bound_percentage}%,
                    #272a31 {max_bound_percentage}%,
                    #272a31 100%)
                """.format(max_bound_percentage=max_bound_percentage)
            ),
            'paddingBottom': 2,
            'paddingTop': 2
        })

    return styles

def data_bars_diverging(df, column, color_above='#3D9970', color_below='#FF4136'):
    n_bins = 100
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    col_max = df[column].max()
    col_min = df[column].min()
    ranges = [
        ((col_max - col_min) * i) + col_min
        for i in bounds
    ]
    midpoint = (col_max + col_min) / 2.

    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        min_bound_percentage = bounds[i - 1] * 100
        max_bound_percentage = bounds[i] * 100

        style = {
            'if': {
                'filter_query': (
                    '{{{column}}} >= {min_bound}' +
                    (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                'column_id': column
            },
            'paddingBottom': 2,
            'paddingTop': 2
        }
        if max_bound > midpoint:
            background = (
                """
                    linear-gradient(90deg,
                    white 0%,
                    white 50%,
                    {color_above} 50%,
                    {color_above} {max_bound_percentage}%,
                    white {max_bound_percentage}%,
                    white 100%)
                """.format(
                    max_bound_percentage=max_bound_percentage,
                    color_above=color_above
                )
            )
        else:
            background = (
                """
                    linear-gradient(90deg,
                    white 0%,
                    white {min_bound_percentage}%,
                    {color_below} {min_bound_percentage}%,
                    {color_below} 50%,
                    white 50%,
                    white 100%)
                """.format(
                    min_bound_percentage=min_bound_percentage,
                    color_below=color_below
                )
            )
        style['background'] = background
        styles.append(style)

    return styles

#charts

# valuation by country chart
country_valuation_chart = html.Div(
    [ 
        dcc.Graph(
            id='valuation-by-country'
        )
    ],className='chart'
)

# valuation by industry chart
industry_valuation_chart = html.Div(
    [ 
        dcc.Graph(
            id='valuation-by-industry'
        )
    ], className='chart'
    
)

df_companies_valuations = df[['company','valuation_in_billions']]
companies_table = dash.dash_table.DataTable(
        data=df_companies_valuations.to_dict('records'),
        #columns=[{"name": i.replace("_", " ").capitalize(), "id": i} for i in df_companies_valuations.columns],
        columns = [
                {'name': 'Company', 'id': 'company', 'type':'text'},
                {'name': 'Valuation ($B)', 'id': 'valuation_in_billions', 'type':'numeric'}
        ],
        #page_action='none',
        # fixed_rows={'headers': True},
        style_cell={
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': 0,
            'textAlign': 'center',    
        },
        style_cell_conditional=[
            {
                'if': {'column_id': 'valuation_in_billions'},
                'textAlign': 'right'
            },
        ],
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white',
            'fontWeight': 'bold',
        },
        style_data={
            'backgroundColor': '#272a31',
            'color': 'white'
        },
        style_table={
                'maxHeight': '900px',
                'height': '1000px%',
                'overflowY': 'scroll',
                'width': '100%',
                'minWidth': '100%',
                'marginTop': '20px'
        },
        style_data_conditional=(
            data_bars(df, 'valuation_in_billions') 
        ),
        
    )
columns=[{"name": i.replace("_", " ").capitalize(), "id": i} for i in df_companies_valuations.columns],
print(columns)
print(type(df.valuation_in_billions.values))



style_table={
                'maxHeight': '50ex',
                'overflowY': 'scroll',
                'width': '100%',
                'minWidth': '100%',
            },

# app layout
app.layout = html.Div(
    [
        navbar,
        html.Div(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            country_valuation_chart,
                            industry_valuation_chart  
                        ], xs=12, md=9,
                    ),
                    dbc.Col(
                        [
                            companies_table
                        ], xs=12, md=3, 
                        className='companies-table'
                    )
                ], className='h-100'
            ),
            style = {'height': '100%'}
        )
    ], style = {'height': '100%'}
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
                hovermode ='closest', # handles multiple points landing on the same vertical,
                plot_bgcolor = '#272a31',
                paper_bgcolor = '#272a31',
                font=dict(
                    color="white"
                )
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
            x=df_industry_valuation.index,
            y=df_industry_valuation.valuation_in_billions,
            hovertemplate=
                f'<b>Industry: </b>%{{x}}</br>' +
                f'<b>Valuation: </b>%{{y}} billions </br>' +
                f'<br> <extra></extra>', 
            name="Valuation"
        )
    layout = go.Layout(
                title = 'Valuation ($B) by industry', # Graph title
                yaxis = dict(title = 'Valuation ($B)'), # y-axis label
                hovermode ='closest', # handles multiple points landing on the same vertical,
                plot_bgcolor = '#272a31',
                paper_bgcolor = '#272a31',
                font=dict(
                    color="white"
                )
            )

    return {'data': [bar], 'layout': layout}

if __name__ == '__main__':
    app.run_server(debug=True)
