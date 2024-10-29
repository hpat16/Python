import pandas as pd
import flask
from flask import Flask, request, jsonify
import time
import re
import matplotlib.pyplot as plt
import io

app = Flask(__name__)
# I found the data at: 'https://vincentarelbundock.github.io/Rdatasets/datasets.html'. It contains numerous datasets, and I chose one that I thought would be ideal for this project
df = pd.read_csv("main.csv")
num_subscribed = 0
home_visits = 0
# dictionary of ips assocaited with the last time it visited browse.json
remote_ips = dict()
# keeps track of count for A/B testing
A = 0
B = 0

@app.route('/')
def home():
    global home_visits
    home_visits += 1
    with open("index.html") as f:
        html = f.read()
    # for the first ten visit an even number of visit corresponds to regular color link, while odd corressponds to tomato colored link
    if home_visits <= 10:
        if home_visits % 2 == 1:
            html = html.replace("blue", "Tomato")
            html = html.replace("from=A", "from=B")
    # after the first ten visits, go with the one with the best Click Through Rate
    else:
        if B/5 > A/5:
            html = html.replace("blue", "Tomato")
            html = html.replace("from=A", "from=B")

    return html

@app.route('/browse.html')
def browse_html():
    return flask.Response("<html><h1>{}</h1><html>".format("Browse") + df.to_html())

@app.route('/browse.json')
def browse_json():
    global remote_ips
    
    if (flask.request.remote_addr not in list(remote_ips)) or (time.time() - remote_ips[flask.request.remote_addr] > 60):
        remote_ips[flask.request.remote_addr] = time.time()
        return jsonify(df.to_dict())
    else:
        return flask.Response("<b>Revist in 60 seconds</b>", status=429, headers={"Retry-After": "60"})

@app.route('/visitors.json')
def vistors_json():
    global remote_ips
    return list(remote_ips)

@app.route('/donate.html')
def donate():
    global A
    global B
    # record the type that was the source of donation for the first 10 visits
    if home_visits <= 10 and len(flask.request.args) > 0:
        if 'A' == flask.request.args['from']:
            A += 1
        else:
            B += 1
    return flask.Response("<html><h1>{}</h1><html>".format("You saved a child!"))

@app.route('/email', methods=["POST"])
def email():
    global num_subscribed
    email = str(request.data, "utf-8")
    if len(re.findall(r"^\w+@\w+\.com", email)) > 0: # 1
        num_subscribed += 1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + '\n') # 2
        return jsonify(f"thanks, your subscriber number is {num_subscribed}!")
    return jsonify(f"Enter a valid email address") # 3

@app.route("/incomeVScigs.svg")
def plot1():    
    fig, ax = plt.subplots(figsize=(3, 2))
    # default options
    y_var = 'MPG.city'
    n_bins = 10
    # if user provided arguments, check and update the default args
    if len(flask.request.args) > 0:
        if 'y' in list(flask.request.args):
            y_var = flask.request.args['y']
        if 'bins' in list(flask.request.args):
            n_bins = flask.request.args['bins']
    # plot
    pd.DataFrame({'Price':df['Price'], 'MPG':df[y_var]}).plot(ax=ax, x='Price', y='MPG', kind='hist', legend=False, bins=int(n_bins))
    # set labels depending on arguments
    ax.set_xlabel("Price of Car")
    if y_var == 'MPG.city':
        ax.set_ylabel("MPG in City")
    else:
        ax.set_ylabel("MPG on Highways")

    plt.tight_layout()
    f = io.StringIO() 
    fig.savefig(f, format="svg")
    # save figure
    if len(flask.request.args) > 0:
        plt.savefig("dashboard1-query.svg")
    else:
        plt.savefig("dashboard1.svg")
    plt.close()
    
    return flask.Response(f.getvalue(), headers={"Content-type": "image/svg+xml"})
    
@app.route("/compactVSsporty.svg")
def plot2():
    fig, axs = plt.subplots(1, 2)
    df.loc[(df['Type']=='Compact')].plot(ax=axs[0], x='MPG.city', y='MPG.highway', title='Compact',
                                         kind='scatter').set_ylim(ymin=22, ymax=40)
    df.loc[(df['Type']=='Sporty')].plot(ax=axs[1], x='MPG.city', y='MPG.highway', title='Sporty', 
                                        kind='scatter').set_ylim(ymin=22, ymax=40)
    axs[0].set_ylabel("MPG on Highways")
    axs[1].set_ylabel("MPG on Highways")
    axs[0].set_xlabel("MPG in City")
    axs[1].set_xlabel("MPG in City")
    plt.tight_layout()
    f = io.StringIO() 
    fig.savefig(f, format="svg")
    plt.savefig('dashboard2.svg')
    plt.close()

    return flask.Response(f.getvalue(), headers={"Content-type": "image/svg+xml"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.
