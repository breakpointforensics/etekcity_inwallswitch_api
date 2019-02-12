import requests
import hashlib
import json
import time
import datetime
import io
import json
import logging
import sys
from urllib.request import urlopen

#etekcitySwitch.py
#Version 1.0
#12/23/2018
#Author: @PROJECTSKYDROID
#Thanks to solarkennedy@github for initial research on plug devices.


# Define pseudo constants
SCRIPT_NAME = 'etekcitySwitch.py'
SCRIPT_VERSION = '1.0'

requests.packages.urllib3.disable_warnings()

BASE_URL = "https://smartapi.vesync.com"

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

#**************************
#Replace Username and Password with your personal account.
USERNAME = "ENTER_USERNAME_HERE"
PASSWORD = "ENTER_PASSWORD_HERE"

#Mobile ID is a random value that appears to be generated based on individual phone app installation.  This field is required to entered when processing on-off state commands.  
#Testing indicates there does not appear to be any validation of this value however and any hexadecimal string of matching length can be randomly generated and entered.
#Otherwise, if you want your exact unique ID, you'll have to intercept these api calls from your mobile device and decode the packet.(Like I said, not necessary but up to you)
mobileID = "65bdde772a3cff1d"

#Call this whatever you want
switchName = "EXAMPLE_NAME"

#The switch ID is referred to as "UUID" in the API calls, and can be retrieved by using option 5 to dump a list of all your devices to a text file.
#The UUID HAS A FORMAT SUCH AS XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
switchID = "ENTER_SWITCH_UUID_VALUE_HERE"

#Creates empty token and accountid variables which are automatically filled when script runs as long as username and password entered above.
token = ""
accountID = ""

# Turn on Logging using standard python logging package, assign logname variable, and set formating for time and messages.
logging.basicConfig(filename=switchName+'_switch.log',level=logging.DEBUG,format='%(asctime)s %(message)s')
logging.info("Welcome to " + SCRIPT_NAME + " " + SCRIPT_VERSION + " Logging Started for " + switchName)
logging.info("Switch UID " + switchID)




class VesyncApi:
    def __init__(self, username, password):
        global token
        global accountID
        
        payload = json.dumps({"account":username,"devToken":"","password":hashlib.md5(password.encode('utf-8')).hexdigest()})
        account = requests.post(BASE_URL + "/vold/user/login", verify=False, data=payload).json()       
        if "error" in account:
            raise RuntimeError("Invalid username or password")
        else:
            self._account = account
            #print (account)
            token = account['tk']
            #print (token)
            accountID = account['accountID']
            #print (accountID)             
            print ('Account Connection Successful')
            
        self._devices = []


    def get_detail(self, id):
        global token
        global accountID        
        payload = {'accountID':accountID,'token':token,'timeZone':'America/Phoenix','uuid':id,'mobileId':mobileID}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.post(BASE_URL + '/inwallswitch/v1/device/devicedetail/',headers=headers, json=payload)
        
        #Gets the json response loaded in r and parses out the value of key "deviceStatus"
        rState = r.json().get('deviceStatus')
        rTime = r.json().get('activeTime')
        
        print ('In-Wall Switch Status'+ " " + id)
        print (r.text)
        print (st + ' - ' + rState + ' for ' + str(rTime) + ' Minutes')
        logging.info(switchName + " " + rState + ' for ' + str(rTime) + ' Minutes')
    
        return r
    
    def get_devices(self):
        global token
        global accountID
        payload = {'accountID':accountID,'timeZone':'America/Phoenix','token':token}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.post(BASE_URL + '/platform/v1/app/devices/',headers=headers, json=payload)
        parsedResponse = (r.text)
        devices = parsedResponse.split(",")
        orig_stdout = sys.stdout
        sys.stdout = open("fulldevicedump.txt", "w")
        for line in devices:
            print (line)
        sys.stdout.close()
        sys.stdout=orig_stdout
        logging.info("Listing of all devices associated with account and their states dumped to 'fulldevicedump.txt'")

    def turn_on(self, id):
        global token
        global accountID        
        #Sends Json Payload to Turn On Switch
        payload = {'accountID':accountID,'token':token,'timeZone':'America/Phoenix','uuid':id,'status':'on'}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.put(BASE_URL + '/inwallswitch/v1/device/devicestatus/',headers=headers, json=payload)
        logging.info(switchName + " on command manually sent")
        #Pause for 5 seconds to allow cloud server to update status
        time.sleep(5)
        
        #Sends a details payload to refresh the new switch status.
        payload = {'accountID':accountID,'token':token,'timeZone':'America/Phoenix','uuid':id,'mobileId':mobileID}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        #Get Json response and parse only for on-off state
        r = requests.post(BASE_URL + '/inwallswitch/v1/device/devicedetail/',headers=headers, json=payload).json().get('deviceStatus')
        
        #Prints refreshed state
        print ('Switch is ' + r)
        logging.info(switchName + " is " + r)
        
    def turn_off(self, id):
        global token
        global accountID        
        payload = {'accountID':accountID,'token':token,'timeZone':'America/Phoenix','uuid':id,'status':'off'}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.put(BASE_URL + '/inwallswitch/v1/device/devicestatus/',headers=headers, json=payload)
        logging.info(switchName + " off command manually sent")
        #Pause for 5 seconds to allow cloud server to update status
        time.sleep(5)
        
        #Sends a details payload to refresh the new switch status.
        payload = {'accountID':accountID,'token':token,'timeZone':'America/Phoenix','uuid':id,'mobileId':mobileID}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        #Get Json response and parse only for on-off state
        r = requests.post(BASE_URL + '/inwallswitch/v1/device/devicedetail/',headers=headers, json=payload).json().get('deviceStatus')
        
        #Prints refreshed state
        print ('Switch is ' + r)
        logging.info(switchName + " is " + r)
        
    def set_auto_off(self, id):
        global token
        global accountID
        
        #Prints user instructions.
  
        autoOffTime = int(input('Please enter time in minutes for how long the switch can be on before automatically shutting off:'))
        pollTime = int(input('Please enter time in seconds for how often to poll the switches on/off status:'))
        logging.info(switchName + " Energy Saver Mode Started - Auto Shutoff Time set for: " + str(autoOffTime) + " Polling every " + str(pollTime) + " seconds")
        
        while True:
            payload = {'accountID':accountID,'token':token,'timeZone':'America/Phoenix','uuid':id,'mobileId':mobileID}
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            r = requests.post(BASE_URL + '/inwallswitch/v1/device/devicedetail/',headers=headers, json=payload)
            
            #Gets the json response loaded in r and parses out the value of key "deviceStatus"
            rState = r.json().get('deviceStatus')
            rTime = r.json().get('activeTime')
            
            print ('In-Wall Switch Status'+ " " + switchID + id)
            print (st + ' - ' + rState + ' for ' + str(rTime) + ' Minutes')
            logging.info(switchName + " Polling State")
            logging.info(switchName + " - " + rState + " for " + str(rTime) + " Minutes")
            
            if rState == "on":
                if rTime > int(autoOffTime):
                    print (st + " Switch left on to long. Shutting off...")
                    logging.info(switchName + " left on to long. Shutting off...")
                    #Sends Json Payload to Turn Off Switch
                    payload = {'accountID':accountID,'token':token,'timeZone':'America/Phoenix','uuid':id,'status':'off'}
                    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
                    r = requests.put(BASE_URL + '/inwallswitch/v1/device/devicestatus/',headers=headers, json=payload)                    
                    #Pause for 5 seconds to allow cloud server to update status
                    time.sleep(5)
                    #Sends a details payload to refresh the new switch status.
                    payload = {'accountID':accountID,'token':token,'timeZone':'America/Phoenix','uuid':id,'mobileId':mobileID}
                    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
                    #Get Json response and parse only for on-off state
                    r = requests.post(BASE_URL + '/inwallswitch/v1/device/devicedetail/',headers=headers, json=payload).json().get('deviceStatus')
                    logging.info(switchName + " Auto shutoff returned status " + r)
                    
                    #Prints refreshed state
                    print ('Switch is now' + r)
            
            logging.info(switchName + " timer process sleeping for " + str(pollTime) + " seconds")
            time.sleep(pollTime)
                

        
        
        
        
         



    
api = VesyncApi(USERNAME,PASSWORD)


#Print Initial Welcome Message in Console Window with a Line Break and more underlining characters.
print ("Welcome to " + str(SCRIPT_NAME) + " " + str(SCRIPT_VERSION) + "\n=======================")



#Create a set of valid user choices to validate user input against.
values = set(["T","1", "2", "3", "4", "5"])

#Create empty variable called commandChoice
commandChoice = []



while True:
    

    #Prints brief description of script and user instructions.
    print ('Enter Choice (T,1,2,3,4,5)')
    print ('\n')
    print ('T. Set Automatic Shutoff Timer')
    print ('1. Get Switch State')
    print ('2. Turn-On Switch')
    print ('3. Turn-Off Switch')
    print ('4. Show Account Token')
    print ('5. Get Full Device List')
    
    
    #Start while loop that will request the user enter a switch command.
    while True:
        #Use raw_input function to present console request to user to enter NTP server choice, and pass input converted to uppercase, to variable ntpChoice.
        commandChoice = input("Please enter switch command, or 'q' to exit:").upper()
    
    
        #Set q as break command to end while loop and exit script using sys modules exit function.
        if commandChoice == "Q":
            print (SCRIPT_NAME + " Closed")
            sys.exit(0)
    
        #Validates the raw_input against the valid choices in the set "values".  If input exists in "values", the while loop breaks and continues script.
        if commandChoice in values:
            print (commandChoice + ' Selected')
            break
    
        #If raw_input not in set "values", prints error message and returns to raw_input prompt.
        print ("Not a Valid choice!\nValid Choices:\nT\n1\n2\n3\n4\n5")
    
    
    
    if commandChoice == ('T'):
        print ('Setup Auto Shutoff (Energy Saver Mode)')
        api.set_auto_off(switchID)    
        
    if commandChoice == ('1'):
        print ('Getting Switch Details')
        api.get_detail(switchID)
    
    if commandChoice == ('2'):
        print ('Turning On')
        api.turn_on(switchID)
    
    if commandChoice == ('3'):
        print ('Turning Off')
        api.turn_off(switchID)

    if commandChoice == ('4'):
        print ('Getting Account Token...')
        print(api._account)
    
    if commandChoice == ('5'):
        print ('Getting Full Device List...')
        api.get_devices()
