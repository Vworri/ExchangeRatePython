from flask import Flask, request, jsonify
from exchangeRate import ExchangeRate as ex
from datetime import date
import threading
import json

app = Flask(__name__)

@app.route("/api", methods=["GET"])
def default():
    """api endpoint for currency conversion:
    example query: /api/?orig=usd&dest=aud&amount=3"""
    origin = request.args.get("orig")
    destination = request.args.get("dest")
    
    if request.args.get("amount"):
        amount = float(request.args.get("amount"))
    else:
        amount = 1
    if request.args.get("date"):
        exDate = request.args.get("date")
    else:
        exDate = date.today()
    res = ex.at(str(exDate), origin, destination)
    res["originalAmount"] = amount
    res["resultAmount"] = ex.exchangeCash(res["rate"],amount,destination)
 
    return jsonify(res)


@app.route("/info", methods=["GET"])
def getInfo():
    res = ex.max_minDate()
    return jsonify(res)


def start_auto():
    worker_thread = threading.Thread(target=ex.worker)
    app_thread = threading.Thread(target=app.run)
    worker_thread.setDaemon(True)
    worker_thread.start()
    app_thread.start()

def start_server_only():
    app.run()

def start_worker_only():
    ex.worker()

if __name__ == '__main__':
    ex.getDailyRates()
    start_auto()
