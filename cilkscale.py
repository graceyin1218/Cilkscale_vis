import argparse
from runner import run
from plotter import plot

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument("--instrumented", "-i", help="binary instrumented with cilkscale", required=True)
  ap.add_argument("--vanilla", "-f", help="binary without cilkscale", required=True)
  """
  ap.add_argument("--output-csv", "-ocsv", help="csv file for output data")
  ap.add_argument("--output-plot", "-oplot", help="plot file dest
  """
  ap.add_argument("--args", "-a", nargs="*", help="binary arguments")

  args = ap.parse_args()
  print(args)


  out_csv = "out.csv"
  out_plot = "out.pdf"

  bin_instrument = args.instrumented
  bin_vanilla = args.vanilla
  bin_args = args.args

  # generate data
  data = run(bin_instrument, bin_vanilla, bin_args)

  # save data to csv?

  # generate plot
  # (out_plot defaults to plot.pdf)
  plot(data, out_plot)

if __name__ == '__main__':
  main()

