import matplotlib.pyplot as plt

from trade_simulator.pool.pool import Pool


def plot_pool_balace(pool: Pool, folder_path: str):
    plt.figure(figsize=(15, 6))
    plt.grid()
    plt.title(f"Pool {pool.name} Balance Over Time")
    plt.xlabel("Time Step")
    plt.ylabel("Balance")
    for key in pool.metrics["portfolio"].keys():
        plt.plot(pool.metrics["portfolio"][key], label=key)
    plt.legend()
    plt.savefig(f"{folder_path}/{pool.name.replace(" ", "_")}_balance_over_time.png")
    plt.close()


def plot_uniswapv2_k(pool: Pool, folder_path: str):
    plt.figure(figsize=(15, 6))
    plt.grid()
    plt.title(f"Uniswap k Value Over Time for Pool {pool.name}")
    plt.xlabel("Time Step")
    plt.ylabel("k Value")
    plt.plot(pool.metrics["k"], label="k Value", color="orange")
    plt.legend()
    plt.savefig(
        f"{folder_path}/{pool.name.replace(' ', '_')}_uniswap_k_value_over_time.png"
    )
    plt.close()
