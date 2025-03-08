from dash import html

selected = {
    'ZFH5': 42072515,
    'ZNH5': 42002219,
    'ZTH5': 42111442,
    'SR1H5': 42177485,
    'SR3H5': 254257
}

name_map = {
    'ZFH5': '5Y T-Note Future',
    'ZNH5': '10Y T-Note Future',
    'ZTH5': '2Y T-Note Future',
    'SR1H5': '1M SOFR Future',
    'SR3H5': '3M SOFR Future',
    # 'ERROR': ''
}

resample_frequency = ['30 seconds', '1 minute', '5 minutes', '30 minutes']

inv_name_map = {v: k for k, v in name_map.items()}

tab2_doc = html.P(['This example shows a data pipeline',
                   html.Br(),
                   '# Top of book market data downloaded from Databento. The data collects order book actions at nanosecond resolution.',
                   html.Br(),
                   html.A("Databento schema", href='https://databento.com/docs/schemas-and-data-formats/mbp-1', target="_blank"),
                   html.Br(),
                   '# The products are T-notes futures and SOFR futures, just for Feb 25th, 2025.',
                   html.Br(),
                   '# The data is stored in an AWS S3 bucket. It is then ingested into a Databricks Delta Lake table.',
                   html.Br(),
                   '# A workbook in Databricks uses PySpark to load, filter and resample the data. It then creates a plotly figure.',
                   html.Br(),
                   '# This Dash app loads the figure from the Databricks cluster and displays it in the browser.',
                   html.Br(),
                   '--- N.B. it takes approx 90 seconds to update the figure ---'
                   ])


tab1_doc = html.P(['This example shows a marking GUI',
                   html.Br(),
                   '# A very simple GUI that uses AG Grid and Plotly Dash to create an interactive table and plot.',
                   html.Br(),
                   '# The Zero Rate column can be edited and the resulting curve is plotted.',
                   html.Br(),
                   '# The interpolation is just a naive cubic spline, there are no controls for no-arbitrage or invalid inputs.',
                   ])