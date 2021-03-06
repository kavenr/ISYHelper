# ISYHelper
Program to assist with communication between ISY994 and anything else.

This is a python program to assist with communicating between the [ISY994i Series Controller](https://www.universal-devices.com/residential/isy994i-series) and any other device you can access.

# Configuration

The configuration file is in YAML format, and an example is provided which contains all necessary information.

The Helper is responsible for managing the device and setting the variables on the ISY.  
## name
Each helper has a 'name' which is any name you chose, but must be unique.
## type
The type of helper, which are described in the Helpers section below.

The variables defined by the Helpers will all start with "s.IH." (will make this configurable) followed by the device 'name', followed by the variable name.  For example if you defined your DateAndTime Helper name as 'DT', then it will set variables like "s.IH.DT.Minute" on your ISY.  When isyhelper starts up it will check for the variables that it needs to exist, and will quit with an error if they are not.

## ssl

You can enable SSL by setting the certificate and private_key params to point to your files.

# REST Interface

The ISYHelper has a REST interface that can direct commands to the individual helpers by name which is supported in the some Helpers.  The interface is available at http://ipaddress:port/HelperName where ipaddress is the IP of you RPi, port is the port specfied in config.yaml, or 8080 by default, and HelperName is the name: specified for the helper.

To verify ISYHelper and the REST interface are alive, go to http://ipaddress:port on a web browser which will disply the version information, and see more information for each type of helper.


# Helpers

ISYHelper defines unique Helper modules for the type of device, and has been written in a way to make adding any new helpers as easy as possible.

## Helper: Test

This is really just a test device for development.

## Helper: DateAndTime

Controls setting date and time variables on the ISY.  The following ISY variables can be set
  * s.IH.DateAndTime.Second
  * s.IH.DateAndTime.Minute
  * s.IH.DateAndTime.Hour
  * s.IH.DateAndTime.Day
  * s.IH.DateAndTime.Month
  * s.IH.DateAndTime.Year
  * s.IH.DateAndTime.Pong

The config file allows you to choose the level of updates with the interval option which can be second, minute, hour or day depending on how often you want isyHelper to update, which also determine which variables will be updated on the ISY.  

### Ping/Pong

The DateAndTime helper now includes a ping/pong feature.  This verifies that ISYHelper is properly observing the changes happening on the ISY and is able to push information back to the ISY.  This works by watching the interval variable and then setting the Pong variable to the matching value.  For example if you have the config interval set to minute, then ISYHelper will set the Pong to match the minute variable as soon as changes.  This allows you to write programs on the ISY to monitor and send notifications if ISYHelper is not working properly.  In my experience, I will see an issue during the ISY Query All which is typically run at 3am each morning, but then the issue clears up shortly after that, but if you have a huge or unstable ISY network it may take longer.  See [README.ISY](/README.ISY.md) for example programs.

## Helper: PyHue

This starts a [Python Hue Hub Emulator](https://github.com/falk0069/hue-upnp) that allows the Amazon Echo and Harmony Hub to control and monitor the ISY devices.

### devices

By default all devices that have a 'Spoken' property set in the ISY notes will be added to the list.  To set this right click on the device in the ISY admin console and select 'Notes'.  If you have a recent version of the ISY fireware and admin console you should see the option to add 'Spoken'.  If you want the spoken name to always match the device name, just make the value of the Spoken property be the number one '1', without the quotes.

You only need to hard code the device in the config for devices that do not have the Spoken property set. You can find all your device names and address http://your_isy_ip/rest/nodes

To control a scene you can set the Spoken on the scene controller, in which case the PyHue will turn on the scene, or set the Spoken paramater on the secen.

IMPORTANT: Currently if you 'group device' it will not find your Spoken property on your devie.  This is an issue with the PyISY library that I will try to fix soon because almost all my devices were grouped.

  * name
    Currently the name must be specified, and can be the full full path to the device name in your folder hierarchy, or just the device name.  This will also be what you call the device for Alexa, unless the spoken param is set below.
  * address
    This is the device or scene address.  This is not required if name is the real device name.
  * spoken
    You can add a device by name, then set spoken to have the spoken name be different than the device name.

### REST Interface

The default interface is at http://ipaddress:8080/PyHue.  The following are supported:
   * /listen/start : Start the listener, this must be done when discovering devices with Alexa or Harmony.
   * /listen/stot  : Stop the listener, this should be done when you are not discovering to reduce load and traffic on the RPi

## Helper: PyHarmony

This uses the [Python Harmony interface](https://github.com/jimboca/pyharmony) to track and control the Harmony Hub from the ISY.

### ISY Variables

The Harmony hub current activity in tracked in an ISY variable, and allows you to set that variable to control the Harmony activity.  Currently the Hub is polled every 30 seconds update the isy variable.  When the ISY variable is changed manually or through a program, that activity is immediatly passed to the Hub so you can create programs on the ISY that control the Harmony Hub!

You must create the Variable that matches the name you chose in the config.yaml.  For example if you used:
```
  - name: FamilyRoomHarmony
    type: PyHarmony
```
Then you must create an ISY State Variable "s.IH.FamilyRoomHarmony.CurrentActivity".

### Activity ID's
   * The Activity ID's are printed to stdout when starting pyharmony
   * You can find them in the log_file defined config.yaml: grep PyHarmony isyhelper.log
   * You can use the REST interface to find them

### REST Interface

The default interface is at http://ipaddress:8080/MyHarmony.  The following are supported:
   * /show/info : Print the basic info about the current and available activities
   * /show/activities : Dump the full json of the harmony activities
   * /show/devices : Dump the full json of the harmony devices
   * /show/config : Dump the full json of the harmony config
   * /send/command/deviceid/command : Send command to device id.  Look up the deviceid's and commands with show/devices.
   * /start/activity/activityid : Start the activity activityid.

To see all available /send and /start commands got to http://ipaddress:8080/MyHarmony of your RPi which will list the URL's.

You can use the above rest commands to access the Harmony hub. There is a command interface to change the current Activty, but you shouldn't use this to change the activity from the ISY, you should set the ISY variable instead.

See config.example.yaml for the example setup and description.

## Helper: FauxMo

This runs the excellent Belkin WeMo emulator https://github.com/makermusings/fauxmo which allows the Amazon Echo to control the ISY and IFTTT Maker!  

To use this, you currently have to grab my version from from git.  So in the same directory where you have ISYHelper (not inside the ISYHelper directory) run:
git clone https://github.com/jimboca/fauxmo as shown in the install instructions below.

See the config.example.yaml for some examples.

### devices
  All information for PyHue devices applies to FauxMo devices, along with the following extras.
  
  * type
    This can be 'ISY' or 'Maker', and the default is 'ISY' if not specified.
  * on_event
    This is the Maker IFTTT event to turn the device on
  * off_event
    This is the Maker IFTTT event to turn the device off

Note that each time you start isyhelper.py, you must tell Alexa to 'discover devices'.  This is because the port numbers for each device are random so they are likely different each time.

## Helper: Maker

Receives IFTTT Maker requests.  This is the intial version of Maker support, so it will likely change based on feedback from everyone.

Currently the 'name' and 'type' must be 'Maker' in your config file.  You must set the 'token' to something, it's like a lame password...

You must forward a port on your router to the IP address of the device runing ISYHelper port 8080.  (Yes it's hardcode to 8080, I need to add a config param...)

### Maker Setup

This may be broken as of 1.14.  If you would like this to be supported, please let me know and I'll test it.  Or you can now use the UDI Portal to access IFTTT.

- Setup your [Maker channel on IFTTT](https://ifttt.com/maker)
- Click on the "Make a web request" on that page
- Set the Trigger to what you want
- Set the Action:
  - URL: http://your_host_or_ip:port_num/maker
  - Method: POST
  - Content Type: application/json
  - Body:  { "token" : "my_secret_token", "type" : "variable", "name" : "varname", "value" : "1" }

  For the above URL, you can use https if you have a certificate, and your_host_or_ip is for your router name or IP to the outside, and port_num is the port number you set to forward to 8080.  The token must match the token in your config file.

  For the Body:
  - type
  The type of object on the ISY we will set, only variable right now
  - name
  The Variable name to set, varname in the example.  Currently only State variables are supported, not Integers!
  - value
  The Value to set the variable

## Helper: Foscam1

This Helper communicates with a Foscam cameras that use the [IP Camer CGI Interface](http://www.foscam.es/descarga/ipcam_cgi_sdk.pdf), like the Insteon 75790R which are what I tested with.

The Helper initializes the alarm params on the camera to point back to the REST interface of the isyHelper which sets the Motion variable for the camera when the alarm is triggered, then starts a monitor which checks every 5 seconds if the motion alarm is still enabled or not.  

This will set the ISY variable 'Motion' for the device.

# Install, Run, Upgrade, Uninstall

## Setup your ISY

## Spoken Property

If you plan to use the Spoken property from the ISY for FauxMo or PyHue helpers, then you must set them in the ISY before starting isyhelper.  Go to your ISY admin console and Right click on the device or scene you want to control and select 'Notes' then in set 'Spoken' to 1. By setting it to 1 it will use the device name as the spoke name, if you want this to be different then just enter the spoken name you want to use.

## Required Variables

If you have the DateAndTime helper enabled, create the [DateAndTime Variables](#helper-dateandtime) listed.

If you have a PyHarmony helper enabled you must create the variable documented in [PyHarmony Variables](#helper-pyharmony)

## Download and configure

Currently there is no installation processes, you must download to try it.  Also, the python modules listed in the "To Do" section must be installed.

- Create a directory where you want to store it in the home directory
  - cd
  - mkdir isyhelper
  - cd isyhelper
- Grab all the code
  - git clone https://github.com/jimboca/ISYHelper
  - cd ISYHelper
  - ./install.sh
- Configure the helpers you want to use
  - cp config.example.yaml config.yaml
  - nano config.yaml

## Manually starting
- ./isyhelper.py

The program will record all information and errors in the log file, to see any errors run 'grep ERROR isyhelper.log', or whatever you set the log to in your config.yaml 'log_file' setting.

Depending on how many devices you have it can take a minute or more to finish starting up, so wait until you see all 'Starting helper' lines for the helpers you have enabled.

If you start in a terminal like shown and close the terminal then isyhelper will exit.  If you want it to stay running after closing the terminal, start it with the ih.start script

If you start it in the forground, then it not let you stop the program with a control-c.  You must background it with control-z then 'kill %1'.

## Run on startup

### Starting as a service.

  This does not work on Raspian Wheezy, you need to be on at least Jessie.
  
  Is sytemctl installed?
    * Run: sudo which systmctl
    * If it returns nothing, you need to install the newer version, which is currently Jessie
      To upgrade you can do this:
        http://linuxconfig.org/raspbian-gnu-linux-upgrade-from-wheezy-to-raspbian-jessie-8
      but the prefered method is to just backup all your files and install Jessie from scratch, but I did try the upgraded on one of mine and...
      
  If it is installed you should use this method, not the rc.local method!
  
  * cd /home/pi/isyhelper/ISYHelper (or wherever you put it, and if you put it somwhere else, you also need to edit the isyhelper.service file)
  * sudo cp isyhelper.service /lib/systemd/system/
  * sudo systemctl --system daemon-reload
  * sudo systemctl enable isyhelper
  * sudo systemctl start isyhelper
  * sudo systemctl status isyhelper

### rc.local method

If you are running Raspian Wheezy you must use this method.  If you are running Jessie, you should NOT use this method, you should use the starting as a service above.
  * sudo nano /etc/rc.local
  * Add this line before the 'exit 0' at the end, where /home/pi is the location you downloaded to.
```
( cd /home/pi/isyhelper/ISYHelper ; ./isyhelper.py & )
```

### Restarting

If you started ISYHelper in the forground, then it  not let you stop the program with a control-c.  You must background it with control-z then 'kill %1'.

If it is running from the rc.local script at startup then it is running as root, so you need to find and kill the processs with
...
ps -ef | grep isyh
...
Note the process id which is the second column for the isyhelper process and run kill on that process id

## Upgrading

If you are on a recent version there will be a script in the ISYHelper directory, just run that script
```
cd /home/pi/isyhelper/ISYHelper
./update.sh
```
If you do not have the update.sh script, just run this first:
```
git pull
```
Then run the update.sh.

## Uninstall

To remove the install just delete the directory isyhelper or whatever you called it and remove it from whichever startup method you chose, rc.local or service.

# To Do

## Other modules that could be used.
Only if you are going to use the NMap helper (which isn't released yet)
For some reason 'sudo pip install libnmap' wont work for me?  So had to do it this way:
```
git clone https://github.com/savon-noir/python-libnmap.git
cd python-libnmap
python setup.py install
sudo pip install collections
sudo apt-get install nmap
sudo pip install libnmap
```
If you plan to use SSL (https) for Maker, and you have a real certificate (not self signed) you need to install these as well:
```
sudo apt-get install libffi-dev
sudo apt-get install python-dev
sudo pip install pyOpenSSL
```
Note: It takes a while to compile pyOpenSSL packages like cryptography...

## Multiple responses for large device count

Currently testing sending seperate responses to a query so only one server can be running to handle > 63 devices, which is the documented hue maximum per hub.  I have currently tested 48 devices and it works as expected.  http://www.developers.meethue.com/documentation/bridge-maximum-settings

## TiVo

Look into the TiVo interface options for changing channels directly instead of thru the Harmony.

## Spoken for Variables

Plan to add support for a naming convention of variables to specify their spoken name.

# Isssues

- IFTTT Maker Channel does not allow a self-signed certificate, so I have not been able to test...  I need to get a real certificate...

I created one with this info:
  - http://heapkeeper-heap.github.io/hh/thread_1344.html
  - http://www.8bitavenue.com/2015/05/webpy-ssl-support/

- I have only tested this on a RPi with Python 2.7.  I had issues trying to install the web.py module on my RPi with Python 3.2 so if I figure that out I will test with 3.2.

# Known Bugs
* hue-upnp does not die if http_port is in use and can't be started, just issues the message and continues
* ISYHelper is trapping and ignoring control-C, I think this is happening in web.py so need to investagate
* log rolling doesn't seem to be working properly.
  * Deleting old logs does not clear space, have to restart.
  * Seems to be keeping all logs instead of just 7 days worth.

# Versions

* 11/26/2016:  Version: 1.15  Changes for latest version of pyharmony to support authorization fixes.
* 03/01/2016:  Version: 1.14  Switch from Python web.py to Flask
                              Better control of log file rotation each night, and keep 7 for debugging for now.
			      Default index file at http://ipaddress:8080/ with links shown for PyHarmony activities and commands.
                              This version may have broken IFTTT support, but I don't think anyone is using it anymore.  If you are, please let me know and I will test it.
* 02/12/2016:  Version: 1.13  Add Ping/Pong.  See DateTime module [Ping/Pong](#pingpong) documentation.
* 02/08/2016:  Version: 1.12  Add REST send/command to PyHarmony
* 02/07/2016:  Version: 1.11  Add instructions for starting as a service, added REST interface for PyHarmony and PyHue helpers.  PyHue now starts up in not-listening mode, must use REST interface to start the listener.
* 01/10/2016:  Version: 1.10  Add automatic creation of FauxMo devices for a Harmony Hub
* 01/09/2016:  Version: 1.09  First release of PyHarmony support.
* 01/03/2016:  Version: 1.08  Update to latest hue-upnp so IP and PORT can now be passed in.
* 11/21/2015:  Version: 1.07  Fixed for scenes that do not have a controller
* 11/18/2015:  Version: 1.06  Add support for spoken property on scenes.
* 11/15/2015:  Version: 1.05  First official release with PyHue support.  
* 09/07/2015:  Fixed when notes exists, but spoken was empty.  Update to PyISY and ISYHelper
* 09/05/2015:  A new version is released with better automatic support of the Spoken parameter for Amazon Echo.

**HUGE** Thanks to Automicus (Ryan Kraus) for his https://github.com/automicus/PyISY library which this references.

- AUTHOR: JimBoCA
- DATE: 8/10/2015
- EMAIL: jimboca3@gmail.com

