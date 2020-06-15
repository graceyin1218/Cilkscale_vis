import subprocess
import sys
import os
import time
import csv

helper_dir = "."


def get_cilk_tool_helper_dir():
  out,err = run_command("which clang")
  path =  ("/".join(str(out, 'utf-8').split("/")[:-1])).strip()
  return path+"/cilk_tool_helpers"

# generate csv with parallelism numbers
def get_parallelism(bin_instrument, bin_args, out_csv):
  out,err = run_command("CILKSCALE_OUT=" + out_csv + " " + bin_instrument + " " + " ".join(bin_args))
  """
  with open("PAR_TEMP_CSV", "rbU") as csvfile:
    reader = csv.DictReader(csvfile)
    first = True
    for row in reader:
      if first:
        first = False
        continue
      print(row["parallelism"])
      return float(row["parallelism"])
  print("Failed to calculate parallelism")

  
  return float((str(err,'utf-8')).split('parallelism')[-1].strip())
  """
  return

def run_command(cmd, asyn = False):
  proc = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  print(cmd)
  if not asyn:
    out,err=proc.communicate()
    return out,err
  else:
    return ""

def get_n_cpus():
  return len(get_cpu_ordering())

def benchmark_tmp_output(n):
  return ".out.bench." + str(n) + ".csv"

def run_on_p_workers(P, rcommand):
  cpu_ordering = get_cpu_ordering()
  cpu_online = cpu_ordering[:P]
  """
  cpu_offline = cpu_ordering[P:]

  for x in cpu_offline:
    #run_command("taskset -c "+",".join([str(p) for (p,m) in cpu_offline])+" nice -n 19 "+helper_dir+"/busywait.sh &", True)
    print("taskset -c "+str(x[0])+" nice -n 19 "+helper_dir+"/busywait.sh &", True)
    run_command("taskset -c "+str(x[0])+" nice -n 19 "+helper_dir+"/busywait.sh &", True)
  """

  time.sleep(0.1)
  rcommand = "taskset -c " + ",".join([str(p) for (p,m) in cpu_online]) + " " + rcommand
  print(rcommand)
  bench_out_csv = benchmark_tmp_output(P)
  proc = subprocess.Popen(['CILK_NWORKERS=' + str(P) + ' ' + "CILKSCALE_OUT=" + bench_out_csv + " " + rcommand], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out,err=proc.communicate()
  err = str(err, "utf-8")
  print(err)

  """
  run_command("pkill -f busywait.sh")
  for line in err.splitlines():
    #if line.endswith('seconds time elapsed'):
    if line.startswith('real'):
      #line = line.replace('seconds time elapsed','').strip()
      line = line.replace('real','').strip()
      val = float(line)
      return val

    #if line.startswith('real'):
    #  line=line.replace('real ', '').strip()
    #  val = float(line)
    #  return val
  """

# upper bound P-worker runtime for program with work T1 and parallelism PAR 
def bound_runtime(T1, PAR, P):
  Tp = T1/P + (1.0-1.0/P)*T1/PAR
  return Tp

"""
def get_hyperthreads():
    command = "for cpunum in $(cat /sys/devices/system/cpu/cpu*/topology/thread_siblings_list | cut -s -d, -f2- | tr ',' '\n' | sort -un); do echo $cpunum; done"
    proc = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out,err=proc.communicate()
    print(out)
"""

def get_cpu_ordering():
  out,err = run_command("lscpu --parse")

  out = str(out, 'utf-8')
  #print(out)

  avail_cpus = []
  for l in out.splitlines():
    if l.startswith('#'):
      continue
    items = l.strip().split(',')
    cpu_id = int(items[0])
    node_id = int(items[1])
    socket_id = int(items[2])
    avail_cpus.append((socket_id, node_id, cpu_id))

  avail_cpus = sorted(avail_cpus)
  ret = []
  added_nodes = dict()
  for x in avail_cpus:
    if x[1] not in added_nodes:
      added_nodes[x[1]] = True
    else:
      continue
    ret.append((x[2], x[0]))
  return ret

def run(bin_instrument, bin_bench, bin_args, out_csv="out.csv"):
  # get parallelism
  get_parallelism(bin_instrument, bin_args, out_csv)

  # get benchmark runtimes
  NCPUS = get_n_cpus()

  print("Generating Scalability Data for " + str(NCPUS) + " cpus.")

  # this will be prepended with CILK_NWORKERS and CILKSCALE_OUT in run_on_p_workers
  # any tmp files will be destroyed
  run_command = bin_bench + " " + " ".join(bin_args)
  results = dict()
  for i in range(1, NCPUS+1):
    results[i] = run_on_p_workers(i, run_command)

  new_rows = []

  # read data from out_csv
  with open(out_csv, "r") as out_csv_file:
    rows = out_csv_file.readlines()
    new_rows = rows.copy()
    for i in range(len(new_rows)):
      new_rows[i] = new_rows[i].strip("\n")

    # join all the csv data
    for i in range(1, NCPUS+1):
      with open(benchmark_tmp_output(i), "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        row_num = 0
        for row in reader:
          if row_num == 0:
            col_header = str(i) + "c " + row[1].strip()
            new_rows[row_num] += "," + col_header
          else:
            # second col contains runtime
            time = row[1].strip()
            new_rows[row_num] += "," + time
          row_num += 1
      os.remove(benchmark_tmp_output(i))

    for i in range(len(new_rows)):
      new_rows[i] += "\n"

  # write the joined data to out_csv
  with open(out_csv, "w") as out_csv_file:
    out_csv_file.writelines(new_rows)



  """


  #RUN_COMMAND = "perf stat " + " ".join(sys.argv[1:])
  # strace -c ?
  #RUN_COMMAND =  "time -p " + " ".join(sys.argv[1:]) #"time -p ./fib 40"
  RUN_COMMAND =  "time -p " + bin_bench + " " + " ".join(bin_args)#" ./fib-clean 40"
  print(RUN_COMMAND)


  print(get_cpu_ordering())

  NCPUS = get_n_cpus()
  print("NCPUS is " + str(NCPUS))
  #schedule = get_schedule()
  #quit()

  print("Generating Scalability Data for " + str(NCPUS) + " cpus.")

  results = dict()
  for i in range(1,NCPUS+1):
    results[i] = run_on_p_workers(i, RUN_COMMAND)

  print("RESULTS")
  print(results)

  #data = open(data_filename, 'w+')

  d = {}
  d["num_workers"] = []
  d["obs_runtime"] = []
  d["obs_speedup"] = []
  d["perf_lin_speedup"] = []
  d["perf_lin_runtime"] = []
  d["greedy_runtime"] = []
  d["span_speedup"] = []
  # ??
  d["greedy_speedup"] = []
  d["span_runtime"] = []

  cpu_ordering = get_cpu_ordering()
  for i in range(1,NCPUS+1):
    cpu_online = cpu_ordering[:i]
    maxsocket = None
    for x in cpu_online:
      if maxsocket == None or int(x[1])+1 > maxsocket:
        maxsocket = int(x[1])+1

    # write to csv
    # 1:#workers, 2:observed runtime, 3:observed speedup, 4:perfect linear speedup, 5:runtime if perfect linear speedup, 6:runtime greedy bound, 7:speedup span bound, 8: ??, 9:speedup greedy bound, 10:runtime span bound
    #data.write(str(i) + "," + str(results[i]) +","+str(results[1]/results[i]) +","+str(1.0*i)+","+str(results[1]/i)+","+str(bound_runtime(results[1],parallelism,i))+","+str(parallelism)+","+str(maxsocket)+"," +str(results[1]/(bound_runtime(results[1], parallelism, i)))+"," +str(results[1]/parallelism)+"\n")

    d["num_workers"].append(i)
    d["obs_runtime"].append(results[i])
    d["obs_speedup"].append(results[1]/results[i])
    d["perf_lin_speedup"].append(1.0*i)
    d["perf_lin_runtime"].append(results[1]/i)
    d["greedy_runtime"].append(bound_runtime(results[1],parallelism,i))
    d["span_speedup"].append(parallelism)
    d["greedy_speedup"].append(results[1]/(bound_runtime(results[1], parallelism, i)))
    d["span_runtime"].append(results[1]/parallelism)

  #data.close()

  return d
  """

