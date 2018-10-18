#!/bin/bash

cd /home/pi/Desktop/ProjetRFID_Rework

echo Script incoming

# sleep 5

# (lxterminal -e sudo python3 Pesee_Rework.py) &
sudo python3 Pesee_Rework.py&
# save lock.$$
sudo python3 Killswitch.py
# kill -USR1 $(cat lock.$$)
