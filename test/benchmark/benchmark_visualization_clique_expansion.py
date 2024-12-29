import matplotlib.pyplot as plt
import numpy as np


def main():
    # Dictionary based organized by node count
    data = {}
    plot3d_raw_data = []
    # Load from benchmark_star_expansion.csv
    with open("benchmark_clique_expansion.csv", "r") as f:
        lines = f.readlines()
        lines = lines[1:]
        for l in lines:
            n, e, dt = l.split(",")
            v = (int(n), int(e), float(dt))
            _data = []
            if n not in data:
                data[n] = []
            data[n].append((v[1], v[2]))
            plot3d_raw_data.append(v)
        for n in data:
            data[n] = np.array(data[n])
    # Plot the data
    plt.figure(figsize=(7, 7))
    plt.title("Clique Expansion Transformation Benchmark (dense matrix)")
    for n in data:
        plt.plot(data[n][:, 0], data[n][:, 1], label="{} nodes".format(n), marker='o')
    plt.grid()
    plt.xlabel("Number of edges")
    plt.ylabel("Time (s)")

    plt.legend()
    # Save the plot
    plt.savefig("benchmark_clique_expansion.png")
    plt.show()
    # 3D mesh plot
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection='3d')
    # Based on plot3d_raw_data
    plot3d_raw_data = np.array(plot3d_raw_data)
    ax.scatter(plot3d_raw_data[:, 0], plot3d_raw_data[:, 1], plot3d_raw_data[:, 2])
    # Fit the data to a mesh
    x = plot3d_raw_data[:, 0]
    y = plot3d_raw_data[:, 1]
    z = plot3d_raw_data[:, 2]
    ax.plot_trisurf(x, y, z, cmap='viridis', edgecolor='none', alpha=0.5)


    ax.set_xlabel("Number of nodes")
    ax.set_ylabel("Number of edges")
    ax.set_zlabel("Time (s)")
    # Set title
    plt.title("Clique Expansion Transformation Benchmark (dense matrix)")
    # Save the plot
    plt.savefig("benchmark_clique_expansion_3d.png")
    plt.show()



if __name__ == "__main__":
    main()

