import matplotlib.pyplot as plt
import numpy as np
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


def plot_k(pool: Pool, folder_path: str):
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


def plot_agent_balance(agent, folder_path: str):
    plt.figure(figsize=(15, 6))
    plt.grid()
    plt.title(f"Agent {agent.type}_{agent.id} Balance Over Time")
    plt.xlabel("Time Step")
    plt.ylabel("Balance")
    for token, balance in agent.metrics["portfolio"].items():
        plt.plot(balance, label=token)
    plt.legend()
    plt.savefig(f"{folder_path}/balance_over_time.png")
    plt.close()


def plot_pair_balance(pool: Pool, folder_path: str):
    plt.figure(figsize=(15, 6))
    plt.grid()
    plt.title(f"Pair Price Over Time for Pool {pool.name}")
    plt.xlabel("Time Step")
    plt.ylabel("Price")
    plt.plot(
        pool.metrics[f"price_of_{pool.amm_agent.token_a}_{pool.amm_agent.token_b}"],
        label=f"{pool.amm_agent.token_a} Price in {pool.amm_agent.token_b}",
    )
    plt.plot(
        pool.metrics[f"price_of_{pool.amm_agent.token_b}_{pool.amm_agent.token_a}"],
        label=f"{pool.amm_agent.token_b} Price in {pool.amm_agent.token_a}",
    )
    plt.legend()
    plt.savefig(
        f"{folder_path}/{pool.name.replace(' ', '_')}_pair_balance_over_time.png"
    )
    plt.close()

def plot_profit_from_fees(pool: Pool, folder_path: str):
    for token, profit in pool.metrics["profit_from_fees"].items():
        if len(profit["value"]) > 0:
            plt.figure(figsize=(15, 6))
            plt.grid()
            plt.title(f"Pool_{pool.id} Profit from Fees in {token}")
            plt.xlabel("Time Step")
            plt.ylabel("Profit")
            plt.plot(profit["timestamp"], profit["value"], label=token)
            plt.legend()
            plt.savefig(f"{folder_path}/profit_from_fees_{token}.png")
            plt.close()

def plot_agent_orders(agent, folder_path: str):
    plt.figure(figsize=(15, 6))
    plt.grid()
    plt.title(f"Agent {agent.type}_{agent.id} Orders Over Time")
    plt.xlabel("Time Step")
    plt.ylabel("Total Orders")
    x_buy = agent.metrics["buy_orders"]
    y_buy = np.linspace(0, len(x_buy) - 1, len(x_buy))
    x_sell = agent.metrics["sell_orders"]
    y_sell = np.linspace(0, len(x_sell) - 1, len(x_sell))
    plt.scatter(x_buy, y_buy, label="Buy Orders", color="green", s=10)
    plt.scatter(x_sell, y_sell, label="Sell Orders", color="red", s=10)
    plt.legend()
    plt.savefig(f"{folder_path}/orders_over_time.png")
    plt.close()
