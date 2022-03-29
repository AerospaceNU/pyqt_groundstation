# pyqt_groundstation

PyQt based GUI program for the DPF rocket (and other stuff?). 

## Install dependencies
This has all been tested on python 3.8.  Use another version at your own risk

On Windows I had to get microsoft visual cpp first
`https://visualstudio.microsoft.com/visual-cpp-build-tools/`
You need the "Visual studio build tools"

This link was helpful:
https://stackoverflow.com/questions/44951456/pip-error-microsoft-visual-c-14-0-is-required

On linux I needed bluetooth-dev and espeak
`sudo apt-get install libbluetooth-dev espeak`

Then get python dependencies with Pip
~~~
pip3 install pyserial opencv-python pyqt5==5.15.4 imutils navpy pyqtchart pyqtgraph pynmea2 pybluez psutil pyttsx3 qtrangeslider[pyqt5]
~~~

## Radio messages
All radio messages from the rocket have this format:
~~~
uint8_t packetType;
uint8_t softwareVersion;
uint32_t timestampMs;
char callsign[8];//14
[DATA]
uint8_t RSSI
uint8_t CRC and LQI
~~~

The [DATA] field is different depending on the packetType

Message type 0 is called "Old transmit stuff"
~~~
float  gps_lat,     gps_long,     gps_alt;//26
float pos_z, vel_z;//34
float    baro_pres;//38
double   battery_voltage;//46
uint8_t  pyro_continuity;
uint8_t  state;//48
~~~

## Naming conventions
PyQt has the concept of a "widget", or a specific part of a GUI, like a text entry box or something. 
This GUI also has "widgets", which are typically a collection of PyQt widgets. 
For the rest of this document, when I say "widgets", I mean the ones specific to this GUI, 
and when I say "PyQt widgets", I mean widget classes from PyQt.

## Structure

### File locations
The dpf_ground_station.py file is the main class that has most of the high level control of the GUI. 
This handles the creation of tabs, the data updating, and managing modules.

### Database dictionary
All the data in the gui lives inside the main database dictionary.
This dictionary is updated from the Data Interfaces, and sent to each widget every update cycle. 

### Widgets
Classes for widgets live in the Widgets folder. 
Each widget class extends `custom_q_widget_base.py`, which provides all the base functions needed for the data-handling side of the GUI. 
`custom_q_widget_base.py` extends QWidget, so any of the widgets for this GUI can be treated like normal PyQt widgets.

To get data from the widget overwrites the `updateData` function, which takes the GUI database dictionary as an argument. 
Each widget then gets their required data from the GUI database dictionary, and sets values accordingly.

#### QWidget_Parts
This is where custom PyQt widgets (widgets that directly extend a PyQt widget) go. 

#### Helpers
This is kind of legacy structure that I don't want to fix, but the class in here handles image display, but doesn't extend a PyQt widget. 
It would be better to refactor it so that it does extend QWidget or QLabel or something.

### Main Tabs
`main_tab_common.py` is an abomination. 
I'm going to try to fix it some, but I don't want to spend a huge amount of time on it yet, since it works.
To add a custom tab, extend `main_tab_common.py` and call `self.addWidget` to add widgets to the call list.
Look at `primary_tab.py` for a nice example.

### Modules
This framework was designed to make it simpler to add new features to the GUI. 
Anything that provides data to the GUI should be a module, and anything that uses the data for any reason other than to drive visuals (for example the text to speech).

The modules are how the GUI actually gets data from radios or log files or whatever.
`data_interface_core.py` spins up a thread, and calls `spin()` in a loop at a maximum of 100hz.
`spin()` runs in a thread, so your implementation can hang the thread, but maybe don't hang forever, because the thread might not close down correctly.
Like other things, to add a new one, extend `data_interface_core.py`, and overwrite the `spin()` function. 
You'll also need to add a line to `main.py` to register your data interface.

### Bluetooth linux error
~~~
sudo chmod o+rw /var/run/sdp
~~~

## Adding custom functionality
In basically anything simple you'd need to add, you'll just extend the base class, and overwrite a few functions.

- For widgets, everything should happen automatically from there.
- For modules, you'll need to add a line to main.py to register it.
- For Tabs, you'll need to add a line to `gui_core.py` in the `addTabByTabType` function, that takes the string name and string type of your tab, and calls `self.addVehicleTab([TabType], tabName)`. 
You'll also need to add a line to the `run` function in `dpf_ground_station.py` that calls `self.addTab()` with the string name and string type from above.
