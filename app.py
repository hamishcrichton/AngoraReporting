import pandas as pd
from dash import Dash, dcc, html, dash_table, Input, Output, callback
import plotly.graph_objs as go
from datetime import datetime, date
import dash.exceptions

from MTORFIDList import basic_reporting_query
from Transformation import transform_date_columns
from Cutting import manipulate_cutting

# Function to create multi-line strings
def to_multi_line(value):
    if isinstance(value, str) and ',' in value:
        return '\n'.join(value.split(', '))
    return value

app = Dash(__name__)

def load_and_transform_data():
    # Load and transform the dataset
    df = basic_reporting_query()
    df = transform_date_columns(df)
    uncut, progress_in_day, readiness = manipulate_cutting(df)
    return uncut, progress_in_day, readiness

def prepare_bar_chart(progress_in_day, readiness):
    # Preparing data for the bar chart
    true_count = progress_in_day["Sales_Order_No"].loc[progress_in_day['Complete']].values[0]
    false_count = progress_in_day["Sales_Order_No"].loc[~progress_in_day['Complete']].values[0]
    total_count = true_count + false_count
    true_percentage = (true_count / total_count) * 100
    false_percentage = (false_count / total_count) * 100

    # Prepare the graph data
    data = [
        go.Bar(
            x=[true_count],
            y=['Total Orders'],
            name='Cut',
            text=f'{true_percentage:.0f}%',
            hoverinfo='x+text',
            orientation='h',
            marker=dict(color='green')
        ),
        go.Bar(
            x=[false_count],
            y=['Total Orders'],
            name='Not Cut',
            text=f'{false_percentage:.0f}%',
            hoverinfo='x+text',
            orientation='h',
            marker=dict(color='red')
        )
    ]
    layout = go.Layout(
        barmode='stack',
        xaxis=dict(title=''),
        yaxis=dict(title='', showticklabels=False),
        height=300,
    )
    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        bargap=0.15
    )
    return fig

def prepare_data_table(uncut):
    # Preparing the data table with the updated data frame 'uncut'
    table = dash_table.DataTable(
        id='table',
        columns=[{"name": col, "id": col} for col in uncut.columns],
        data=uncut.to_dict('records'),
        style_data={
            'whiteSpace': 'pre-line',
            'verticalAlign': 'top',
            'textAlign': 'left',
        }
    )
    return table

# Interval component for refreshing the data every 5 minutes (300000 milliseconds)
app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=30000,  # in milliseconds
        n_intervals=0
    ),
    html.Div(id='content-update')
])


@app.callback(
    Output('content-update', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_layout(n):
    try:
        uncut, progress_in_day, readiness = load_and_transform_data()

        # Prepare the updated bar chart figure
        fig = prepare_bar_chart(progress_in_day, readiness)

        # Prepare the updated data table component
        table_component = prepare_data_table(uncut)

        # Prepare text content
        now = datetime.now()
        today = date.today()
        true_count = progress_in_day["Sales_Order_No"].loc[progress_in_day['Complete']].values[0]
        false_count = progress_in_day["Sales_Order_No"].loc[~progress_in_day['Complete']].values[0]
        ready_order_count = readiness["Sales_Order_No"].loc[readiness['ReadyForCut']].values[0]
        not_ready_order_count = readiness["Sales_Order_No"].loc[~readiness['ReadyForCut']].values[0]
        text_elements = html.Div([
            html.H1("Cutting Progress"),
            html.P(f"Cut progress {today.strftime('%d %B')}: last updated {now.strftime('%H:%M')}."),
            html.P(f"Today's plan: {ready_order_count} orders ready for cutting. {not_ready_order_count} not yet ready for cutting."),
            html.P(f"{true_count} Orders Complete Cut. {false_count} Orders Not Yet Complete Cut.")
        ])

        graph_element = dcc.Graph(figure=fig)

        return html.Div([
            text_elements,
            graph_element,
            table_component
        ])

    except Exception as e:
        return html.Div(str(e))

if __name__ == "__main__":
    app.run_server(debug=True)