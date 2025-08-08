import pandas
from glob import glob

def main():
    # Load all benchmarks from the CSV file
    glob_benchmarks = glob("benchmark_star_expansion*.csv")
    dfs = []
    for benchmark in glob_benchmarks:
        print(f"Processing benchmark: {benchmark}")
        df = pandas.read_csv(benchmark)
        # Append the DataFrame to the list
        dfs.append(df)
    # Calculate the median and the mean of the time for nodes 250 and edges 500 (aggregated over all benchmarks)
    df_all = pandas.concat(dfs)
    node_cnt = 250
    for cnt_edge in df_all['e'].unique():
        print(f"Number of edges: {cnt_edge}")
        df_filtered = df_all[(df_all['n'] == node_cnt) & (df_all['e'] == cnt_edge)]
        median_time = df_filtered['dt'].median()
        mean_time = df_filtered['dt'].mean()
        print(f"Median time for {cnt_edge} edges: {median_time:.6f} seconds")
        print(f"Mean time for {cnt_edge} edges: {mean_time:.6f} seconds")

if __name__ == "__main__":
    main()
