# meross-powermon
Simple command line interface for local operation of Meross IoT kit

Requires MerossIot to be installed.

Incorporates iwlist.py from https://github.com/iancoleman/python-iwlist as I couldn't figure out how to include it without running into problems when trying to package this stuff up so it was suitable for "pip install".

You have to be root to run all of the wifi commands to connect to Meross device. This assumes that root will only run the "setup" phase for each device and that a user, will run everything else.

To initialise local config files:

For root:

Specify who the lucky user is, give your normal wifi network details and the interface of the wifi device:

`./meross init --user USER --ssid SSID --password PASSWORD --interface IF`


For the user:

Give the name of the mqtt server, port number and path to certificate file if required:

`./meross init --server SERVER --port PORT --ca-cert /path/to/ca.crt`

In both cases the configuration is stored in .config/meross_powermon/config.json relative to the home directory and has a "chmod 600" performed on it.

Once that's done you don't need to think about those options, you can change them with a `config` sub-command though.

To add a device (as root):

`./meross setup name`

Will bring up the wifi device and scan for an AP name starting with "Meross_"

We then associate with the Meross_* network

Next we configure the wifi network with an appropriate IP address and route and gather some device data (which we'll store later). Then it's a case of giving the device details of the MQTT server to use and the ssid and password for our normal wifi network.

Finally the device data is stored in the named user's config file using the name given in the setup command.

Our user can then run a simple monitor to test that it's working:

`./meross monitor name`

Root can overwrite an existing device name by using `--force` with the `setup` command or the user can delete a device using a `delete` sub-command.