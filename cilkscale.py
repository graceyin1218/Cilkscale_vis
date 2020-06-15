import argparse
from runner import run
from plotter import plot

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument("--cilkscale", "-c", help="binary compiled with -fcilktool=cilkscale", required=True)
  ap.add_argument("--cilkscale-benchmark", "-b", help="binary compiled with -fcilktool=cilkscale-benchmark", required=True)
  """
  ap.add_argument("--instrumented", "-i", help="binary instrumented with cilkscale", required=True)
  ap.add_argument("--vanilla", "-f", help="binary without cilkscale", required=True)
  """
  ap.add_argument("--output-csv", "-ocsv", help="csv file for output data")
  ap.add_argument("--output-plot", "-oplot", help="plot file dest")
  ap.add_argument("--args", "-a", nargs="*", help="binary arguments")

  args = ap.parse_args()
  print(args)


  # TEMP
  out_csv = "out-new.csv"
  out_plot = "out-new.pdf"

  """
  bin_instrument = args.instrumented
  bin_vanilla = args.vanilla
  """
  bin_instrument = args.cilkscale
  bin_bench = args.cilkscale_benchmark
  bin_args = args.args

  # generate data
  run(bin_instrument, bin_bench, bin_args, out_csv)

  # save data to csv?

  # generate plot
  # (out_plot defaults to plot.pdf)
  # (tag defaults to "", i.e. last row of csv)
  tag = ""
  plot(out_csv, out_plot, tag)

if __name__ == '__main__':
  main()

