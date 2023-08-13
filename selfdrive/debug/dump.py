#!/usr/bin/env python3
import os
import sys
import argparse
import json
from hexdump import hexdump
import codecs
codecs.register_error("strict", codecs.backslashreplace_errors)
import pandas as pd
from cereal import log
import cereal.messaging as messaging
from cereal.services import service_list
import signal
import sys

if __name__ == "__main__":

  parser = argparse.ArgumentParser(description='Dump communication sockets. See cereal/services.py for a complete list of available sockets.')
  parser.add_argument('--addr', default='127.0.0.1')
  parser.add_argument("socket", type=str, nargs='*', help="socket names to dump. defaults to all services defined in cereal")
  args = parser.parse_args()

  if args.addr != "127.0.0.1":
    os.environ["ZMQ"] = "1"
    messaging.context = messaging.Context()

  poller = messaging.Poller()
  data_list = []
  for m in args.socket if len(args.socket) > 0 else service_list:
    messaging.sub_sock(m, poller, addr=args.addr)
  def signal_handler(sig, frame):
    print('KeyboardInterrupt detected, writing DataFrame to Parquet file...')
    df = pd.DataFrame(data_list)
    df.to_parquet('candump.parquet')
    sys.exit(0)
  signal.signal(signal.SIGINT, signal_handler)
  values = None

  iteration_i = 0

  DATA_DIR_PATH = "/home/deepview/SSD/pathfinder/src/get_data/replay"

  #with open('candump.txt', 'a') as f:
  if True:
    while 1:
      polld = poller.poll(100)
      for sock in polld:
        msg = sock.receive()

        with log.Event.from_bytes(msg) as log_evt:
          evt = log_evt

        print(f"evt.which()={evt.which()}")

        if evt.which() == 'modelV2':
            print(f"________________________")
            print(f"________________________")
            print(f"________________________")
            print(f"________________________")
            print(evt.to_dict())

            # iteration_0001.json
            # iteration_0002.json
            # ... etc
            json_filename = f"iteration_{iteration_i:04}.json"
            json_filepath = os.path.join(DATA_DIR_PATH, json_filename)

            with open(json_filepath, 'w') as FILE:
                modelV2_dict = evt.to_dict()
                json.dump(modelV2_dict, FILE, indent=4)

            iteration_i += 1

        '''
        try:
           if evt.which() == 'can':
                    # Parse the log.Event into a dictionary
                    data = {
                        'logMonoTime': evt.logMonoTime,
                        'valid': evt.valid
                    }
                    for can_msg in evt.can:
                      data = {
                          'logMonoTime': evt.logMonoTime,
                          'valid': evt.valid,
                          'can_address': can_msg.address,
                          'can_busTime': can_msg.busTime,
                          'can_dat': can_msg.dat,
                          'can_src': can_msg.src
                      }
                      data_list.append(data)
                    # Add the dictionary to data_list

        except UnicodeDecodeError:
          w = evt.which()
          s = f"( logMonoTime {evt.logMonoTime} \n  {w} = "
          s += str(evt.__getattr__(w))
          s += f"\n  valid = {evt.valid} )"
          print(s)
        '''
#df = pd.DataFrame(data_list)
#df.to_parquet('candump.parquet')
