# B"H

import os
import time

from termcolor import cprint as print_in_color

from tools.lib.framereader import FrameReader
from tools.lib.logreader import LogReader
from tools.lib.filereader import FileReader
from selfdrive.test.process_replay.migration import migrate_all

from selfdrive.test.openpilotci import get_url


# ______________________________________________________________________________ #
# ______________________________________________________________________________ #

from pprint import pprint
from io import StringIO

def pprint_dict(msg, dict, color="yellow"):
    str_output = StringIO()
    pprint(dict, stream=str_output, width=1)
    formatted_output = "\n"+str_output.getvalue()
    print_in_color(f"{msg}={formatted_output}", color)

# ______________________________________________________________________________ #
# ______________________________________________________________________________ #

def print_delta_t(start_time, msg, color="yellow"):
    # Convert to milliseconds
    delta_t = (time.time() - start_time) * 1000
    print_in_color(f"[test2.py] {msg}: {delta_t:.1f} ms", color)

# ______________________________________________________________________________ #
# ______________________________________________________________________________ #


def get_log_data(segment):
    r, n = segment.rsplit("--", 1)
    with FileReader(get_url(r, n)) as f:
        return (segment, f.read())





def run_test():

    # FORD
    source_segment = "54827bf84c38b14f|2023-01-26--21-59-07--4" # FORD.BRONCO_SPORT_MK1

    # FORD
    #### segment = "aregenDDE0F89FA1E|2023-05-10--14-59-26--0"

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
    t0 = time.time()

    _, lr_dat = get_log_data(source_segment)

    lr = LogReader.from_bytes(lr_dat)

    # based on openpilot/selfdrive/test/process_replay/process_replay.replay_process()
    all_msgs = migrate_all(lr, old_logtime=True, camera_states=True)
    all_msgs = sorted(all_msgs, key=lambda msg: msg.logMonoTime)

    ####
    ####
    unique_values = set()

    for m in all_msgs:
        unique_values.add(m.which())

    print("Unique values from m.which():", unique_values)
    ####
    ####

    processes_to_log = ['carParams',

                        #'cameraOdometry',
                        'liveParameters',
                        'liveCalibration',
                        'liveLocationKalman',

                        'CarState',
                        'carControl',

                        'sendcan',
                        'can',

                        'lateralPlan',
                        'modelV2']

    #print(f"len(all_msgs)={len(all_msgs)}")

    new_logs = [msg for msg in all_msgs if msg.which() in processes_to_log]

    print(f"len(new_logs)={len(new_logs)}")

    for process_type in processes_to_log:
        matching_logs = [msg for msg in new_logs if msg.which() == process_type]
        if matching_logs:
            first_log = matching_logs[0]
            ###pprint_dict(f"{process_type} - Type: {type(first_log)}", first_log.to_dict())

            keys_only = list(first_log.to_dict().keys())
            #print(f"{process_type} - Type: {type(first_log)}")
            print(f"{process_type} Keys:", keys_only)

        else:
            print(f"No logs found for {process_type}")


    ####
    _carParams       = [m for m in lr if m.which() == "carParams"]

    _liveParameters  = [m for m in lr if m.which() == "liveParameters"]
    _liveCalibration = [m for m in lr if m.which() == "liveCalibration"]
    _liveLocationKalman = [m for m in lr if m.which() == "liveLocationKalman"]

    _CarState   = [m for m in lr if m.which() == "CarState"]
    _CarControl = [m for m in lr if m.which() == "CarControl"]

    _sendcan = [m for m in lr if m.which() == "sendcan"]
    _can     = [m for m in lr if m.which() == "can"]

    _lateralPlan = [m for m in lr if m.which() == "lateralPlan"]
    _modelV2 = [m for m in lr if m.which() == "modelV2"]

    print("Length of _carParams:", len(_carParams))
    print("Length of _liveParameters:", len(_liveParameters))
    print("Length of _liveCalibration:", len(_liveCalibration))
    print("Length of _liveLocationKalman:", len(_liveLocationKalman))
    print("Length of _CarState:", len(_CarState))
    print("Length of _CarControl:", len(_CarControl))
    print("Length of _sendcan:", len(_sendcan))
    print("Length of _can:", len(_can))
    print("Length of _lateralPlan:", len(_lateralPlan))
    print("Length of _modelV2:", len(_modelV2))



    ####



    #print(f"type(all_msgs[0])={type( all_msgs[0] )}")

    ####pprint_dict(f"all_msgs[0].to_dict()", all_msgs[0].to_dict())



    print_delta_t(t0, "get logs")
    #print(lr)

    os._exit(0)

    _TEST_ROUTE, _SEGMENT = source_segment.rsplit("--", 1)
    print_in_color(f"TEST_ROUTE={_TEST_ROUTE} _SEGMENT={_SEGMENT}", "cyan")
    frs = {
      'roadCameraState': FrameReader(get_url(_TEST_ROUTE, _SEGMENT, log_type="fcamera"), readahead=True),
      #'driverCameraState': FrameReader(get_url(_TEST_ROUTE, _SEGMENT, log_type="dcamera"), readahead=True),
      'wideRoadCameraState': FrameReader(get_url(_TEST_ROUTE, _SEGMENT, log_type="ecamera"), readahead=True)
    }




if __name__ == "__main__":

    run_test()

