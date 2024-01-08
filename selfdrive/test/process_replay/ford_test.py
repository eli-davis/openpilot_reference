# B"H

# based on /openpilot/selfdrive/test/process_replay/test_processes.py

import argparse
import concurrent.futures
import os
import sys
from collections import defaultdict

from typing import Any, DefaultDict, Dict

from selfdrive.car.car_helpers import interface_names
from selfdrive.test.openpilotci import get_url, upload_file
from selfdrive.test.process_replay.compare_logs import compare_logs
from selfdrive.test.process_replay.process_replay import ProcessConfig, get_car_params_callback, FrequencyBasedRcvCallback, NUMPY_TOLERANCE, PROC_REPLAY_DIR
from selfdrive.test.process_replay.process_replay import controlsd_config_callback, controlsd_fingerprint_callback, controlsd_rcv_callback
from selfdrive.test.process_replay.process_replay import check_openpilot_enabled, replay_process
from system.version import get_commit
from tools.lib.filereader import FileReader
from tools.lib.logreader import LogReader
from tools.lib.helpers import save_log

# ___________________________________________________________ #
# ___________________________________________________________ #

from termcolor import cprint as print_in_color
# ___________________________________________________________ #
# ___________________________________________________________ #


EXCLUDED_PROCS = {"modeld", "dmonitoringmodeld"}


def test_process(cfg, lr, segment, ref_log_path):

  ignore_fields = []
  ignore_msgs = []

  ref_log_msgs = list(LogReader(ref_log_path))

  try:
    log_msgs = replay_process(cfg, lr, disable_progress=True)
  except Exception as e:
    raise Exception("failed on segment: " + segment) from e

  # check to make sure openpilot is engaged in the route
  if cfg.proc_name == "controlsd":
    if not check_openpilot_enabled(log_msgs):
      return f"Route did not enable at all or for long enough: ", log_msgs

  try:
    return compare_logs(ref_log_msgs, log_msgs, ignore_fields + cfg.ignore, ignore_msgs, cfg.tolerance, cfg.field_tolerances), log_msgs
  except Exception as e:
    return str(e), log_msgs



def get_log_data(segment):
  r, n = segment.rsplit("--", 1)
  with FileReader(get_url(r, n)) as f:
    return (segment, f.read())




def format_diff(results, log_paths, ref_commit):
  diff1, diff2 = "", ""
  diff2 += f"***** tested against commit {ref_commit} *****\n"

  failed = False
  for segment, result in list(results.items()):
    diff1 += f"***** results for segment {segment} *****\n"
    diff2 += f"***** differences for segment {segment} *****\n"

    for proc, diff in list(result.items()):
      # long diff
      diff2 += f"*** process: {proc} ***\n"
      diff2 += f"\tref: {log_paths[segment][proc]['ref']}\n"
      diff2 += f"\tnew: {log_paths[segment][proc]['new']}\n\n"

      # short diff
      diff1 += f"    {proc}\n"
      if isinstance(diff, str):
        diff1 += f"        ref: {log_paths[segment][proc]['ref']}\n"
        diff1 += f"        new: {log_paths[segment][proc]['new']}\n\n"
        diff1 += f"        {diff}\n"
        failed = True
      elif len(diff):
        diff1 += f"        ref: {log_paths[segment][proc]['ref']}\n"
        diff1 += f"        new: {log_paths[segment][proc]['new']}\n\n"

        cnt: Dict[str, int] = {}
        for d in diff:
          diff2 += f"\t{str(d)}\n"

          k = str(d[1])
          cnt[k] = 1 if k not in cnt else cnt[k] + 1

        for k, v in sorted(cnt.items()):
          diff1 += f"        {k}: {v}\n"
        failed = True
  return diff1, diff2, failed





def run_test():

    # FORD
    source_segment = "54827bf84c38b14f|2023-01-26--21-59-07--4" # FORD.BRONCO_SPORT_MK1

    # FORD
    segment = "aregenDDE0F89FA1E|2023-05-10--14-59-26--0"


    '''
    CONFIGS = []
    '''

    cfg = ProcessConfig(
        proc_name="controlsd",
        pubs=[
          "can", "deviceState", "pandaStates", "peripheralState", "liveCalibration", "driverMonitoringState",
          "longitudinalPlan", "lateralPlan", "liveLocationKalman", "liveParameters", "radarState",
          "modelV2", "driverCameraState", "roadCameraState", "wideRoadCameraState", "managerState",
          "testJoystick", "liveTorqueParameters"
        ],
        subs=["controlsState", "carState", "carControl", "sendcan", "carEvents", "carParams"],
        ignore=["logMonoTime", "valid", "controlsState.startMonoTime", "controlsState.cumLagMs"],
        config_callback=controlsd_config_callback,
        init_callback=controlsd_fingerprint_callback,
        should_recv_callback=controlsd_rcv_callback,
        tolerance=NUMPY_TOLERANCE,
        processing_time=0.004,
        main_pub="can",
    )

    '''
    CONFIGS.append(
      ProcessConfig(
        proc_name="radard",
          pubs=["can", "carState", "modelV2"],
          subs=["radarState", "liveTracks"],
          ignore=["logMonoTime", "valid", "radarState.cumLagMs"],
          init_callback=get_car_params_callback,
          should_recv_callback=MessageBasedRcvCallback("modelV2"),
          unlocked_pubs=["can"],
      )
    )
    '''

    cfg1 = ProcessConfig(
              proc_name="plannerd",
              pubs=["modelV2", "carControl", "carState", "controlsState", "radarState"],
              subs=["lateralPlan", "longitudinalPlan", "uiPlan"],
              ignore=["logMonoTime", "valid", "longitudinalPlan.processingDelay", "longitudinalPlan.solverExecutionTime", "lateralPlan.solverExecutionTime"],
              init_callback=get_car_params_callback,
              should_recv_callback=FrequencyBasedRcvCallback("modelV2"),
              tolerance=NUMPY_TOLERANCE,
          )

    '''
    CONFIGS.append(
      ProcessConfig(
        proc_name="calibrationd",
        pubs=["carState", "cameraOdometry", "carParams"],
        subs=["liveCalibration"],
        ignore=["logMonoTime", "valid"],
        should_recv_callback=calibration_rcv_callback,
      )
    )

    CONFIGS.append(
      ProcessConfig(
        proc_name="dmonitoringd",
        pubs=["driverStateV2", "liveCalibration", "carState", "modelV2", "controlsState"],
        subs=["driverMonitoringState"],
        ignore=["logMonoTime", "valid"],
        should_recv_callback=FrequencyBasedRcvCallback("driverStateV2"),
        tolerance=NUMPY_TOLERANCE,
      )
    )

    CONFIGS.append(
      ProcessConfig(
        proc_name="locationd",
        pubs=[
          "cameraOdometry", "accelerometer", "gyroscope", "gpsLocationExternal",
          "liveCalibration", "carState", "carParams", "gpsLocation"
        ],
        subs=["liveLocationKalman"],
        ignore=["logMonoTime", "valid"],
        config_callback=locationd_config_pubsub_callback,
        tolerance=NUMPY_TOLERANCE,
      )

    )

    CONFIGS.append(
      ProcessConfig(
        proc_name="paramsd",
        pubs=["liveLocationKalman", "carState"],
        subs=["liveParameters"],
        ignore=["logMonoTime", "valid"],
        init_callback=get_car_params_callback,
        should_recv_callback=FrequencyBasedRcvCallback("liveLocationKalman"),
        tolerance=NUMPY_TOLERANCE,
        processing_time=0.004,
      )
    )

    CONFIGS.append(
      ProcessConfig(
        proc_name="ubloxd",
        pubs=["ubloxRaw"],
        subs=["ubloxGnss", "gpsLocationExternal"],
        ignore=["logMonoTime"],
      )
    )

    CONFIGS.append(
      ProcessConfig(
        proc_name="laikad",
        pubs=["ubloxGnss", "qcomGnss"],
        subs=["gnssMeasurements"],
        ignore=["logMonoTime"],
        config_callback=laikad_config_pubsub_callback,
        tolerance=NUMPY_TOLERANCE,
        processing_time=0.002,
        timeout=60*10,  # first messages are blocked on internet assistance
        main_pub="ubloxGnss", # config_callback will switch this to qcom if needed
      )
    )

    CONFIGS.append(
      ProcessConfig(
        proc_name="torqued",
        pubs=["liveLocationKalman", "carState", "carControl"],
        subs=["liveTorqueParameters"],
        ignore=["logMonoTime"],
        init_callback=get_car_params_callback,
        should_recv_callback=torqued_rcv_callback,
        tolerance=NUMPY_TOLERANCE,
      )
    )

    CONFIGS.append(
      ProcessConfig(
        proc_name="modeld",
        pubs=["lateralPlan", "roadCameraState", "wideRoadCameraState", "liveCalibration", "driverMonitoringState"],
        subs=["modelV2", "cameraOdometry"],
        ignore=["logMonoTime", "modelV2.frameDropPerc", "modelV2.modelExecutionTime"],
        should_recv_callback=ModeldCameraSyncRcvCallback(),
        tolerance=NUMPY_TOLERANCE,
        processing_time=0.020,
        main_pub=vipc_get_endpoint_name("camerad", meta_from_camera_state("roadCameraState").stream),
        main_pub_drained=False,
        vision_pubs=["roadCameraState", "wideRoadCameraState"],
        ignore_alive_pubs=["wideRoadCameraState"],
      )
    )

    CONFIGS.append(
      ProcessConfig(
        proc_name="dmonitoringmodeld",
        pubs=["liveCalibration", "driverCameraState"],
        subs=["driverStateV2"],
        ignore=["logMonoTime", "driverStateV2.modelExecutionTime", "driverStateV2.dspExecutionTime"],
        should_recv_callback=dmonitoringmodeld_rcv_callback,
        tolerance=NUMPY_TOLERANCE,
        processing_time=0.020,
        main_pub=vipc_get_endpoint_name("camerad", meta_from_camera_state("driverCameraState").stream),
        main_pub_drained=False,
        vision_pubs=["driverCameraState"],
        ignore_alive_pubs=["driverCameraState"],
      )
    )
    '''

    _, lr_dat = get_log_data(segment)

    lr = LogReader.from_bytes(lr_dat)


    # "new" commit - tested against "cur" commit
    # - a bit unclear, they're testing against cur commit which seems to be last tested logs
    #REFERENCE_COMMIT_PATH = os.path.join(PROC_REPLAY_DIR, "ref_commit")
    #ref_commit = open(REFERENCE_COMMIT_PATH).read().strip()

    # updated daily? seems to call github
    #cur_commit = get_commit()

    cur_commit = "bc5c38bbd833316331d32c0eeb8048c56040bd2f"
    print(cur_commit)

    REFERENCE_DATA_PATH = os.path.join(PROC_REPLAY_DIR, "fakedata/")
    ref_log_path = os.path.join(REFERENCE_DATA_PATH, f"{segment}_{cfg.proc_name}_{cur_commit}.bz2")

    res, log_msgs = test_process(cfg, lr, segment, ref_log_path)

    keys = set()
    for m in log_msgs:
        keys.add(m.which())

    #print(log_msgs[0])
    #print(log_msgs[-1])

    print_in_color(f"keys={keys}", "red")
    print_in_color(f"len(log_msgs)={len(log_msgs)}", "red")

    print_in_color("___________________", "yellow")
    print_in_color(f"segment={segment}", "yellow")
    print_in_color(f"cfg.proc_name={cfg.proc_name}", "yellow")
    print_in_color(f"res={res}", "yellow")
    print_in_color("___________________", "yellow")



if __name__ == "__main__":

    run_test()
