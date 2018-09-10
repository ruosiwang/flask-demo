from flask import Flask, render_template, request, redirect
import requests
import pandas as pd

from bokeh.plotting import figure
from bokeh.embed import components

app = Flask(__name__)


price_search = ['Close', 'Open', 'Adj. Close', 'Adj. Open']

# use quandl api to get the data of a stock, and then return the pandaframe


def get_quandl_data(stock):

    # api
    api_key = 'HS-tx_Mev3qhG9vzKCik'
    api_url = 'https://www.quandl.com/api/v3/datasets/WIKI/{}.json?api_key={}'.format(stock, api_key)
    # request data
    # response = requests.get(url)
    # data = response.json()
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
    raw_data = session.get(api_url)
    data = raw_data.json()

    # create pandaframe from json data
    df = pd.DataFrame(data['dataset']['data'], columns=data['dataset']['column_names'])
    df['Date'] = pd.to_datetime(df['Date'])
    return df


def get_csv_data(stock):
    df = pd.read_csv('data/WIKI-{}.csv'.format(stock))
    df['Date'] = pd.to_datetime(df['Date'])
    return df


# create a bokeh figure
def create_figure(stock, lookup):

    # df = get_csv_data(stock)
    df = get_quandl_data(stock)

    # lookup = 'Close'

    lib = {'Close': 'Closing Prices', 'Open': 'Open Prices',
           'Adj. Close': 'Adj. Closing Prices', 'Adj. Open': 'Adj. Open Prices'}

    # figure 1: raw data
    p1 = figure(x_axis_type="datetime", title='Stock {}'.format(lib[lookup]))
    # p1 = figure(title='Stock Close Prices')
    # p1.grid.grid_line_alpha = 0.6
    p1.xaxis.axis_label = 'Date'
    p1.yaxis.axis_label = 'Price'

    p1.line(df['Date'].values, df[lookup].values, color='#A6CEE3', legend=stock)
    # p1.line(stock_data['tp'], stock_data[lookup], color='#A6CEE3', legend=stock)
    p1.legend.location = "top_left"
    return p1


app.vars = {}


@app.route('/')
def main():
    return redirect('/index')


@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html', price_search=price_search)


@app.route('/graph', methods=['POST'])
def graph():

    app.vars['ticker'] = request.form['ticker']
    app.vars['lookup'] = request.form['lookup']

    # Create the plot
    p = create_figure(app.vars['ticker'], app.vars['lookup'])

    # Embed plot into HTML via Flask Render
    script, div = components(p)
    return render_template("graph.html", script=script, div=div, price_search=price_search)


# With debug=True, Flask server will auto-reload
# when there are code changes
if __name__ == '__main__':
    app.run(port=5000, debug=True)
