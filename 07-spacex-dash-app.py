# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Prepare dropdown options for Launch Site selection
# Get all unique launch sites
launch_sites = spacex_df['Launch Site'].unique()

# Create the list of options: 'ALL' and individual sites
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
for site in launch_sites:
    dropdown_options.append({'label': site, 'value': site})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,  # Using the prepared list of options
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={i: f'{i} kg' for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# --------------------------------------------------------------------------------------
# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Calculate total success for all sites
        total_success = spacex_df[spacex_df['class'] == 1].shape[0]
        total_fail = spacex_df[spacex_df['class'] == 0].shape[0]
        
        # Data for the pie chart
        data = pd.DataFrame({
            'Launch Outcome': ['Success', 'Failure'],
            'Count': [total_success, total_fail]
        })
        
        fig = px.pie(data,
                     values='Count', 
                     names='Launch Outcome', 
                     title='Total Successful vs. Failed Launches for All Sites',
                     color_discrete_map={'Success': 'green', 'Failure': 'red'}
                     )
        return fig
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Count successful (class=1) and failed (class=0) launches for the site
        outcome_counts = filtered_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']
        outcome_counts['Outcome'] = outcome_counts['class'].apply(lambda x: 'Success' if x == 1 else 'Failure')
        
        fig = px.pie(outcome_counts,
                     values='count', 
                     names='Outcome', 
                     title=f'Success and Failure Launches for Site: {entered_site}',
                     color='Outcome',
                     color_discrete_map={'Success': 'green', 'Failure': 'red'}
                     )
        return fig

# --------------------------------------------------------------------------------------
# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    
    # Filter by payload range first
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    
    if entered_site == 'ALL':
        # Scatter chart for all sites and selected payload range
        fig = px.scatter(filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category',
                         title='Payload Mass vs. Launch Outcome for All Sites (Payload Range: {}-{} kg)'.format(low, high)
                         )
        fig.update_layout(yaxis_title='Launch Outcome (0=Failure, 1=Success)')
        return fig
    else:
        # Filter by selected site AND payload range
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
        # Scatter chart for the specific site and selected payload range
        fig = px.scatter(site_filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category',
                         title='Payload Mass vs. Launch Outcome for Site: {} (Payload Range: {}-{} kg)'.format(entered_site, low, high)
                         )
        fig.update_layout(yaxis_title='Launch Outcome (0=Failure, 1=Success)')
        return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)  # <-- Correct, modern function