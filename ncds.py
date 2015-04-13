#!/usr/bin/env python3

import sys
import os
import lzma
import io
import csv
from multiprocessing import Pool
import multiprocessing

def progress(s):
  sys.stderr.write(s)
  sys.stderr.write('\n')

files = sorted([f for f in sys.argv[1:] if os.path.getsize(f) > 0])
sizes = [os.path.getsize(f) for f in files]

progress("Reading all files")
contents = { f : io.FileIO(f).readall() for f in files}


lzma_filters = my_filters = [
    {
      "id": lzma.FILTER_LZMA2, 
      "preset": 9 | lzma.PRESET_EXTREME, 
      "dict_size": max(sizes) * 10, # a big enough dictionary, but not more than needed, saves memory
      "lc": 3,
      "lp": 0,
      "pb": 0, # assume ascii
      "mode": lzma.MODE_NORMAL,
      "nice_len": 273,
      "mf": lzma.MF_BT4
    }
]

def Z(contents):
  return len(lzma.compress(contents, format=lzma.FORMAT_RAW, filters= lzma_filters))

progress("Compressing all files")
compressed = { f : Z(contents[f]) for f in files }

if len(compressed) == 1:
  print(compressed)
  sys.exit()


def ncd(fa,fb):
  Za = compressed[fa]
  Zb = compressed[fb]
  Zab = Z(contents[fa] + contents[fb])
  return (Zab - min(Za, Zb)) / max(Za, Zb)

if len(compressed) == 2:
  print(ncd(files[0], files[1]))
  sys.exit()

progress("Calculating ncd's")



def calculate_row(f):
  data = {"file" : f}
  for f2 in files:
    if f >= f2:
      data[f2] = ncd(f, f2)
    else:
      data[f2] = ''
  return data

data = {}


def add_result(row):
  if len(data) % 10 == 0:
    progress("progress: %f %%" % ((float(len(data)) / len(files)) * 100))
  data[row["file"]] = row

with Pool(multiprocessing.cpu_count()) as p:
  for f in files:
    p.apply_async(calculate_row, args = (f,), callback = add_result) 
  p.close()
  p.join()

output =  csv.DictWriter(sys.stdout, ["file"] + files)
output.writeheader()
for f in files:
  output.writerow(data[f])
