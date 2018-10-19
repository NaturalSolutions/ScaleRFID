#!/bin/bash
cd /home/pi/Desktop/ProjetRFID_Rework
[ "_$VIRTUAL_ENV" == "_" ]  && \
  echo 'Activating virtual environment' && \
  source venv/bin/activate

mkdir -p log

echo Script incoming

# sleep 5
sudo venv/bin/python3 Pesee_Rework.py &
# save lock.$$
sudo venv/bin/python3 Killswitch.py
# kill -USR1 $(cat lock.$$)

# sudo apt install -y \
#     libopenjp2-7 libopenjp2-7-dev libopenjp2-tools
