# B"H

# ____________________________________________________________ #
# ____________________________________________________________ #

(1) Update submodules:

cd openpilot
git submodule update --init

(2) Run the setup script:

# for Ubuntu 20.04 LTS
tools/ubuntu_setup.sh

(3) Activate a shell with the Python dependencies installed:

cd openpilot
poetry shell

(4) Build openpilot with this command:

scons -u -j$(nproc)

(5) Build single module (e.g. modeld)

cd <module_path>
scons -u -j$(nproc)

# ____________________________________________________________ #
# ____________________________________________________________ #

6) replay model:

cd selfdrive/test/process_replay

python3 model_replay.py

# ____________________________________________________________ #
# ____________________________________________________________ #

4) get all logs from selfdrive/debug/dump.py

# ____________________________________________________________ #
# ____________________________________________________________ #

1) Main replay - tools/replay/replay --demo

2) can get images from tools/replay/ui.py

3) get can data from selfdrive/debug/can_printer.py

5) ford route -   ("FORD", "54827bf84c38b14f|2023-01-26--21-59-07--4"),        # FORD.BRONCO_SPORT_MK1 
# remove --4 from the end to run in replay

