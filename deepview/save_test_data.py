# B"H

# to run, see openpilot_reference/selfdrive/test/process_replay (fordtest.py/process_replay.py)

import os
import time

from termcolor import cprint as print_in_color


# @ prior_to_return of openpilot/selfdrive/controls/controlsd.state_control()
#
'''
    # ________________________________________________________________________ #
    # ________________________________________________________________________ #

    # @ prior_to_return of controlsd.state_control()
    save_test_data.save_control_inputs(self.sm['liveParameters'],
                                       self.sm['liveLocationKalman'],
                                       self.CP,
                                       self.last_actuators,
                                       self.steer_limited,
                                       self.CI.cp.dbc_name,
                                       self.desired_curvature,
                                       self.desired_curvature_rate,
                                       iteration_i)

    # ________________________________________________________________________ #
    # ________________________________________________________________________ #
'''
#
def save_control_inputs(liveParameters, liveLocationKalman, save_CarParams, last_actuators, steer_limited, can_controller_dbc_name, desired_curvature, desired_curvature_rate, iteration_i):
    print_in_color(f"[save_control_inputs] i={iteration_i:04}", "yellow")

    # controlsd.last_actuators, controlsd.steer_limited, controlsd.CI.CC.dbc_name (state_control - intermediate outputs: controlsd.desired_curvature, controlsd.desired_curvature_rate)

    '''
    # save_test_data

    # - self.sm['liveParameters']
    # - self.sm['liveLocationKalman']

    INPUTS_DATA_DIR_PATH = "/home/deepview/SSD/pathfinder/src/unit_tests/test_data/can/outputs"

    # for each timestep 0-5999:
    # - save can values / car state
    #
    # (60 second segment // 100 controlsd steps per second)

    dir_name = f"{iteration_i:04}"  # 4 digits, zero-padded
    dir_path = os.path.join(INPUTS_DATA_DIR_PATH, dir_name)
    os.makedirs(dir_path, exist_ok=True)

    print_in_color(f"[controlsd.state_control] type(livePameters)={type(self.sm['liveParameters'])}", "red")
    print_in_color(f"[controlsd.state_control] livePameters={self.sm['liveParameters']}", "green")

    print_in_color(f"[controlsd.state_control] type(liveLocationKalman)={type(self.sm['liveLocationKalman'])}", "red")
    print_in_color(f"[controlsd.state_control] liveLocationKalman={self.sm['liveLocationKalman']}", "green")
    '''

    '''
    vehicle_can_dict = {k: v for k, v in self.CI.cp.vl.items() if v}
    vehicle_can_json_path = os.path.join(dir_path, "vehicle_can.json")
    with open(vehicle_can_json_path, "w") as FILE:
        json.dump(vehicle_can_dict, FILE, indent=4)
    '''


# @ prior_to_return of openpilot/selfdrive/controls/controlsd.publish_logs()
#
'''
    # ________________________________________________________________________ #
    # ________________________________________________________________________ #

    # @ prior_to_return of controlsd.publish_logs()
    if 'can_sends' not in locals():
        can_sends = []
    save_test_data.save_control_outputs(self.CC, can_sends, lac_log, self.last_actuators, self.steer_limited, iteration_i)

    # ________________________________________________________________________ #
    # ________________________________________________________________________ #
'''
#
def save_control_outputs(save_CarControl, can_sends, lac_log, last_actuators, steer_limited, iteration_i):
    print_in_color(f"[save_control_outputs] i={iteration_i:04}", "cyan")


    # save_test_data

    '''
    OUTPUTS_DATA_DIR_PATH = "/home/deepview/SSD/pathfinder/src/unit_tests/test_data/can/outputs"

    # for each timestep 0-5999:
    # - save can values / car state
    #
    # (60 second segment // 100 controlsd steps per second)

    dir_name = f"{iteration_i:04}"  # 4 digits, zero-padded
    dir_path = os.path.join(OUTPUTS_DATA_DIR_PATH, dir_name)
    os.makedirs(dir_path, exist_ok=True)
    '''
