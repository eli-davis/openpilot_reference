# #!/usr/bin/env python3
# import argparse
# import binascii
# from collections import defaultdict

# import cereal.messaging as messaging
# from common.realtime import sec_since_boot


# def can_printer(bus, max_msg, addr, ascii_decode):
#   logcan = messaging.sub_sock('can', addr=addr)

#   start = sec_since_boot()
#   lp = sec_since_boot()
#   msgs = defaultdict(list)
#   while 1:
#     can_recv = messaging.drain_sock(logcan, wait_for_one=True)
#     for x in can_recv:
#       for y in x.can:
#         if y.src == bus:
#           msgs[y.address].append(y.dat)

#     if sec_since_boot() - lp > 0.1:
#       dd = chr(27) + "[2J"
#       dd += f"{sec_since_boot() - start:5.2f}\n"
#       for addr in sorted(msgs.keys()):
#         a = f"\"{msgs[addr][-1].decode('ascii', 'backslashreplace')}\"" if ascii_decode else ""
#         x = binascii.hexlify(msgs[addr][-1]).decode('ascii')
#         freq = len(msgs[addr]) / (sec_since_boot() - start)
#         if max_msg is None or addr < max_msg:
#           dd += "%04X(%4d)(%6d)(%3dHz) %s %s\n" % (addr, addr, len(msgs[addr]), freq, x.ljust(20), a)
#       print(dd)
#       lp = sec_since_boot()

# if __name__ == "__main__":
#   parser = argparse.ArgumentParser(description="simple CAN data viewer",
#                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

#   parser.add_argument("--bus", type=int, help="CAN bus to print out", default=0)
#   parser.add_argument("--max_msg", type=int, help="max addr")
#   parser.add_argument("--ascii", action='store_true', help="decode as ascii")
#   parser.add_argument("--addr", default="127.0.0.1")

#   args = parser.parse_args()
#   can_printer(args.bus, args.max_msg, args.addr, args.ascii)
#!/usr/bin/env python3
#!/usr/bin/env python3
#!/usr/bin/env python3
#!/usr/bin/env python3
import argparse
import binascii
import pandas as pd
from collections import defaultdict

import cereal.messaging as messaging
from common.realtime import sec_since_boot

def can_printer(bus, addr, output_file):
  logcan = messaging.sub_sock('can', addr=addr)

  start = sec_since_boot()
  lp = sec_since_boot()
  msgs = defaultdict(list)

  # Initialize a DataFrame to store the CAN data
  can_data = pd.DataFrame(columns=['timestamp', 'arbitration_id', 'data'])

  while 1:
    can_recv = messaging.drain_sock(logcan, wait_for_one=True)
    for x in can_recv:
      
      for y in x.can:
        if y.src == bus:
          msgs[y.address].append((y.busTime, y.dat))  # use y.busTime for timestamp

    if sec_since_boot() - lp > 0.1:
      for addr in sorted(msgs.keys()):
        t, data = msgs[addr][-1]  # unpack timestamp and data
        x = binascii.hexlify(data).decode('ascii')

        # Append the new data to the DataFrame using pandas.concat
        new_data = pd.DataFrame({
          'timestamp': [t],
          'arbitration_id': [addr],
          'data': [x]
        })
        can_data = pd.concat([can_data, new_data], ignore_index=True)

      # Print the data to the console
      can_data.to_parquet(output_file)

      lp = sec_since_boot()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="simple CAN data viewer",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument("--bus", type=int, help="CAN bus to print out", default=0)
  parser.add_argument("--addr", default="127.0.0.1")
  parser.add_argument("--output", help="Output parquet file", required=True)

  args = parser.parse_args()
  can_printer(args.bus, args.addr, args.output)
