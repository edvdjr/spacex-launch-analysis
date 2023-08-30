# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

sites = ['ALL']
sites.extend(list(spacex_df['Launch Site'].unique()))
labels = sites.copy()
labels[0] = 'All sites'

dropdown_options = [{'label': label, 'value': site} for label, site in zip(labels, sites)]

content = [
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center',
                   'color': '#503D36',
                   'font-size': 40}),
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    # dcc.Dropdown(id='site-dropdown',...)
    html.Br(),

    html.Div([dcc.Dropdown( id='site-dropdown',
                            options=dropdown_options,
                            value='ALL',
                            placeholder='Select a Launch Site here',
                            searchable=True)
            ]
    ),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    #dcc.RangeSlider(id='payload-slider',...)
    html.Div(dcc.RangeSlider(id='payload-slider',
                             min=0,
                             max=10000,
                             step=1000,
                             marks={0: '0',
                                    2500: '2500',
                                    5000: '5000',
                                    7500: '7500',
                                    10000: '10000'},
                             value=[0, 10000])),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=content)

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback( Output(component_id='success-pie-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    filtered_df = spacex_df[['Launch Site', 'class']].groupby(['Launch Site']).value_counts().reset_index()
    filtered_df = filtered_df.rename(columns={'count': 'results'})
    
    if entered_site == 'ALL':
        fig = px.pie(filtered_df[filtered_df['class'] == 1][['Launch Site', 'results']],
                    values='results',
                    names='Launch Site',
                    title='Total Sucess Launches By Site')
        return fig
    fig = px.pie(filtered_df[filtered_df['Launch Site'] == entered_site][['class', 'results']],
                values='results', 
                names='class', 
                title='Total Sucess Launches For Site ' + entered_site)
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback( Output(component_id='success-payload-scatter-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value'))

def get_scatter_chart(entered_site, payload_val):
    filtered_df = spacex_df[['Launch Site', 'Booster Version', 'Payload Mass (kg)', 'class']]
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_val[0]) &
                              (filtered_df['Payload Mass (kg)'] <= payload_val[1])]
    filtered_df.loc[filtered_df['Booster Version'].str.startswith('F9 v1.1'), 'Booster Version'] = 'v1.1'
    filtered_df.loc[filtered_df['Booster Version'].str.startswith('F9 v1.0'), 'Booster Version'] = 'v1.0'
    filtered_df.loc[filtered_df['Booster Version'].str.startswith('F9 B4'), 'Booster Version'] = 'B4'
    filtered_df.loc[filtered_df['Booster Version'].str.startswith('F9 B5'), 'Booster Version'] = 'B5'
    filtered_df.loc[filtered_df['Booster Version'].str.startswith('F9 FT'), 'Booster Version'] = 'FT'

    if entered_site == 'ALL':
        fig = px.scatter(filtered_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color="Booster Version",
                         title='Correlation Between Payload and Success For All Sites')
        return fig
    fig = px.scatter(filtered_df[filtered_df['Launch Site'] == entered_site],
                     x='Payload Mass (kg)',
                     y='class',
                     color="Booster Version",
                     title='Total Sucess Launches For Site ' + entered_site)
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
