import sys
import subprocess
import os
import glob
import re

if len(sys.argv)==1:
  crash_dumps = glob.glob(os.path.expanduser('~/matlab_crash_dump.*'))
  filename = max(crash_dumps, key=os.path.getctime)
else:
  filename = sys.argv[1]

print("Translation of %s" % filename)

context = 5

with open(filename,'r') as f:
  for line in f:

    if line.startswith('['):
      parts = line.rstrip().split()
      if parts[0]=="[" and parts[1].endswith("]"):
        [lib_name, lib_pos] = parts[3].split("+")

        lib_pos_hex = "0x%X" % int(lib_pos)
        
        source_line = None
        source_file = None
        
        new_parts = parts[:2]
        if os.path.exists(lib_name):
          out = subprocess.check_output(["addr2line","-p","-C","-f","-e",lib_name,lib_pos_hex])
          m = re.match("(.*?) \(discriminator \d+\)", out)
          if m: out = m.group(1)
          new_parts+=[out.rstrip()]
          try:
            source_line = int(out.split(":")[-1])
            out = out.split(":")[-2]
          except:
            pass
          if " at " in out:
            source_file = out[out.rindex(" at ")+4:]
        else:
          new_parts+= parts[3:]

        print(" ".join(new_parts))


        if os.path.exists(source_file):
          with open(source_file,'r') as sf:
            for i,line in enumerate(sf):
              if i<source_line-context: continue
              if i>source_line+context: break

              print_line = str(i)
              print_line+= "*" if source_line==i else " "
              print_line+=":"+line.rstrip()
              print(print_line)
        

