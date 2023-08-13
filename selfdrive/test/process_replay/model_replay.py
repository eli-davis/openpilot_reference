#!/usr/bin/env python3
import os
import sys
import time
from collections import defaultdict
from typing import Any

import cereal.messaging as messaging
from common.params import Params
from common.spinner import Spinner
from system.hardware import PC
from selfdrive.manager.process_config import managed_processes
from selfdrive.test.openpilotci import BASE_URL, get_url
from selfdrive.test.process_replay.compare_logs import compare_logs
from selfdrive.test.process_replay.test_processes import format_diff
from selfdrive.test.process_replay.process_replay import get_process_config, replay_process
from system.version import get_commit
from tools.lib.framereader import FrameReader
from tools.lib.logreader import LogReader
from tools.lib.helpers import save_log

# ____
# ____

#sys.path.append("/home/deepview/SSD/pathfinder/src")
#sys.path.insert(0, "/home/deepview/SSD/pathfinder/src/utils/transformations")
#from control import mode, ControlStateMachine


from termcolor import cprint as print_in_color
import numpy as np
import cv2

from pycuda import driver as cuda

def img_to_rgb(yuv_img_raw):
  imgff = np.frombuffer(yuv_img_raw.data, dtype=np.uint8).reshape((1208 * 3 // 2, 1928))
  num_px = 1208 * 1928
  rgb = cv2.cvtColor(imgff, cv2.COLOR_YUV2RGB_NV12)
  return rgb
  #bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
  #return bgr

# ____
# ____

TEST_ROUTE = "4cf7a6ad03080c90|2021-09-29--13-46-36"
SEGMENT = 0
MAX_FRAMES = 5
NAV_FRAMES = 0

NO_NAV = True
SEND_EXTRA_INPUTS = bool(int(os.getenv("SEND_EXTRA_INPUTS", "0")))

print(f'{NO_NAV=} , {SEND_EXTRA_INPUTS=}')

def get_log_fn(ref_commit, test_route):
  return f"{test_route}_model_tici_{ref_commit}.bz2"


def trim_logs_to_max_frames(logs, max_frames, frs_types, include_all_types):
  all_msgs = []
  cam_state_counts = defaultdict(int)
  # keep adding messages until cam states are equal to MAX_FRAMES
  for msg in sorted(logs, key=lambda m: m.logMonoTime):
    all_msgs.append(msg)
    if msg.which() in frs_types:
      cam_state_counts[msg.which()] += 1

    if all(cam_state_counts[state] == max_frames for state in frs_types):
      break

  if len(include_all_types) != 0:
    other_msgs = [m for m in logs if m.which() in include_all_types]
    all_msgs.extend(other_msgs)

  return all_msgs


def nav_model_replay(lr):
  sm = messaging.SubMaster(['navModel', 'navThumbnail', 'mapRenderState'])
  pm = messaging.PubMaster(['liveLocationKalman', 'navRoute'])

  nav = [m for m in lr if m.which() == 'navRoute']
  llk = [m for m in lr if m.which() == 'liveLocationKalman']
  assert len(nav) > 0 and len(llk) >= NAV_FRAMES and nav[0].logMonoTime < llk[-NAV_FRAMES].logMonoTime

  log_msgs = []
  try:
    assert "MAPBOX_TOKEN" in os.environ
    os.environ['MAP_RENDER_TEST_MODE'] = '1'
    Params().put_bool('DmModelInitialized', True)
    managed_processes['mapsd'].start()
    managed_processes['navmodeld'].start()

    # setup position and route
    for _ in range(10):
      for s in (llk[-NAV_FRAMES], nav[0]):
        pm.send(s.which(), s.as_builder().to_bytes())
      sm.update(1000)
      if sm.updated['navModel']:
        break
      time.sleep(1)

    if not sm.updated['navModel']:
      raise Exception("no navmodeld outputs, failed to initialize")

    # drain
    time.sleep(2)
    sm.update(0)

    # run replay
    for n in range(len(llk) - NAV_FRAMES, len(llk)):
      pm.send(llk[n].which(), llk[n].as_builder().to_bytes())
      m = messaging.recv_one(sm.sock['navThumbnail'])
      assert m is not None, f"no navThumbnail, frame={n}"
      log_msgs.append(m)

      m = messaging.recv_one(sm.sock['mapRenderState'])
      assert m is not None, f"no mapRenderState, frame={n}"
      log_msgs.append(m)

      m = messaging.recv_one(sm.sock['navModel'])
      assert m is not None, f"no navModel response, frame={n}"
      log_msgs.append(m)
  finally:
    managed_processes['mapsd'].stop()
    managed_processes['navmodeld'].stop()

  return log_msgs


def model_replay(lr, frs):
  if not PC:
    spinner = Spinner()
    spinner.update("starting model replay")
  else:
    spinner = None

  log_msgs = []

  # modeld is using frame pairs
  modeld_logs = trim_logs_to_max_frames(lr, MAX_FRAMES, {"roadCameraState", "wideRoadCameraState"}, {"roadEncodeIdx", "wideRoadEncodeIdx"})
  dmodeld_logs = trim_logs_to_max_frames(lr, MAX_FRAMES, {"driverCameraState"}, {"driverEncodeIdx"})

  if not SEND_EXTRA_INPUTS:
    modeld_logs = [msg for msg in modeld_logs if msg.which() not in ["liveCalibration", "lateralPlan"]]
    dmodeld_logs = [msg for msg in dmodeld_logs if msg.which() not in ["liveCalibration", "lateralPlan"]]




  # initial calibration
  cal_msg = next(msg for msg in lr if msg.which() == "liveCalibration").as_builder()
  cal_msg.logMonoTime = lr[0].logMonoTime
  modeld_logs.insert(0, cal_msg.as_reader())
  dmodeld_logs.insert(0, cal_msg.as_reader())

  modeld = get_process_config("modeld")
  dmonitoringmodeld = get_process_config("dmonitoringmodeld")

  try:
    if spinner:
      spinner.update("running model replay")
    modeld_msgs = replay_process(modeld, modeld_logs, frs)
    dmonitoringmodeld_msgs = replay_process(dmonitoringmodeld, dmodeld_logs, frs)
    log_msgs.extend([m for m in modeld_msgs if m.which() == "modelV2"])
    #log_msgs.extend([m for m in dmonitoringmodeld_msgs if m.which() == "driverStateV2"])
  finally:
    if spinner:
      spinner.close()

  return log_msgs


if __name__ == "__main__":
  update = "--update" in sys.argv
  replay_dir = os.path.dirname(os.path.abspath(__file__))
  print(replay_dir)
  ref_commit_fn = os.path.join(replay_dir, "model_replay_ref_commit")

  # load logs
  lr = list(LogReader(get_url(TEST_ROUTE, SEGMENT)))
  frs = {
    'roadCameraState': FrameReader(get_url(TEST_ROUTE, SEGMENT, log_type="fcamera"), readahead=True),
    'driverCameraState': FrameReader(get_url(TEST_ROUTE, SEGMENT, log_type="dcamera"), readahead=True),
    'wideRoadCameraState': FrameReader(get_url(TEST_ROUTE, SEGMENT, log_type="ecamera"), readahead=True)
  }

  # Update tile refs
  if update:
    import urllib
    import requests
    import threading
    import http.server
    from selfdrive.test.openpilotci import upload_bytes
    os.environ['MAPS_HOST'] = 'http://localhost:5000'

    class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
      def do_GET(self):
        assert len(self.path) > 10  # Sanity check on path length
        r = requests.get(f'https://api.mapbox.com{self.path}', timeout=30)
        upload_bytes(r.content, urllib.parse.urlparse(self.path).path.lstrip('/'))
        self.send_response(r.status_code)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(r.content)

    server = http.server.HTTPServer(("127.0.0.1", 5000), HTTPRequestHandler)
    thread = threading.Thread(None, server.serve_forever, daemon=True)
    thread.start()
  else:
    os.environ['MAPS_HOST'] = BASE_URL.rstrip('/')


  print("__")
  print("__")

  #print(frs)

  #main_img = frs['roadCameraState']


  #main_img = frs['roadCameraState'].get(0, pix_fmt="nv12")

  # ____

  frame_id = 0
  prev_main_img = frs['roadCameraState'].get(frame_id, pix_fmt="nv12")[0]
  prev_wide_img = frs['wideRoadCameraState'].get(frame_id, pix_fmt="nv12")[0]

  prev_main_img_rgb = img_to_rgb(prev_main_img)
  prev_wide_img_rgb = img_to_rgb(prev_wide_img)

  # ____

  frame_id = 1
  main_img = frs['roadCameraState'].get(frame_id, pix_fmt="nv12")[0]
  wide_img = frs['wideRoadCameraState'].get(frame_id, pix_fmt="nv12")[0]

  main_img_rgb = img_to_rgb(main_img)
  wide_img_rgb = img_to_rgb(wide_img)

  # ____



  '''

  #print("OK0")
  #context = cuda.Device(0).make_context()
  #control_loop = ControlStateMachine(active_mode=mode.step_through, model_name="supercombo_laptop")
  #print("OK0.5")

  prev_main_img_comma_format = control_loop.convert_image(prev_main_img_rgb, control_loop.model_transform_main)
  prev_wide_img_comma_format = control_loop.convert_image(prev_wide_img_rgb, control_loop.model_transform_extra)

  main_img_comma_format = control_loop.convert_image(main_img_rgb, control_loop.model_transform_main)
  wide_img_comma_format = control_loop.convert_image(wide_img_rgb, control_loop.model_transform_extra)

  np.save('/home/deepview/SSD/pathfinder/src/get_data/images/main_image.npy', main_img_comma_format)
  np.save('/home/deepview/SSD/pathfinder/src/get_data/images/wide_image.npy', wide_img_comma_format)
  np.save('/home/deepview/SSD/pathfinder/src/get_data/images/prev_main_image.npy', prev_main_img_comma_format)
  np.save('/home/deepview/SSD/pathfinder/src/get_data/images/prev_wide_image.npy', prev_wide_img_comma_format)

  print("OK1")
  #os._exit(0)
  print("OK2")

  # ____
  timestamp = str(time.time())
  control_loop.images.append((timestamp, prev_main_img_rgb, prev_main_img_comma_format, prev_wide_img_comma_format))
  control_loop.images.append((timestamp, main_img_rgb, main_img_comma_format, wide_img_comma_format))

  control_loop.run_inference()

  os._exit(0)

  '''

  print("OK")

  # run replays
  log_msgs = model_replay(lr, frs)

  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")

  print_in_color(f"len(log_msgs)={len(log_msgs)}", "yellow")

  for log_msg_i in range(0, len(log_msgs)):
      print_in_color(f"log_msgs[{log_msg_i}].modelV2.frameId={log_msgs[log_msg_i].modelV2.frameId}", "yellow")

  print_in_color(f"log_msgs[0]={log_msgs[0]}", "yellow")
  print_in_color(f"log_msgs[1]={log_msgs[1]}", "yellow")
  print_in_color(f"log_msgs[2]={log_msgs[2]}", "yellow")
  print_in_color(f"log_msgs[3]={log_msgs[3]}", "yellow")

  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")
  print("___________________")

  if not NO_NAV:
    log_msgs += nav_model_replay(lr)

  # get diff
  failed = False
  if not update:
    with open(ref_commit_fn) as f:
      ref_commit = f.read().strip()
    log_fn = get_log_fn(ref_commit, TEST_ROUTE)
    try:
      all_logs = list(LogReader(BASE_URL + log_fn))
      cmp_log = []

      # logs are ordered based on type: modelV2, driverStateV2, nav messages (navThumbnail, mapRenderState, navModel)
      model_start_index = next(i for i, m in enumerate(all_logs) if m.which() == "modelV2")
      cmp_log += all_logs[model_start_index:model_start_index + MAX_FRAMES]
      dmon_start_index = next(i for i, m in enumerate(all_logs) if m.which() == "driverStateV2")
      cmp_log += all_logs[dmon_start_index:dmon_start_index + MAX_FRAMES]
      if not NO_NAV:
        nav_start_index = next(i for i, m in enumerate(all_logs) if m.which() in ["navThumbnail", "mapRenderState", "navModel"])
        nav_logs = all_logs[nav_start_index:nav_start_index + NAV_FRAMES*3]
        cmp_log += nav_logs

      ignore = [
        'logMonoTime',
        'modelV2.frameDropPerc',
        'modelV2.modelExecutionTime',
        'driverStateV2.modelExecutionTime',
        'driverStateV2.dspExecutionTime',
        'navModel.dspExecutionTime',
        'navModel.modelExecutionTime',
        'navThumbnail.timestampEof',
        'mapRenderState.locationMonoTime',
        'mapRenderState.renderTime',
      ]
      if PC:
        ignore += [
          'modelV2.laneLines.0.t',
          'modelV2.laneLines.1.t',
          'modelV2.laneLines.2.t',
          'modelV2.laneLines.3.t',
          'modelV2.roadEdges.0.t',
          'modelV2.roadEdges.1.t',
        ]
      # TODO this tolerance is absurdly large
      tolerance = 2.0 if PC else None
      results: Any = {TEST_ROUTE: {}}
      log_paths: Any = {TEST_ROUTE: {"models": {'ref': BASE_URL + log_fn, 'new': log_fn}}}
      results[TEST_ROUTE]["models"] = compare_logs(cmp_log, log_msgs, tolerance=tolerance, ignore_fields=ignore)
      diff1, diff2, failed = format_diff(results, log_paths, ref_commit)

      print(diff2)
      print('-------------\n'*5)
      print(diff1)
      with open("model_diff.txt", "w") as f:
        f.write(diff2)
    except Exception as e:
      print(str(e))
      failed = True

  # upload new refs
  if (update or failed) and not PC:
    from selfdrive.test.openpilotci import upload_file

    print("Uploading new refs")

    new_commit = get_commit()
    log_fn = get_log_fn(new_commit, TEST_ROUTE)
    save_log(log_fn, log_msgs)
    try:
      upload_file(log_fn, os.path.basename(log_fn))
    except Exception as e:
      print("failed to upload", e)

    with open(ref_commit_fn, 'w') as f:
      f.write(str(new_commit))

    print("\n\nNew ref commit: ", new_commit)

  sys.exit(int(failed))
