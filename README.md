# etekcity_inwallswitch_api
Python API Script to make direct API calls to Etekcity / VeSync Cloud for WiFi In-Wall Smart Switch

Requirements:

  Python 3
  
  Python "Requests" Module (https://pypi.org/project/requests/)
  
  Etekcity Wifi Light Switch (https://www.etekcity.com/product/100323)
  
 
Use:
 -Download etekcitySwitch.py
 
 -Edit script and enter your unique values for:
 
    --USERNAME
    
    --PASSWORD
    
    --mobileID (Optional, see comments in File)
    
    --switchID
    
    --switchName
  
 -Run script
 
 Script also generates and maintains a logfile in same directory.
 
 
 Script provides 5 basic options at this time:
    Example Run:
    
        Welcome to etekcitySwitch.py 1.0
        =======================
        Enter Choice (T,1,2,3,4,5)


        T. Set Automatic Shutoff Timer
        1. Get Switch State
        2. Turn-On Switch
        3. Turn-Off Switch
        4. Show Account Token
        5. Get Full Device List
        Please enter switch command, or 'q' to exit:
 
 
 Function Description:
 
 T. Set Automatic Shutoff Timer
 
        This is a missing function is the current Vesync app.  This allows you to set an automatic 
        shutoff period and configure how often you want the script to poll the on/off status of the switch.  
        If the switch is left on after the configured period, it will automatically get turned off.  Once 
        started, the script will continue to run in a loop, polling the on/off state and issuing
        shutoff commands until the script is terminated.

 1. Get Switch State
 
        Queries the current state and details of the configured switch. And prints response.
 2. Turn-On Switch
 
        Issues on command to configured switch.
 3. Turn-Off Switch
 
        Issues off command to configured switch.
 4. Show Account Token 
 
        Prints the account token and accountID for the configured account.
 5. Get Full Device List
 
        Queries all devices associate with VeSync account and dumps full list of devices and their unique ID's to a 
        text file named "fulldevicedump.txt".
        
     
