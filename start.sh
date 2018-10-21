#!/bin/bash

# TODO: persistant hw_id/dev_name relation
# ls /dev/input/by-id/usb-413d_2107-mouse
# sudo apt install -y \
#     git python3-venv \
#     libopenjp2-7 libopenjp2-7-dev libopenjp2-tools

# pip install -r requirements.txt
# @NSloloulol: qu'as-tu installé cet après-midi ?

cd /home/pi/ScaleRFID
[ "_$VIRTUAL_ENV" == "_" ]  && \
  echo -n 'Activating virtual environment' && \
  source venv/bin/activate && echo 'Done.'

mkdir -p log

echo Script incoming

# sleep 5
sudo venv/bin/python3 Pesee_Rework.py &
sudo venv/bin/python3 Killswitch.py < $(cat /dev/input/by-id/usb-413d_2107-mouse | od -x)
# save lock.$$
# kill -USR1 $(cat lock.$$)
