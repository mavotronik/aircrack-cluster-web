from flask import Flask, render_template, request, redirect, url_for
import yaml
from mqtt import MQTT
import os
import threading
import json

def load_config(file_path="config.yaml"):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

mqtt_id = config["mqtt"]["client_id"]
upload_folder = config["dirs"]["uploads"]
os.makedirs(upload_folder, exist_ok=True)

app = Flask(__name__)
mqtt_client = MQTT(mqtt_id)


def mqtt_loop():
    mqtt_client.connect()
    mqtt_client.subscribe("cluster/clients/stats/#")
   
    while True:
        pass  

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    pcap = request.files["pcap"]
    wordlist_name = request.form["wordlist"]  

    pcap_path = os.path.join(upload_folder, pcap.filename)
    dict_path = os.path.join(upload_folder, wordlist_name)  
    pcap.save(pcap_path)

    task = {
        "pcap_file": pcap.filename,
        "dict_file": wordlist_name
    }

    print(f"[>] Отправка задачи: {task}")
    mqtt_client.publish("cluster/tasks/new", json.dumps(task))

    return redirect(url_for("index"))

if __name__ == "__main__":
    threading.Thread(target=mqtt_loop, daemon=True).start()  
    app.run(config["web"]["ip"], config["web"]["port"], debug=True, use_reloader=False)
