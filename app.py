from flask import Flask, render_template, request
import pandas as pd
import datetime, random
from datetime import timedelta
import plotly.express as px

start_date = datetime.datetime.now()
end_date = start_date + timedelta(days=10)
df_temp = pd.read_csv('samples/temp.csv').head(50)
df_air=pd.read_csv('samples/air_humidity.csv').head(50)
df_lum=pd.read_csv('samples/luminance.csv').head(50)
random_date = start_date + (end_date - start_date) * random.random()
app = Flask(__name__)

def data(col):
    if(col=='temp'):
        return df_temp
    elif(col=='air_humidity'):
        return df_air
    elif(col=='soil_humidity'):
        return df_temp
    elif(col=='luminance'):
        return df_lum
    elif(col=='water'):
        return df_temp
    elif(col=='light'):
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