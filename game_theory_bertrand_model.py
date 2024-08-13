import streamlit as st
import math
import random
import matplotlib.pyplot as plt
import pandas as pd
import io

class Player:
    def __init__(self, name):
        self.name = name
        self.capital = 1000
        self.production_cost = 50
        self.price = 0
        self.units_sold = 0
        self.profits = []
        self.prices = []
        self.investments = []

    def set_price(self, price):
        self.price = price
        self.prices.append(self.price)

    def invest(self, amount):
        self.capital -= amount
        self.investments.append(amount)
        return amount

class Game:
    def __init__(self):
        self.players = [Player("Player 1"), Player("Player 2")]
        self.round = 1
        self.max_demand = 100

    def play_round(self, p1_price, p2_price, p1_investment, p2_investment):
        # Pricing Phase
        self.players[0].set_price(p1_price)
        self.players[1].set_price(p2_price)

        # Market Resolution
        if self.players[0].price < self.players[1].price:
            self.players[0].units_sold = self.max_demand
            self.players[1].units_sold = 0
        elif self.players[1].price < self.players[0].price:
            self.players[1].units_sold = self.max_demand
            self.players[0].units_sold = 0
        else:
            self.players[0].units_sold = self.players[1].units_sold = self.max_demand // 2

        # Profit Calculation
        for player in self.players:
            profit = (player.price - player.production_cost) * player.units_sold
            player.capital += profit
            player.profits.append(profit)

        # Investment Phase
        for player, investment in zip(self.players, [p1_investment, p2_investment]):
            player.invest(investment)
            
            # Production Cost Adjustment
            cost_reduction = math.sqrt(investment) / 10
            scale_effect = (player.units_sold / 100) * 2
            player.production_cost = max(30, player.production_cost - cost_reduction - scale_effect)

        self.round += 1

    def get_results_df(self):
        data = []
        for i in range(self.round - 1):
            data.append({
                'Round': i + 1,
                'Player 1 Price': self.players[0].prices[i],
                'Player 2 Price': self.players[1].prices[i],
                'Player 1 Units Sold': self.players[0].units_sold if i == len(self.players[0].prices) - 1 else (self.max_demand if self.players[0].prices[i] < self.players[1].prices[i] else (self.max_demand // 2 if self.players[0].prices[i] == self.players[1].prices[i] else 0)),
                'Player 2 Units Sold': self.players[1].units_sold if i == len(self.players[1].prices) - 1 else (self.max_demand if self.players[1].prices[i] < self.players[0].prices[i] else (self.max_demand // 2 if self.players[1].prices[i] == self.players[0].prices[i] else 0)),
                'Player 1 Profit': self.players[0].profits[i],
                'Player 2 Profit': self.players[1].profits[i],
                'Player 1 Investment': self.players[0].investments[i],
                'Player 2 Investment': self.players[1].investments[i],
                'Player 1 Production Cost': self.players[0].production_cost,
                'Player 2 Production Cost': self.players[1].production_cost
            })
        return pd.DataFrame(data)

    def plot_game_results(self):
        p1_prices = self.players[0].prices
        p2_prices = self.players[1].prices
        p1_profits = self.players[0].profits
        p2_profits = self.players[1].profits

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        ax1.scatter(p1_prices, p2_prices, c='blue', label='Price Combinations')
        max_profit_index = max(range(len(p1_profits)), key=lambda i: p1_profits[i] + p2_profits[i])
        ax1.scatter(p1_prices[max_profit_index], p2_prices[max_profit_index], c='red', s=100, label='Nash Equilibrium')
        ax1.set_xlabel('Player 1 Price')
        ax1.set_ylabel('Player 2 Price')
        ax1.set_title('Price Strategies and Nash Equilibrium')
        ax1.legend()
        ax1.grid(True)

        rounds = range(1, len(p1_prices) + 1)
        ax2.plot(rounds, p1_prices, label='Player 1 Prices', marker='o')
        ax2.plot(rounds, p2_prices, label='Player 2 Prices', marker='s')
        ax2.set_xlabel('Round')
        ax2.set_ylabel('Price')
        ax2.set_title('Price Changes Over Time')
        ax2.legend()
        ax2.grid(True)

        plt.tight_layout()
        return fig

import streamlit as st
import random
import matplotlib.pyplot as plt
import pandas as pd

# Assuming your classes `Player` and `Game` are already defined

def main():
    st.title("Bertrand Model Game Theory Simulator")

    st.write("""
    ## Project Overview
    This simulation is based on the Bertrand competition model, where two firms compete by setting prices for homogeneous goods. The goal is to explore the concept of Nash Equilibrium in this pricing game, where each player's optimal strategy depends on the strategy of the other player. By simulating multiple rounds of competition, you can observe how different pricing strategies impact profits and market share.
    """)

    st.sidebar.header("Game Settings")
    num_rounds = st.sidebar.slider("Number of Rounds", 1, 20, 5)
    game_mode = st.sidebar.radio("Game Mode", ["Manual Input", "Random Simulation"])

    game = Game()

    if game_mode == "Manual Input":
        st.header("Manual Input Mode")
        for round in range(num_rounds):
            st.subheader(f"Round {round + 1}")
            col1, col2 = st.columns(2)
            with col1:
                p1_price = st.number_input(f"Player 1 Price (Round {round + 1})", 50.0, 150.0, 100.0, step=0.1)
                p1_investment = st.number_input(
                    f"Player 1 Investment (Round {round + 1})", 
                    min_value=0.0, 
                    max_value=float(game.players[0].capital), 
                    step=0.1
                )
            with col2:
                p2_price = st.number_input(f"Player 2 Price (Round {round + 1})", 50.0, 150.0, 100.0, step=0.1)
                p2_investment = st.number_input(
                    f"Player 2 Investment (Round {round + 1})", 
                    min_value=0.0, 
                    max_value=float(game.players[1].capital), 
                    step=0.1
                )
            
            game.play_round(p1_price, p2_price, p1_investment, p2_investment)
            
            st.write(f"Player 1 sold {game.players[0].units_sold} units. Profit: ${game.players[0].profits[-1]:.2f}")
            st.write(f"Player 2 sold {game.players[1].units_sold} units. Profit: ${game.players[1].profits[-1]:.2f}")
    else:
        st.header("Random Simulation Mode")
        if st.button("Run Simulation"):
            for _ in range(num_rounds):
                p1_price = random.uniform(game.players[0].production_cost, 150)
                p2_price = random.uniform(game.players[1].production_cost, 150)
                p1_investment = random.uniform(0, game.players[0].capital)
                p2_investment = random.uniform(0, game.players[1].capital)
                game.play_round(p1_price, p2_price, p1_investment, p2_investment)
            st.success("Simulation completed!")

    if game.round > 1:
        st.header("Game Results")
        results_df = game.get_results_df()
        st.dataframe(results_df)

        st.header("Game Visualizations")
        st.pyplot(game.plot_game_results())

        st.write("""
        ### Graph Explanation
        - **Price Strategies and Nash Equilibrium**: This scatter plot shows the pricing strategies of both players across different rounds. The red point indicates the Nash Equilibrium, where neither player can increase their profit by changing their price unilaterally.
        - **Price Changes Over Time**: This line chart visualizes how each player's pricing strategy evolved over the rounds, offering insight into the competitive dynamics and strategic adjustments.
        
        ### Understanding Nash Equilibrium
        The Nash Equilibrium in this context occurs when both players choose prices such that neither can improve their profit by altering their price while the other player's price remains constant. It's a crucial concept in game theory that illustrates stable strategies in competitive scenarios.
        """)

        st.header("Final Results")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Player 1")
            st.write(f"Capital: ${game.players[0].capital:.2f}")
            st.write(f"Production Cost: ${game.players[0].production_cost:.2f}")
        with col2:
            st.subheader("Player 2")
            st.write(f"Capital: ${game.players[1].capital:.2f}")
            st.write(f"Production Cost: ${game.players[1].production_cost:.2f}")

        csv = results_df.to_csv(index=False)
        st.download_button(
            label="Download results as CSV",
            data=csv,
            file_name="game_results.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    main()

