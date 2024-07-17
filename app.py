from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px

app = Flask(__name__)

@app.route('/callback', methods=['POST', 'GET']) 
def cb():
    col = request.args.get('data')
    address = 'samples/'+col+'.csv'
    frame = pd.read_csv(address).head(23)
    fig = px.line(frame, x="timestamp", y="value")
    graphJSON = fig.to_json()
    return graphJSON


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)