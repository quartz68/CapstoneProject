import requests
import flask 
from flask import request

laptop_ips = {}

user_ips = {}

app = flask.Flask(__name__)

@app.route('/get_data', methods = ['GET'])
def get_data():
    return user_ips

@app.route('/user_signup' ,methods = ['POST'])
def pi_signup():
    data = request.json
    userID = str(data["userID"])
    user_ip = str(data["ip"])
    user_ips[userID] = user_ip
    if userID in laptop_ips.keys():
        requests.post(user_ip + "/laptop_ip", json={"ip": laptop_ips[userID] })
    
    print("User: ", userID, user_ip)

    return {"status": "success"}

@app.route('/user_logout' ,methods = ['POST'])
def pi_logout():
    data = request.json
    user_ip = str(data["ip"])

    ids_to_remove = [key for key, value in user_ips.items() if value == user_ip]
    for key in ids_to_remove:
        del user_ips[key]

    return {"status": "success"}

@app.route('/laptop_signup', methods = ['POST'])
def laptop_signup():
    data = request.json
    print(data)
    userID = str(data['userID'])
    laptop_ip = str(data['laptop_ip'])
    print("userID", userID)
    print("laptop_ip", laptop_ip)

    if userID in user_ips.keys():
        requests.post(user_ips[userID] + "/laptop_ip", json={"ip": laptop_ip })
    
    laptop_ips[userID] = laptop_ip
    # print(data)
    return {"status": "success"}

@app.route('/router', methods = ['POST'])
def router():
    data = request.get_json(force=True)
    userID = str(data["userID"])

    print(data)

    if userID in user_ips.keys():
        ip = user_ips[userID]
        requests.post(ip+"/update", json=data)
        print("sent data")
    
    return {"status": "success"}

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=8080)
