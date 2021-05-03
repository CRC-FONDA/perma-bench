import sys
import matplotlib.pyplot as plt

from common import *

def plot_bw(system_data, ax):
    bars = sorted([k for k in system_data.keys() if 'dram' not in k])
    num_bars = len(bars)
    bar_width = 0.8 / num_bars

    num_xticks = len(system_data[bars[0]])
    x_pos = range(num_xticks)

    for i, system in enumerate(bars):
        data = system_data[system]
        _, y_data = zip(*data)
        pos = [x + (i * bar_width) for x in x_pos]
        ax.bar(pos, y_data, width=bar_width, label=SYSTEM_NAME[system],
               **BAR(system))

    xticks = BAR_X_TICKS_POS(bar_width, num_bars, num_xticks)
    ax.set_xticks(xticks)
    ax.set_xticklabels([1, 4, 16])
    ax.set_xlabel("# of Partitions")

    ax.set_ylabel("Bandwidth (GB/s)")
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 20))

    HATCH_WIDTH()
    Y_GRID(ax)
    HIDE_BORDERS(ax)


if __name__ == '__main__':
    filter_config = {
        "access_size": 256,
        # "number_partitions": 1
        "random_distribution": "zipf"
    }

    result_path, plot_dir = INIT(sys.argv)
    runs = get_runs_from_results(result_path, "index_update", filter_config)
    bw_data = get_data_from_runs(runs, "number_partitions", "bandwidth", "read")

    fig, ax = plt.subplots(1, 1, figsize=DOUBLE_FIG_SIZE)
    plot_bw(bw_data, ax)

    fig.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=5,
               frameon=False, columnspacing=1, handletextpad=0.3)
    fig.tight_layout()

    plot_path = os.path.join(plot_dir, "index_update_performance")
    SAVE_PLOT(plot_path)
    PRINT_PLOT_PATHS()