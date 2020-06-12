import matplotlib
import matplotlib.pyplot as plt

def plot(data, out_plot="plot.pdf"):
  print("Generate plot")
  matplotlib.use('PDF')
  fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(12,6))

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

