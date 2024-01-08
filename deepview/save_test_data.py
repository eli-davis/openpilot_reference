# B"H

# to run, see openpilot_reference/selfdrive/test/process_replay (fordtest.py/process_replay.py)

import os
import time

from termcolor import cprint as print_in_color

import json


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

    # _________________________________________________________________ #
    # _________________________________________________________________ #

    print_in_color(f"[save_control_inputs] i={iteration_i:04}", "yellow")

    # _________________________________________________________________ #
    # _________________________________________________________________ #

    INPUTS_DATA_DIR_PATH = "/home/deepview/SSD/pathfinder/src/unit_tests/test_data/can/inputs"

    # for each timestep 0-5999:
    # - save can values / car state
    #
    # (60 second segment // 100 controlsd steps per second)

    dir_name = f"{iteration_i:04}"  # 4 digits, zero-padded
    dir_path = os.path.join(INPUTS_DATA_DIR_PATH, dir_name)
    os.makedirs(dir_path, exist_ok=True)

    '''
    if hasattr(liveParameters, 'to_dict') and callable(getattr(liveParameters, 'to_dict')):
        # The object has a to_dict() method
        print("liveParameters has a to_dict() method")

    print_in_color(f"[controlsd.state_control] type(livePameters)={type(liveParameters)}", "red")
    print_in_color(f"[controlsd.state_control] livePameters={liveParameters}", "green")

    print_in_color(f"[controlsd.state_control] type(liveLocationKalman)={type(liveLocationKalman)}", "red")
    print_in_color(f"[controlsd.state_control] liveLocationKalman={liveLocationKalman}", "green")

    print_in_color(f"[controlsd.state_control] type(save_CarParams)={type(save_CarParams)}", "red")
    print_in_color(f"[controlsd.state_control] save_CarParams={save_CarParams}", "green")

    print_in_color(f"[controlsd.state_control] type(can_controller_dbc_name)={type(can_controller_dbc_name)}", "red")
    print_in_color(f"[controlsd.state_control] can_controller_dbc_name={can_controller_dbc_name}", "green")

    print_in_color(f"[controlsd.state_control] type(last_actuators)={type(last_actuators)}", "red")
    print_in_color(f"[controlsd.state_control] last_actuators={last_actuators}", "green")

    print_in_color(f"[controlsd.state_control] type(steer_limited)={type(steer_limited)}", "red")
    print_in_color(f"[controlsd.state_control] steer_limited={steer_limited}", "green")

    print_in_color(f"[controlsd.state_control] type(desired_curvature)={type(desired_curvature)}", "red")
    print_in_color(f"[controlsd.state_control] desired_curvature={desired_curvature}", "green")

    print_in_color(f"[controlsd.state_control] type(desired_curvature_rate)={type(desired_curvature_rate)}", "red")
    print_in_color(f"[controlsd.state_control] desired_curvature_rate={desired_curvature_rate}", "green")
    '''

    control_inputs_dict = dict()

    control_inputs_dict['liveParameters']               = liveParameters.to_dict()
    control_inputs_dict['liveLocationKalman']           = liveLocationKalman.to_dict()
    CarParams_dict                                      = save_CarParams.to_dict()
    control_inputs_dict['last_actuators']               = last_actuators.to_dict()
    control_inputs_dict['bool_steer_limited']           = steer_limited
    control_inputs_dict['can_controller_dbc_name']      = can_controller_dbc_name.decode('utf-8') # bytes_object to str
    control_inputs_dict['float_desired_curvature']      = desired_curvature
    control_inputs_dict['float_desired_curvature_rate'] = desired_curvature_rate


    control_inputs_json_path = os.path.join(dir_path, "control_inputs.json")
    with open(control_inputs_json_path, "w") as FILE:
        json.dump(control_inputs_dict, FILE, indent=4)


    # list of ECUs. workaround, set to None to avoid bytes object to json
    CarParams_dict['carFw']=None
    #
    CarParams_json_path = os.path.join(dir_path, "CarParams.json")
    with open(CarParams_json_path, "w") as FILE:
        json.dump(CarParams_dict, FILE, indent=4)





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

    # _________________________________________________________________ #
    # _________________________________________________________________ #

    print_in_color(f"[save_control_outputs] i={iteration_i:04}", "cyan")

    # _________________________________________________________________ #
    # _________________________________________________________________ #

    OUTPUTS_DATA_DIR_PATH = "/home/deepview/SSD/pathfinder/src/unit_tests/test_data/can/outputs"

    # for each timestep 0-5999:
    # - save can values / car state
    #
    # (60 second segment // 100 controlsd steps per second)

    dir_name = f"{iteration_i:04}"  # 4 digits, zero-padded
    dir_path = os.path.join(OUTPUTS_DATA_DIR_PATH, dir_name)
    os.makedirs(dir_path, exist_ok=True)

    '''
    print_in_color(f"[controlsd.state_control] type(save_CarControl)={type(save_CarControl)}", "red")
    print_in_color(f"[controlsd.state_control] save_CarControl={save_CarControl}", "green")

    print_in_color(f"[controlsd.state_control] type(can_sends)={type(can_sends)}", "red")
    print_in_color(f"[controlsd.state_control] can_sends={can_sends}", "green")

    print_in_color(f"[controlsd.state_control] type(lac_log)={type(lac_log)}", "red")
    print_in_color(f"[controlsd.state_control] lac_log={lac_log}", "green")

    print_in_color(f"[controlsd.state_control] type(last_actuators)={type(last_actuators)}", "red")
    print_in_color(f"[controlsd.state_control] last_actuators={last_actuators}", "green")

    print_in_color(f"[controlsd.state_control] type(steer_limited)={type(steer_limited)}", "red")
    print_in_color(f"[controlsd.state_control] steer_limited={steer_limited}", "green")

    '''

    # can_data: bytes_object to hex
    hex_can_sends = []
    for (arg1, arg2, bytes_object, arg4) in can_sends:
        #print(f"    bytes_object={bytes_object}")
        #print(f"    bytes_object.hex={bytes_object.hex()}")
        hex_can_sends.append([arg1, arg2, bytes_object.hex(), arg4])

    control_outputs_dict = dict()

    CarControl_dict                            = save_CarControl.to_dict()
    control_outputs_dict['can_sends']          = hex_can_sends
    control_outputs_dict['lac_log']            = lac_log.to_dict()
    control_outputs_dict['last_actuators']     = last_actuators.to_dict()
    control_outputs_dict['bool_steer_limited'] = steer_limited


    control_outputs_json_path = os.path.join(dir_path, "control_outputs.json")
    with open(control_outputs_json_path, "w") as FILE:
        json.dump(control_outputs_dict, FILE, indent=4)

    CarControl_json_path = os.path.join(dir_path, "CarControl.json")
    with open(CarControl_json_path, "w") as FILE:
        json.dump(CarControl_dict, FILE, indent=4)

