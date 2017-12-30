# trellis-mpc

Control *forked-daapd* with the Adafruit UNTZtrument!

## Installation

Install pip3 and numpy

```
sudo apt-get install python3-pip python3-numpy
```


Install python-mpd2 (with support for the `outputvolume` command)

```
git clone https://github.com/chme/python-mpd2.git
cd python-mpd2
git checkout outputvolume
sudo python3 setup.py install
```

Install the Adafruit gpio and trellis python libraries

```
sudo pip3 install adafruit-gpio
git clone https://github.com/chme/Adafruit_Trellis_Python.git
cd Adafruit_Trellis_Python
sudo python3 setup.py install
```

Install trellis-mpc

```
git clone https://github.com/chme/trellis-mpc.git
```

Create fifo

```
mkfifo vizualizer.fifo
sudo chown daapd:daapd vizualizer.fifo
```

Configure trellis-mpc

```
cd trellis-mpc
cp ./trellis_mpc/config_template.py ./trellis_mpc/config.py
```

Set `VIZ_FIFOPATH` to the created fifo. Add fifo configuration to `/etc/forked-daapd.conf`.

Optionally enable systemd service for trellis-mpc

```
sudo cp ./scripts/trellismpc.service /etc/systemd/system
sudo systemctl enable trellismpc.service
```