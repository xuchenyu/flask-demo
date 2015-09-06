import requests, os
from flask import Flask, render_template, request, redirect
from pandas import *
from bokeh.plotting import figure, show, output_file, output_notebook
from bokeh.embed import components
from bokeh.resources import CDN

app = Flask(__name__)

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/graph', methods=['POST'])
def show_graph():
    form_data = request.form
    if not form_data.get('ticker', False):
        return redirect('/index')
    ticker = form_data['ticker'].upper()
    
    close = form_data.get('close', False)
    adj_close = form_data.get('adj_close', False)
    volume = form_data.get('volume', False)
    if not (close or adj_close or volume):
        return redirect('/index')

    rawdata = requests.get('https://www.quandl.com/api/v3/datasets/WIKI/%s.json?order=asc' % ticker).json()['dataset']
    df = DataFrame(rawdata['data'], columns=rawdata['column_names'])
    def convert_date(raw_date):
        y, m, d = raw_date.split('-')
        return datetime(int(y), int(m), int(d))
    df['Date'] = df['Date'].map(convert_date)
    
    output_file('templates/bokeh_plot.html', title='Stock Data')
    TOOLS = 'pan, box_zoom, wheel_zoom, reset, save'
    p = figure(x_axis_type='datetime', x_axis_label = 'Date', y_axis_label = 'Stock Data', tools=TOOLS, toolbar_location='above')
    if close:
        p.line(df['Date'], df['Close'], color='#1F78B4', legend='Close')
    if adj_close:
        p.line(df['Date'], df['Adj. Close'], color='#33A02C', legend='Adj. Close')
    if volume:
        p.line(df['Date'], df['Volume'], color='#FB9A99', legend='Volume')
    p.legend.orientation = 'top_left'
    
    script, div = components(p, CDN)

    return render_template('graph.html', ticker=ticker, script=script, div=div)
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
  
