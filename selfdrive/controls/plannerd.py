#!/usr/bin/env python3
import os
import numpy as np
from cereal import car
from common.params import Params
from common.realtime import Priority, config_realtime_process
from system.swaglog import cloudlog
from selfdrive.modeld.constants import T_IDXS
from selfdrive.controls.lib.longitudinal_planner import LongitudinalPlanner
from selfdrive.controls.lib.lateral_planner import LateralPlanner
import cereal.messaging as messaging

import json
import signal
from termcolor import cprint as print_in_color

def cumtrapz(x, t):
  return np.concatenate([[0], np.cumsum(((x[0:-1] + x[1:])/2) * np.diff(t))])

def publish_ui_plan(sm, pm, lateral_planner, longitudinal_planner):
  plan_odo = cumtrapz(longitudinal_planner.v_desired_trajectory_full, T_IDXS)
  model_odo = cumtrapz(lateral_planner.v_plan, T_IDXS)

  ui_send = messaging.new_message('uiPlan')
  ui_send.valid = sm.all_checks(service_list=['carState', 'controlsState', 'modelV2'])
  uiPlan = ui_send.uiPlan
  uiPlan.frameId = sm['modelV2'].frameId
  uiPlan.position.x = np.interp(plan_odo, model_odo, lateral_planner.lat_mpc.x_sol[:,0]).tolist()
  uiPlan.position.y = np.interp(plan_odo, model_odo, lateral_planner.lat_mpc.x_sol[:,1]).tolist()
  uiPlan.position.z = np.interp(plan_odo, model_odo, lateral_planner.path_xyz[:,2]).tolist()
  uiPlan.accel = longitudinal_planner.a_desired_trajectory_full.tolist()
  pm.send('uiPlan', ui_send)

def plannerd_thread(sm=None, pm=None):
  config_realtime_process(5, Priority.CTRL_LOW)

  cloudlog.info("plannerd is waiting for CarParams")
  params = Params()
  with car.CarParams.from_bytes(params.get("CarParams", block=True)) as msg:
    CP = msg
  cloudlog.info("plannerd got CarParams: %s", CP.carName)

  debug_mode = bool(int(os.getenv("DEBUG", "0")))

  longitudinal_planner = LongitudinalPlanner(CP)
  lateral_planner = LateralPlanner(CP, debug=debug_mode)

  if sm is None:
    sm = messaging.SubMaster(['carControl', 'carState', 'controlsState', 'radarState', 'modelV2'],
                             poll=['radarState', 'modelV2'], ignore_avg_freq=['radarState'])

  if pm is None:
    pm = messaging.PubMaster(['longitudinalPlan', 'lateralPlan', 'uiPlan'])


  iteration_i = 0
  CarParams_dict = CP.to_dict()
  CarParams_dict.pop("carFw", None)
  with open('/home/deepview/SSD/pathfinder/src/planner/test/CP.json', 'w') as FILE:
    json.dump({'CP': CarParams_dict}, FILE, indent=4)

  while True:
    sm.update()

    if sm.updated['modelV2']:

      #
      # save inputs
      #
      #print(f"[{iteration_i:04}]plannerd thread!")
      car_state      = sm['carState'].to_dict()
      controls_state = sm['controlsState'].to_dict()
      modelV2        = sm['modelV2'].to_dict()
      bool_lateral_control_active = sm['carControl'].latActive
      input_values_dict = {
        'car_state': car_state,
        'controls_state': controls_state,
        'modelV2': modelV2,
        'bool_lateral_control_active': bool_lateral_control_active
      }
      with open(f'/home/deepview/SSD/pathfinder/src/planner/test/inputs/{iteration_i:04}.json', 'w') as FILE:
        json.dump(input_values_dict, FILE, indent=4)

      # plannerd loop
      lateral_planner.update(sm)
      lateral_plan = lateral_planner.publish(sm, pm)
      longitudinal_planner.update(sm)
      longitudinal_planner.publish(sm, pm)
      publish_ui_plan(sm, pm, lateral_planner, longitudinal_planner)

      #
      # save outputs
      #
      lateral_plan_dict = lateral_plan.as_reader().to_dict()
      output_values_dict = {
        'lateral_plan': lateral_plan_dict,
      }
      with open(f'/home/deepview/SSD/pathfinder/src/planner/test/outputs/{iteration_i:04}.json', 'w') as FILE:
        json.dump(output_values_dict, FILE, indent=4)
      iteration_i += 1


def main(sm=None, pm=None):
  plannerd_thread(sm, pm)


if __name__ == "__main__":
  main()
