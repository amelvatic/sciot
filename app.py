from flask import Flask, render_template, request
import pandas as pd
import datetime, random
from datetime import timedelta
import plotly.express as px

start_date = datetime.datetime.now()
end_date = start_date + timedelta(days=10)
df_temp = pd.read_csv('samples/temp.csv')
random_date = start_date + (end_date - start_date) * random.random()
app = Flask(__name__)

def data(col):
    if(col=='temp'):
        return df_temp
    if(col=='air_humidity'):
        return df_temp
    if(col=='soil_humidity'):
        return df_temp
    if(col=='luminance'):
        return df_temp
    if(col=='water'):
        return df_temp
    if(col=='light'):
        return df_temp      

@app.route('/callback', methods=['POST', 'GET']) 
def cb():
    col = request.args.get('data')
    frame = data(col)
    fig = px.line(frame, x="timestamp", y="value")
    graphJSON = fig.to_json()
    return graphJSON


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)