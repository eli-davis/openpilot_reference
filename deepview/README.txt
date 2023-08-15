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

# opencl issue - to fix install opencl:

https://github.com/intel/compute-runtime/releases

# ____________________________________________________________ #
# ____________________________________________________________ #

# planner test:

# - lateral planner test
# - todo: longitudinal test

#  /openpilot/selfdrive/controls/plannerd.py

# INPUTS LateralPlanner(CP)
# - CP ("CarParams")
# INPUTS LongitudinalPlanner(CP)
# - CP ("CarParams")
#
# INPUTS lateral_planner.update(sm)
# - sm['controlsState'].curvature
# - sm['carState'].vEgo
# - sm['modelV2']
# - sm['carState']
# - sm['carControl'].latActive
#
# INPUTS lateral_planner.publish(sm, pm)
# - plan_send.valid = sm.all_checks(service_list=['carState', 'controlsState', 'modelV2'])
# - lateralPlan.modelMonoTime = sm.logMonoTime['modelV2']
#
# OUTPUTS lateral_planner.publish(sm, pm)
# - plan_send = messaging.new_message('lateralPlan')
#
#
#

# ____________________________________________________________ #
# ____________________________________________________________ #

# update can

# controlsd.data_sample() gets a copy of CarState (from can_strs)
# (controlsd.CI.cp.vl holds the can values)
#
# testing - save the following for each timestep:
# - can_binary.json (from can_strs)
# - can_values.json (can_values['Can_ID']['property'] //latest only)
# - car_state.json
#
# --> /openpilot/selfdrive/car/controls/controlsd.data_sample(): CS = self.CI.update(self.CC, can_strs)
#     --> controlsd.CI = /openpilot/selfdrive/car/CarInterfaceBase() // /openpilot/selfdrive.car/ford/interface.CarInterface()
#        -->  controlsd.CI.update() [called on CarInterfaceBase]
#             --> controlsd.CI.cp.update_strings(can_strings) [called from CarInterfaceBase] 
#                 --> /openpilot/opendbc/can.parser_pyx.pyx: CanParser.update_strings(can_strings)
#                     --> /openpilot/opendbc/can.parser.cc: CANParser::update_strings()
#                     [overwrites] within loop: [this happens in parser_pyx.pyx]
#                     controls.CI.cp.vl[cv.address][cv_name] = cv.value
#
#        -->  controlsd.CI._update() [called on CarInterface]
#             CS = controlsd.CI.CS.update(controld.CI.cp) [where the cp is updated with the latest can in cp.vl]
#     --> controld CS (value @ time t of controlsd.CI.CS)    
#
# CI: Car Interface
# CS: Car State
# cp: can parser

# ____________________________________________________________ #
# ____________________________________________________________ #

# controls test:

# - car_state test
# - todo: tbd

#  /openpilot/selfdrive/controls/controls.py

# INPUTS controls
# __init__()
# - num_pandas
# - experimental_long_allowed = self.params.get_bool("ExperimentalLongitudinalEnabled")
# - self.disengage_on_accelerator = self.params.get_bool("DisengageOnAccelerator")
# - self.is_metric = self.params.get_bool("IsMetric")
# - self.is_ldw_enabled = self.params.get_bool("IsLdwEnabled")
# - openpilot_enabled_toggle = self.params.get_bool("OpenpilotEnabledToggle")
# - passive = self.params.get_bool("Passive") or not openpilot_enabled_toggle
#
# step()
# - self.is_metric = self.params.get_bool("IsMetric")
# - self.experimental_mode = self.params.get_bool("ExperimentalMode") and self.CP.openpilotLongitudinalControl
#
# data_sample() 
# - self.sm.update(0)
# - sm['lateralPlan']
#
# OUTPUTS car_state
#
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

