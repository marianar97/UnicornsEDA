from dash import Input, Output, html, dash, dcc
import pandas as pd
import plotly.graph_objects as go

UNICORN_LOGO = 'assets/images/unicorn.png'


app = dash.Dash(
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ]
    )
app.title = 'Unicorn Dataset Analysis'
app._favicon = 'images/unicorn.png'


# data manipulation
df = pd.read_csv('unicorn.csv')

# group by country and industry
dfs = []
for column in ['country', 'industry']:
    dfs.append(df.groupby(column).sum().sort_values(by='valuation_in_billions', ascending=False))


# nav-bar dropdowns
countries = ['All countries' ] + sorted(df.country.unique()) 
industries = ['All industries'] + sorted(df.industry.unique())
dropdown_country = dcc.Dropdown(
                        id='dropdown-country',
                        options=[
                            {'label': country, 'value': country}
                            for country in countries],  
                        value='All countries',
                        multi=True,
                    )

dropdown_industry = dcc.Dropdown(
                        id='dropdown-industry',
                        options=[
                            {'label': industry, 'value': industry}
                            for industry in industries],
                        value='All industries',
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


# charts

# valuation by country chart
country_valuation_chart = html.Div(
    [ 
        dcc.Graph(
            id='valuation-by-country',
        )
    ], className='valuation-by-country'
)

# valuation by industry chart
industry_valuation_chart = html.Div(
    [ 
        dcc.Graph(
            id='valuation-by-industry'
        )
    ],className='valuation-by-industry'
)

# Companies valuation table
df_companies_valuations = df[['company', 'valuation_in_billions']]
companies_table = html.Div(
        dash.dash_table.DataTable(
            id='table-companies',
            columns=[
                    {'name': 'Company', 'id': 'company', 'type':'text'},
                    {'name': 'Valuation ($B)', 'id': 'valuation_in_billions', 'type':'numeric'}
            ],
            style_cell={
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0
            },
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white',
                'fontWeight': 'bold',
            },
            style_data={
                'backgroundColor': '#272a31',
                'color': 'white',
            },
            style_data_conditional=(
                data_bars(df, 'valuation_in_billions') 
            ),
           css=[{
                'selector': '.dash-table-tooltip',
                'rule': 'background-color: white; color: black; position: absolute; white-space=pre'
            }],
            tooltip_duration=None
        ), className='companies-table',
     
)

navbar = html.Div(
    [   
        html.A(
            html.Div(
                html.Div(
                    [
                        html.Img(src=UNICORN_LOGO, alt="logo", className="logo"),
                        html.H1("", className='navbar__title')
                    ], className='navbar__title-container'
                ), className='bigger-container'
            ),
            href="https://www.kaggle.com/code/marami21/unicorns-eda"
        ),
        html.Div(
            [
                dropdown_industry,
                dropdown_country
            ],
            className='dropdowns'
        )
    ],
    className='navbar'
)

# app layout
app.layout = html.Div(
    [
        navbar,
        country_valuation_chart,
        industry_valuation_chart,
        companies_table,
    ], className='container'
)

#callbacks 

@app.callback(
    Output('valuation-by-country', 'figure'),
    [
        Input('dropdown-country', 'value'),
        Input('dropdown-industry', 'value'),
        Input('table-companies', 'active_cell'),
        Input('table-companies', 'data')
    ]
)
def update_country_valuation(selected_countries, selected_industry, active_cell, data):
    company_df = df

    if active_cell and active_cell['column_id']=='company':
        col = active_cell['column_id']
        row = active_cell['row']
        cellData = data[row][col]
        company_df = company_df[company_df['company'] == cellData]

    industry_df = company_df

    if selected_industry != 'All industries':
        industry_df = df[df['industry']==selected_industry]

    country_df = industry_df

    if type(selected_countries) == list:
        if len(selected_countries) > 1 and 'All countries' in selected_countries:
            selected_countries.remove('All countries')
            country_df = country_df.loc[country_df['country'].isin(selected_countries)]
        elif 'All countries' not in selected_countries:
            country_df = country_df.loc[country_df['country'].isin(selected_countries)]
    
    df_country_valuation = country_df.groupby('country').sum().sort_values(by='valuation_in_billions', ascending=False)
    df_country_count = country_df.groupby('country').count()
    df_country_count = df_country_count.reindex(df_country_valuation.index)
   
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_country_valuation.index,
            y=df_country_valuation.valuation_in_billions,
            hovertemplate=
                 f'<b>Country: </b>%{{x}}</br>' +
                 f'<b>Valuation: </b>%{{y}} billions </br>' +
                 f'<br> <extra></extra>', 
            name='valuation',
            marker={'color': '#2177b4'}
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_country_count.index,
            y=df_country_count.valuation_in_billions,
            hovertemplate=
                 f'<b>Country: </b>%{{x}}</br>' +
                 f"<b>Count: </b>%{{y}} unicorns <br> <extra></extra>",
            name='count',
        )
    )


    fig.update_layout(
        title={
            'text': 'Valuation ($B) by country',
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis=dict(title = 'Valuation ($B)'), # y-axis label
        hovermode='closest', # handles multiple points landing on the same vertical,
        plot_bgcolor='#272a31',
        paper_bgcolor='#272a31',
        font=dict(
            color="white",
            # size=18,
        ),
        autosize=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.99,
        ),
        # showlegend=False,
        hoverlabel=dict(
            bgcolor="white",
            # font_size=18
        )

    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
                
    return fig

@app.callback(
    Output('valuation-by-industry', 'figure'),
    [
        Input('dropdown-country','value'),
        Input('dropdown-industry','value'),
        Input('table-companies', 'active_cell'),
        Input('table-companies', 'data')
    ]
)
def update_industry_valuation(selected_countries, selected_industry, active_cell, data):

    company_df = df

    if active_cell and active_cell['column_id']=='company':
        col = active_cell['column_id']
        row = active_cell['row']
        cellData = data[row][col]
        company_df = company_df[company_df['company'] == cellData]

    industry_df = company_df
    if selected_industry != 'All industries':
        industry_df = df[df['industry']==selected_industry]

    country_df = industry_df

    if type(selected_countries) == list:
        if len(selected_countries) > 1 and 'All countries' in selected_countries:
            selected_countries.remove('All countries')
            country_df = country_df.loc[country_df['country'].isin(selected_countries)]
        elif 'All countries' not in selected_countries:
            country_df = country_df.loc[country_df['country'].isin(selected_countries)]

    df_industry_valuation = country_df.groupby('industry').sum().sort_values(by='valuation_in_billions', ascending=False)
    df_industry_count = country_df.groupby('industry').count()
    df_industry_count = df_industry_count.reindex(df_industry_valuation.index)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_industry_valuation.index,
            y=df_industry_valuation.valuation_in_billions,
            hovertemplate=
                f'<b>Industry: </b>%{{x}}</br>' +
                 f'<b>Valuation: </b>%{{y}} billions </br>' +
                 f'<br> <extra></extra>', 
            name='valuation',
            marker = {'color' : '#2177b4'}
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_industry_count.index,
            y=df_industry_count.valuation_in_billions,
            hovertemplate=
                 f'<b>Industry: </b>%{{x}}</br>' +
                 f"<b>Count: </b>%{{y}} unicorns <br> <extra></extra>",
            name='count',
        )
    )


    fig.update_layout(
        title={
            'text': 'Valuation ($B) by industry',
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis=dict(title = 'Valuation ($B)'), # y-axis label
        hovermode='closest', # handles multiple points landing on the same vertical,
        plot_bgcolor='#272a31',
        paper_bgcolor='#272a31',
        font=dict(
            color="white",
        ),
        autosize=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.99,
        ),
        hoverlabel=dict(
            bgcolor="white",
        )

    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig


@app.callback(
    Output('table-companies', 'data'),
    Output('table-companies', 'tooltip_data'),
    [   
        Input('dropdown-country','value'),
        Input('dropdown-industry','value'),
    ]
)
def update_table(selected_countries, industry):
    df_companies_valuations = df

    if industry != 'All industries':
        df_companies_valuations = df_companies_valuations[df_companies_valuations['industry']==industry]

    country_df = df_companies_valuations

    if type(selected_countries) == list:
        if len(selected_countries) > 1 and 'All countries' in selected_countries:
            selected_countries.remove('All countries')
            country_df = country_df.loc[country_df['country'].isin(selected_countries)]
        elif 'All countries' not in selected_countries:
            country_df = country_df.loc[country_df['country'].isin(selected_countries)]

    df_table = country_df[['company','valuation_in_billions']]

    tooltip_data=[]    
    for row in country_df.to_dict('records'):
        founded_year = row['founded_year']
        try:
            founded_year = int(founded_year)
        except ValueError:
            pass
        tooltip_data.append(
            {
                'company': {
                    'value': '**Company:** {}\n\n**Country**: {}\n\n**City**: {}\n\n**Valuation**: {}B\n\n**Date Joined**: {}\n\n**Founded year**: {}\n\n'.format(row['company'], row['country'], row['city'], row['valuation_in_billions'],row['date_joined'], founded_year),
                    'type': 'markdown'
                }
            }
        )

    return df_table.to_dict('records'), tooltip_data



if __name__ == '__main__':
    app.run_server(debug=True)
