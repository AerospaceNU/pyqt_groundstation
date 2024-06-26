# pyqt_groundstation

PyQt based GUI program for the DPF rocket (and other stuff?).

## Setup

### Get Git Repository

*If an existing AeroNU developer, just clone repository and continue: https://gitlab.com/aeronu/dollar-per-foot/pyqt_groundstation.git*

1. Download git and install executable: https://git-scm.com/downloads
2. If on Windows, add `C:\Program Files\Git\bin\` and `C:\Program Files\Git\cmd\` to PATH (in Environment Variables)
3. Run `git config --global user.name <your-name-here>` and `git config --global user.email <your-email-here>` on command line
4. Create GitLab account and request access to DPF/Redshift organization
5. On command line, navigate to folder where you want repository to live
6. Clone `pyqt_groundstation` via `https://gitlab.com/aeronu/dollar-per-foot/pyqt_groundstation.git`

### Download & Install Python

1. Go to https://www.python.org/downloads/ and download the version specified in `install_setup.sh` (Right now, that's [Python 3.8.10](https://www.python.org/downloads/release/python-3810/))
Note that if you're on Linux, you'll need to follow [these steps](https://www.linuxcapable.com/how-to-install-python-3-8-on-ubuntu-22-04-lts/)
2. Install the downloaded python executable. If given an option, add python to your PATH

### Import Project into IDE

PyCharm or IntelliJ Ultimate has good Python support and will do type hinting, supports finding definitions of functions,
and other fun things. In my experience, VSCode is smaller and faster, and still has descent Python support.

#### Pycharm

1. Download PyCharm Community Edition here:
https://www.jetbrains.com/pycharm/download
2. Install PyCharm using default settings
3. Go to `File->Open` and select the pyqt_groundstation` folder

##### Interpreter -- PyCharm

1. In PyCharm, click on `File->Settings->Project: pyqt_groundstation->Project Interpreter`.
2. Click on the gear in the top right, then `Add->Existing Environment`. For the interpreter, select `PATH_TO_VENV/.venv/(Scripts or bin)/python.exe`.
3. Click Apply.

##### Integrated Python Tools -- PyCharm

1. Click on `File->Settings->Tools->Python Integrated Tools`
2. Set `Package requirements file` to `requirements.txt`
3. Set `Docstring format` to `reStructuredText`

#### VSCode

1. [Download VSCode](https://code.visualstudio.com/download)
2. Run the installer
3. Open VSCode, then go to file->open folder->pyqt_groundstation
4. When prompted install the Python plugin -- if not, click the 4 blocks on the menu bar and search for Python by Microsoft
5. Open a Python file, and select the Python 3.8 interpreter you installed above in the bottom right corner once that loads

### Install Virtual Environment, Requirements

If you're doing prop test stand stuff, you don't have to do steps 1 or 2.

1. [Windows, rockets only] Install MSVC build tools from https://visualstudio.microsoft.com/visual-cpp-build-tools/ (for pybluez)
2. [Linux, rockets only] Install `libbluetooth-dev` and `espeak` and `python3.8-dev` via package manager. Something like: `sudo apt-get install libbluetooth-dev espeak python3.8-dev`
3. Run `install_setup.sh` from PyCharm Run Configurations (top right) or command line via `./install_setup.sh`
You may need to give it the path to your Python executable, this can be found with `which python3.8` on Linux at least.
4. If any error message occurs, find spot in script where error is output and try running manually. For Unix systems you may need the package `python3.8-venv` or `gcc`!

### Known issues under Linux

Under Ubuntu 22.04 (at least with the new Wayland), Qt is still pretty buggy. I had to install `sudo apt install libxcb-xinerama0` [source](https://stackoverflow.com/questions/68036484/qt6-qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-thou) and also run with `XDG_SESSION_TYPE=x11 python -m src.main`.

### Run GUI

1. Activate virtual environment using (Linux) `source .venv/bin/activate` or (Windows) `.\\venv\\bin\\activate.ps1` (or .bat if using command prompt instead of powershell). You should now see a (.venv) prefix to the command prompt, like this:

```
(.venv) matt@matt-Inspiron-15-5510:~/Documents/pyqt_groundstation$
```

2. Run `python -m src.main` on command line

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

There's also an `updateInFocus` function that only runs when you're looking at the widget.
Use this for computationally intensive stuff (like drawing a graph or rendering 3d images) so that it also doesn't run in the background.

#### QWidget_Parts
This is where custom PyQt widgets (widgets that directly extend a PyQt widget) go.

#### Helpers
This is kind of legacy structure that I don't want to fix, but the class in here handles image display, but doesn't extend a PyQt widget.
It would be better to refactor it so that it does extend QWidget or QLabel or something.

### Main Tabs
To add a custom tab, extend `main_tab_common.py` and call `self.addWidget` to add widgets to the call list.
Look at `primary_tab.py` for a nice example.
`main_tab_common.py` extends `QWidget`, so each tab object is actually a pyqt widget.
`main_tab_common` also provides framework for making sure all the Widgets get their database dictionary updated as needed.

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

- For widgets, you'll need to add the widget class to the dictionary of widget classes in the constructor.
- For modules, you'll need to add a line to main.py to register it.
- For Tabs, you'll need to add the tab class to the dictionary of tab classes in the constructor.
