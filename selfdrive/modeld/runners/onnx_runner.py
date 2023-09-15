#!/usr/bin/env python3

import os
import sys
import numpy as np
from typing import Tuple, Dict, Union, Any

from termcolor import cprint as print_in_color


os.environ["OMP_NUM_THREADS"] = "4"
os.environ["OMP_WAIT_POLICY"] = "PASSIVE"

import onnxruntime as ort # pylint: disable=import-error

ORT_TYPES_TO_NP_TYPES = {'tensor(float16)': np.float16, 'tensor(float)': np.float32, 'tensor(uint8)': np.uint8}

def read(sz, tf8=False):
  dd = []
  gt = 0
  szof = 1 if tf8 else 4
  while gt < sz * szof:
    st = os.read(0, sz * szof - gt)
    assert(len(st) > 0)
    dd.append(st)
    gt += len(st)
  r = np.frombuffer(b''.join(dd), dtype=np.uint8 if tf8 else np.float32)
  if tf8:
    r = r / 255.
  return r

def write(d):
  os.write(1, d.tobytes())

def run_loop(m, tf8_input=False):
  input_shapes = [[1]+ii.shape[1:] for ii in m.get_inputs()]
  input_keys = [x.name for x in m.get_inputs()]
  input_types = [ORT_TYPES_TO_NP_TYPES[x.type] for x in m.get_inputs()]

  # run once to initialize CUDA provider
  if "CUDAExecutionProvider" in m.get_providers():
    m.run(None, dict(zip(input_keys, [np.zeros(shp, dtype=itp) for shp, itp in zip(input_shapes, input_types)])))

  DATA_DIR_PATH = "/home/deepview/SSD/pathfinder/src/get_data/replay"

  #print_in_color("[/openpilot/selfdrive/modeld/onnx_runnner: run_loop()]", color="red", file=sys.stderr)

  print_in_color(f"_______________________", color="yellow", file=sys.stderr)
  print_in_color(f"_______________________", color="yellow", file=sys.stderr)
  print_in_color(f"ready to run onnx model", color="yellow", file=sys.stderr)

  # start at 1
  # iteration at 0 has no model output
  iteration_i = 1

  while 1:
    inputs = []
    for k, shp, itp in zip(input_keys, input_shapes, input_types):

      ts = np.product(shp)
      #print("reshaping %s with offset %d" % (str(shp), offset), file=sys.stderr)
      inputs.append(read(ts, (k=='input_img' and tf8_input)).reshape(shp).astype(itp))


    test_inputs_dir_path  = f"/home/deepview/SSD/pathfinder/src/models/test/inputs/{iteration_i:04}"
    os.makedirs(test_inputs_dir_path, exist_ok=True)

    print_in_color(f"len(inputs)={len(inputs)}", color="red", file=sys.stderr)

    print_in_color(f"input_keys={input_keys}", color="yellow", file=sys.stderr)
    print_in_color(f"input_shapes={input_shapes}", color="yellow", file=sys.stderr)
    print_in_color(f"input_types={input_types}", color="yellow", file=sys.stderr)

    #print_in_color(f"inputs.shape={inputs.shape}", color="red", file=sys.stderr)
    #print_in_color(f"inputs={inputs}", color="red", file=sys.stderr)
    #print_in_color(f"type(inputs)={type(inputs)}", color="red", file=sys.stderr)

    print_in_color(f"iteration_i={iteration_i}", color="red", file=sys.stderr)

    for input_index in range(0, len(inputs)):

        input_i = inputs[input_index]
        input_key_i = input_keys[input_index]
        input_i_filename = f"{input_key_i}.npy"
        input_i_filepath = os.path.join(test_inputs_dir_path, input_i_filename)

        print(f"saving filepath={input_i_filepath}", file=sys.stderr)
        np.save(input_i_filepath, input_i)


    ret = m.run(None, dict(zip(input_keys, inputs)))

    print(f"len(ret)={len(ret)}")
    print(f"model_output_array.shape={ret[0].shape}")
    #print(ret, file=sys.stderr)

    # save model_output_array
    test_outputs_dir_path  = f"/home/deepview/SSD/pathfinder/src/models/test/outputs/{iteration_i:04}"
    os.makedirs(test_outputs_dir_path, exist_ok=True)
    output_i_filename = f"model_output_array.npy"
    output_i_filepath = os.path.join(test_outputs_dir_path, output_i_filename)
    print(f"saving filepath={output_i_filepath}", file=sys.stderr)
    np.save(output_i_filepath, ret[0])

    for r in ret:
      write(r.astype(np.float32))

    iteration_i += 1


if __name__ == "__main__":
  print(sys.argv, file=sys.stderr)
  print("Onnx available providers: ", ort.get_available_providers(), file=sys.stderr)
  options = ort.SessionOptions()
  options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_DISABLE_ALL

  provider: Union[str, Tuple[str, Dict[Any, Any]]]
  if 'OpenVINOExecutionProvider' in ort.get_available_providers() and 'ONNXCPU' not in os.environ:
    provider = 'OpenVINOExecutionProvider'
  elif 'CUDAExecutionProvider' in ort.get_available_providers() and 'ONNXCPU' not in os.environ:
    options.intra_op_num_threads = 2
    provider = ('CUDAExecutionProvider', {'cudnn_conv_algo_search': 'DEFAULT'})
  else:
    options.intra_op_num_threads = 2
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    provider = 'CPUExecutionProvider'

  try:
    provider = 'CPUExecutionProvider'
    print_in_color(f"Onnx selected provider: {[provider]}", color="yellow", file=sys.stderr)
    ort_session = ort.InferenceSession(sys.argv[1], options, providers=[provider])
    print("Onnx using ", ort_session.get_providers(), file=sys.stderr)
    run_loop(ort_session, tf8_input=("--use_tf8" in sys.argv))
  except KeyboardInterrupt:
    pass
