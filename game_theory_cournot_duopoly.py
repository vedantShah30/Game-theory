import streamlit as st 
import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class LemonadeStandGame:
    def __init__(self, num_rounds):
        self.num_rounds = num_rounds
        self.player1_quantities = []
        self.player2_quantities = []
        self.player1_profits = []
        self.player2_profits = []
        self.prices = []
        self.base_price = 5  # Base price per cup
        self.cost_per_cup = 1  # Cost to produce each cup

    def calculate_price(self, q1, q2):
        return max(self.base_price/2, self.base_price - (q1 + q2) / 4)

    def calculate_profit(self, price, quantity):
        revenue = price * quantity
        cost = self.cost_per_cup * quantity
        return max(0, revenue - cost)

    def play_round(self, q1, q2):
        price = self.calculate_price(q1, q2)
        profit1 = self.calculate_profit(price, q1)
        profit2 = self.calculate_profit(price, q2)

        self.player1_quantities.append(q1)
        self.player2_quantities.append(q2)
        self.player1_profits.append(profit1)
        self.player2_profits.append(profit2)
        self.prices.append(price)

        return q1, q2, price, profit1, profit2

    def best_response(self, q):
        return max(0, min(10, (self.base_price * 4 - q - 4 * self.cost_per_cup) / 2))

    def get_results_df(self):
        return pd.DataFrame({
            'Round': range(1, self.num_rounds + 1),
            'Player 1 Quantity': self.player1_quantities,
            'Player 2 Quantity': self.player2_quantities,
            'Price': self.prices,
            'Player 1 Profit': self.player1_profits,
            'Player 2 Profit': self.player2_profits
        })

    def plot_results(self):
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.scatter(self.player1_quantities, self.player2_quantities, alpha=0.5)
        ax.set_xlabel("Player 1's Lemonade (cups)")
        ax.set_ylabel("Player 2's Lemonade (cups)")
        ax.set_title("Lemonade Stand Showdown: Player Decisions")

        nash_q = (self.base_price * 4 - 4 * self.cost_per_cup) / 3
        nash_q = max(0, min(10, nash_q))
        ax.plot(nash_q, nash_q, 'r*', markersize=20, label='Nash Equilibrium')

        q_range = np.linspace(0, 10, 100)
        br1 = [self.best_response(q) for q in q_range]
        br2 = [self.best_response(q) for q in q_range]
        ax.plot(q_range, br1, 'r--', label="Player 1's Best Response")
        ax.plot(br2, q_range, 'b--', label="Player 2's Best Response")

        ax.legend()
        ax.grid(True)
        return fig

    def plot_input_variation(self):
        fig, ax = plt.subplots(figsize=(10, 6))
        rounds = range(1, self.num_rounds + 1)
        ax.plot(rounds, self.player1_quantities, label="Player 1 Quantity")
        ax.plot(rounds, self.player2_quantities, label="Player 2 Quantity")
        ax.plot(rounds, self.prices, label="Price per Cup")
        ax.set_xlabel("Round")
        ax.set_ylabel("Quantity / Price")
        ax.set_title("Input Variation and Price Over Time")
        ax.legend()
        ax.grid(True)
        return fig

def main():
    st.title("Lemonade Stand Game Simulator")

    st.markdown("""
    ## Project Overview
    This simulator models a competitive game between two players who operate lemonade stands. Each player decides how many cups of lemonade to produce in each round, and the price per cup is determined by the total quantity produced by both players. The goal for each player is to maximize their profit by choosing the optimal quantity of lemonade to produce, taking into account the decisions of the other player.

    The simulator allows you to explore different strategies and understand key concepts in game theory, such as Nash Equilibrium.
    """)

    st.sidebar.header("Game Settings")
    num_rounds = st.sidebar.slider("Number of Rounds", 1, 100, 10)
    game_mode = st.sidebar.radio("Game Mode", ["Manual Input", "Random Simulation"])

    game = LemonadeStandGame(num_rounds)

    if game_mode == "Manual Input":
        st.header("Manual Input Mode")
        for round in range(num_rounds):
            st.subheader(f"Round {round + 1}")
            col1, col2 = st.columns(2)
            with col1:
                q1 = st.number_input(f"Player 1 Quantity (Round {round + 1})", 0, 10, 5)
            with col2:
                q2 = st.number_input(f"Player 2 Quantity (Round {round + 1})", 0, 10, 5)
            
            q1, q2, price, profit1, profit2 = game.play_round(q1, q2)
            
            st.write(f"Price per cup: ${price:.2f}")
            st.write(f"Player 1 profit: ${profit1:.2f}")
            st.write(f"Player 2 profit: ${profit2:.2f}")
    else:
        st.header("Random Simulation Mode")
        if st.button("Run Simulation"):
            for _ in range(num_rounds):
                q1 = random.randint(0, 10)
                q2 = random.randint(0, 10)
                game.play_round(q1, q2)
            st.success("Simulation completed!")

    if game.player1_quantities:
        st.header("Game Results")
        results_df = game.get_results_df()
        st.dataframe(results_df)

        st.header("Player Decisions Visualization")
        st.pyplot(game.plot_results())

        st.markdown("""
        ### Explanation of the Graph
        The scatter plot above shows the quantities of lemonade produced by both players in each round. The red star indicates the **Nash Equilibrium**, where neither player can increase their profit by changing their quantity while the other player's quantity remains the same. The dashed lines represent the best response functions for each player, which show the optimal quantity for one player given the quantity chosen by the other player.
        """)

        st.header("Input Variation and Price Over Time")
        st.pyplot(game.plot_input_variation())

        st.markdown("""
        ### Explanation of the Input Variation Graph
        The line chart above shows how the quantities produced by each player and the price per cup evolve over time across multiple rounds. This visualization helps you understand the dynamics of the game and how the decisions of each player impact the price and profits.
        """)

        total_profit1 = sum(game.player1_profits)
        total_profit2 = sum(game.player2_profits)
        avg_profit1 = total_profit1 / num_rounds
        avg_profit2 = total_profit2 / num_rounds

        st.header("Final Results")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Player 1")
            st.write(f"Total Profit: ${total_profit1:.2f}")
            st.write(f"Average Profit: ${avg_profit1:.2f}")
        with col2:
            st.subheader("Player 2")
            st.write(f"Total Profit: ${total_profit2:.2f}")
            st.write(f"Average Profit: ${avg_profit2:.2f}")

        st.header("Best Choice Equation")
        st.latex(r"q^* = \frac{" + str(game.base_price * 4) + r" - q_{opponent} - " + str(4 * game.cost_per_cup) + r"}{2}")
        st.write("Where q* is the best quantity to produce, and q_opponent is the opponent's quantity.")
        st.write("Note: The actual quantity is limited to the range [0, 10].")

if __name__ == "__main__":
    main()

