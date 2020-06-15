import csv
import matplotlib
import matplotlib.pyplot as plt

PARALLELISM_COL = 3
BENCHMARK_COL_START = 5 # actually 6, but we're adding 1-indexed cpu counts

# upper bound P-worker runtime for program with work T1 and parallelism PAR 
def bound_runtime(T1, PAR, P):
  Tp = T1/P + (1.0-1.0/P)*T1/PAR
  return Tp

def get_row_data(out_csv, tag):
  data = {}
  data["num_workers"] = []
  data["obs_runtime"] = []
  data["perf_lin_runtime"] = []
  data["greedy_runtime"] = []
  data["span_runtime"] = []
  data["obs_speedup"] = []
  data["perf_lin_speedup"] = []
  data["greedy_speedup"] = []
  data["span_speedup"] = []

  with open(out_csv, "r") as out_csv_file:
    rows = csv.reader(out_csv_file, delimiter=",")

    first = True
    num_cpus = 0

    for row in rows:
      if first:
        # get num cpus (extracts num_cpus from, for example, "32c time (seconds)" )
        num_cpus = int(row[-1].split()[0][:-1])
        print(num_cpus)

        first = False
        continue

      if row[0] == tag:
        # collect data from this row of the csv file
        parallelism = float(row[PARALLELISM_COL])
        single_core_runtime = float(row[BENCHMARK_COL_START+1])

        for i in range(1, num_cpus+1):
          data["num_workers"].append(i)

          data["obs_runtime"].append(float(row[BENCHMARK_COL_START+i]))
          data["perf_lin_runtime"].append(single_core_runtime/i)
          data["greedy_runtime"].append(bound_runtime(single_core_runtime, parallelism, i))
          data["span_runtime"].append(single_core_runtime/parallelism)

          data["obs_speedup"].append(single_core_runtime/float(row[BENCHMARK_COL_START+i]))
          data["perf_lin_speedup"].append(1.0*i)
          data["greedy_speedup"].append(single_core_runtime/(bound_runtime(single_core_runtime, parallelism, i)))
          data["span_speedup"].append(parallelism)
        break
  return data

# by default, plots the last row (i.e. overall execution)
def plot(out_csv="out.csv", out_plot="plot.pdf", tag=""):
  print("Generate plot")
  matplotlib.use('PDF')
  fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(12,6))

  data = get_row_data(out_csv, tag)

  print(data)


  # legend shared between subplots.
  # TODO: make colors correspond between the subplots, so the legend makes sense for both
  axs[0].plot(data["num_workers"], data["obs_runtime"], "m", label="Observed")
  axs[0].plot(data["num_workers"], data["perf_lin_runtime"], "g", label="Perfect linear speedup")
  axs[0].plot(data["num_workers"], data["greedy_runtime"], "c", label="Greedy scheduling bound")
  axs[0].plot(data["num_workers"], data["span_runtime"], "y", label="Span bound")

  num_workers = data["num_workers"][-1]

  axs[0].set_xlabel("Num workers")
  axs[0].set_ylabel("Runtime")
  axs[0].set_title("Execution time")
  axs[0].set(xlim=[0,num_workers], ylim=[0,num_workers])
  #axs[0].set_aspect(1/axs[0].get_data_ratio())
  #axs[0].set_aspect(1)
  
  """
  print("obs_speedup")
  print(obs_speedup)
  print("perf_lin_speedup")
  print(perf_lin_speedup)
  print("greedy speedup")
  print(greedy_speedup)
  print("span bound")
  print(span_speedup)
  """
  axs[1].plot(data["num_workers"], data["obs_speedup"], "m", label="Observed")
  axs[1].plot(data["num_workers"], data["perf_lin_speedup"], "g", label="Perfect linear speedup")
  axs[1].plot(data["num_workers"], data["greedy_speedup"], "c", label="Greedy scheduling bound")
  axs[1].plot(data["num_workers"], data["span_speedup"], "y", label="Span bound")

  axs[1].set_xlabel("Num workers")
  axs[1].set_ylabel("Speedup")
  axs[1].set_title("Speedup")
  axs[1].set(xlim=[0,num_workers], ylim=[0,num_workers])
  #axs[1].set_aspect(1/axs[1].get_data_ratio())
  #axs[1].set_aspect(1)

  plt.tight_layout(pad=3.0)
  plt.legend(loc="upper right")

  plt.savefig(out_plot)

