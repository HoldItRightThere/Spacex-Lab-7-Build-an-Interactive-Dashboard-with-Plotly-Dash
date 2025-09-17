# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),
    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=10000,  # Upper limit set to 10000
        step=1000,
        marks={
            0: '0',
            2500: '2500',
            5000: '5000',
            7500: '7500',
            10000: '10000'
        },
        value=[min_payload, max_payload if max_payload <= 10000 else 10000]
    ),
    html.Br(),
    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Filter for successful launches (class=1)
        success_df = spacex_df[spacex_df['class'] == 1]
        # Group by Launch Site and count successful launches
        site_counts = success_df['Launch Site'].value_counts().reset_index()
        site_counts.columns = ['Launch Site', 'Count']
        # Check if there are any successful launches
        if site_counts.empty:
            fig = {
                'data': [],
                'layout': {
                    'title': 'No Successful Launches Available',
                    'annotations': [{'text': 'No data', 'showarrow': False}]
                }
            }
        else:
            fig = px.pie(
                site_counts,
                names='Launch Site',
                values='Count',
                title='Total Success Launches by Site',
                labels={'Launch Site': 'Launch Site', 'Count': 'Successful Launches'}
            )
    else:
        # Filter data for the selected launch site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(
            filtered_df,
            names='class',
            title=f'Success vs. Failed Launches for {selected_site}',
            labels={'class': 'Launch Outcome', '0': 'Failed', '1': 'Success'}
        )
    return fig

# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'), Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    min_payload, max_payload = payload_range
    if selected_site == 'ALL':
        # Filter data by payload range
        filtered_df = spacex_df[
            (spacex_df['Payload Mass (kg)'] >= min_payload) &
            (spacex_df['Payload Mass (kg)'] <= max_payload)
        ]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation Between Payload and Success for All Sites',  # Updated title
            labels={'class': 'class'}  # Updated y-axis label
        )
    else:
        # Filter data by selected site and payload range
        filtered_df = spacex_df[
            (spacex_df['Launch Site'] == selected_site) &
            (spacex_df['Payload Mass (kg)'] >= min_payload) &
            (spacex_df['Payload Mass (kg)'] <= max_payload)
        ]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation Between Payload and Success for {selected_site}',  # Updated title
            labels={'class': 'class'}  # Updated y-axis label
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
