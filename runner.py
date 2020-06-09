import subprocess
import sys
import os
import time

helper_dir = "."

def get_cilk_tool_helper_dir():
  out,err = run_command("which clang")
  path =  ("/".join(str(out, 'utf-8').split("/")[:-1])).strip()
  return path+"/cilk_tool_helpers"

def get_parallelism(bin_instrument, bin_args):
  out,err = run_command(bin_instrument + " " + " ".join(bin_args))
  return float((str(err,'utf-8')).split('parallelism')[-1].strip())

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

def run_on_p_workers(P, rcommand):
  cpu_ordering = get_cpu_ordering()
  cpu_online = cpu_ordering[:P]
  cpu_offline = cpu_ordering[P:]

  for x in cpu_offline:
    #run_command("taskset -c "+",".join([str(p) for (p,m) in cpu_offline])+" nice -n 19 "+helper_dir+"/busywait.sh &", True)
    print("taskset -c "+str(x[0])+" nice -n 19 "+helper_dir+"/busywait.sh &", True)
    run_command("taskset -c "+str(x[0])+" nice -n 19 "+helper_dir+"/busywait.sh &", True)

  time.sleep(0.1)
  #print cpu_online
  #print cpu_offline
  rcommand = "taskset -c " + ",".join([str(p) for (p,m) in cpu_online]) + " " + rcommand
  #print rcommand
  print(rcommand)
  proc = subprocess.Popen(['CILK_NWORKERS=' + str(P) + ' ' + rcommand], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out,err=proc.communicate()
  err = str(err, "utf-8")
  print(err)
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

# upper bound P-worker runtime for program with work T1 and parallelism PAR 
def bound_runtime(T1, PAR, P):
  Tp = T1/P + (1.0-1.0/P)*T1/PAR
  return Tp

def get_hyperthreads():
    command = "for cpunum in $(cat /sys/devices/system/cpu/cpu*/topology/thread_siblings_list | cut -s -d, -f2- | tr ',' '\n' | sort -un); do echo $cpunum; done"
    proc = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out,err=proc.communicate()
    print(out)

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

def run(bin_instrument, bin_vanilla, bin_args):
  parallelism = get_parallelism(bin_instrument, bin_args)
  print(parallelism)

  #RUN_COMMAND = "perf stat " + " ".join(sys.argv[1:])
  # strace -c ?
  #RUN_COMMAND =  "time -p " + " ".join(sys.argv[1:]) #"time -p ./fib 40"
  RUN_COMMAND =  "time -p " + bin_vanilla + " " + " ".join(bin_args)#" ./fib-clean 40"
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

