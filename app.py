from flask import Flask, render_template, request
import requests
import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.embed import components

app = Flask(__name__)


def datetime(x):
    return np.array(x, dtype=np.datetime64)


stock_names = ['GOOG', 'AAPL', 'IBM', 'MSFT']

# use quandl api to get the data of a stock, and then return the pandaframe


def get_quandl_data(stock):
    start_date, end_date = '2016-01-01', '2018-01-01'
    # api
    url = 'https://www.quandl.com/api/v3/datasets/WIKI/{}.json?start_date={}&end_date={}'.format(stock, start_date, end_date)
    # request data
    with requests.get(url) as response:
        data = response.json()
    # create pandaframe from json data
    df = pd.DataFrame(data['dataset']['data'], columns=data['dataset']['column_names'])
    return df


def get_csv_data(stock):
    df = pd.read_csv('data/WIKI-{}.csv'.format(stock))
    df['tp'] = df.index
    return df


# create a bokeh figure
def create_figure(stock):

    stock_data = get_csv_data(stock)
    # stock_data['tp'] = stock_data.index
    lookup = 'Adj. Close'

    # lib = {'Close': 'Closing Prices', 'Open': 'Open Prices',
    #       'Adj. Close': 'Adj. Closing Prices', 'Adj. Open': 'Adj. Open Prices'}

    # figure 1: raw data
    # p1 = figure(x_axis_type="datetime", title='Stock {}'.format(lib[lookup]))
    p1 = figure(title='Stock Close Prices')
    p1.grid.grid_line_alpha = 0.3
    p1.xaxis.axis_label = 'Date'
    p1.yaxis.axis_label = 'Price'

    # p1.line(datetime(stock_data['Date']), stock_data[lookup], color='#A6CEE3', legend=stock)
    p1.line(stock_data['tp'], stock_data[lookup], color='#A6CEE3', legend=stock)
    p1.legend.location = "top_left"
    return p1

    # # figure 2: month average
    # stock_raw = np.array(stock_data[lookup])
    # stock_dates = np.array(stock_data['Date'], dtype=np.datetime64)

    # window_size = 30
    # window = np.ones(window_size) / float(window_size)
    # stock_avg = np.convolve(stock_raw, window, 'same')

    # p2 = figure(x_axis_type="datetime", title='{} One-Month Average'.format(stock))
    # p2.grid.grid_line_alpha = 0
    # p2.xaxis.axis_label = 'Date'
    # p2.yaxis.axis_label = 'Price'
    # p2.ygrid.band_fill_color = "olive"
    # p2.ygrid.band_fill_alpha = 0.1

    # p2.circle(stock_dates, stock_raw, size=4, legend='close',
    #           color='darkgrey', alpha=0.2)

    # p2.line(stock_dates, stock_avg, legend='avg', color='navy')
    # p2.legend.location = "top_left"

    # p = gridplot([[p1, p2]], plot_width=400, plot_height=400)  # open a browser


# Index page
@app.route('/')
def index():
    # Determine the selected feature
    current_stock_name = request.args.get("stock_name")
    if current_stock_name is None:
        current_stock_name = "AAPL"

    # Create the plot
    plot = create_figure(current_stock_name)

    # Embed plot into HTML via Flask Render
    script, div = components(plot)
    return render_template("stock_index.html", script=script, div=div,
                           stock_names=stock_names, current_stock_name=current_stock_name)


# With debug=True, Flask server will auto-reload
# when there are code changes
if __name__ == '__main__':
    app.run(port=5000, debug=True)
