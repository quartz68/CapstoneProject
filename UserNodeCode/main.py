import requests
from setup import setup
from page_handler import display_img, hide_calc_page, idle_screen, unidle_screen
from page_setup import page_setup
import flask 
from flask import request, jsonify
import threading
import socket
import cv2
from PIL import Image
from SingletonDeckState import SingletonDeckState

# Create Flask app instance
app = flask.Flask(__name__)

# Create a SingletonDeckState instance
deck_state = SingletonDeckState()

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

# Define a route to receive laptop IP address
@app.route('/laptop_ip', methods=['POST'])
def get_laptop_ip():
    # Get the IP address from the request data
    data = request.get_json(force=True)
    deck_state.laptop_ip = data["ip"]
    # deck_state.laptop_id = data["userID"]
    print("Received IP:", deck_state.laptop_ip)
    return {"status": "success"}

# Function to send print label request
def send_print_label():
    requests.post(deck_state.laptop_ip + "/print_label")

# Function to send print document request
def send_print_doc():
    requests.post(deck_state.laptop_ip + "/print_doc")

# Function to send user IP address
def send_user_ip():
    # Scan the user ID
    userID = ""
    cap = cv2.VideoCapture(0) 
    detector = cv2.QRCodeDetector()
    while True: 
        _, img = cap.read()

        img_cvt = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_cvt)
        display_img(img_pil)
        
        data, bbox, _ = detector.detectAndDecode(img) 

        if cv2.waitKey(100) & 0xFF == ord("q"):
            idle_screen()
            break
        if data: 
            userID=data 
            idle_screen()
            break
    # Set the user ID and IP address
    # userID = "1669217383057x956943083712790800"
    # userID = "123"
    IP = get_ip_address()
    info = {'userID': userID, 'ip': 'http://' + IP + ':5005'}
    # Send the user IP address to the server
    requests.post('https://tools.shipitdone.com/hub/user_signup', json=info)

def logout_user_ip():
    IP = get_ip_address()
    info = {'ip': 'http://' + IP + ':5005'}
    # Send the user IP address to the server
    requests.post('https://tools.shipitdone.com/hub/user_logout', json=info)

# Define a route to receive update data
@app.route('/update', methods=['POST'])
def update():
    # Get the update data from the request
    data = request.get_json(force=True)

    print(data)

    # Post URL: https://wms.shipitdone.com/version-3tar/api/1.1/wf/capstone_ship_print/

    if data["status"] == "open":
        # Define document printers and label printers
        docPrinters = ["Rollo", "Epson"]
        labelPrinters = ["Rollo", "Epson"]
        addDocs = data["addDocs"]
        boxSizes = data["boxSizes"]

        boxSizesList = []

        # Extract box sizes from the data
        for i in range(len(boxSizes)):
            boxSizesList.append(boxSizes[i]["name"])

        print("Number of Boxes:", len(boxSizesList))

        # Set up the page with the box sizes, document printers, label printers, and additional documents
        page_setup(boxSizes=boxSizesList, docPrinters=docPrinters, labelPrinters=labelPrinters, addDocs=["Receipts"], data=data)

        # Unidle the screen
        unidle_screen()

    elif data["status"] == "closed":
        # Idle the screen
        if deck_state.current_page == -1:
            hide_calc_page()
        idle_screen()   

    return jsonify({"status": "success"})

# Run the Flask app
if __name__ == "__main__":
    # Start the Elgato setup thread
    elgato_thread = threading.Thread(target=setup)
    elgato_thread.daemon = True
    elgato_thread.start()
    
    # Send the user IP address
    send_user_ip()
    
    # Run the Flask app on host 0.0.0.0 and port 5005
    app.run(host='0.0.0.0', port=5005)