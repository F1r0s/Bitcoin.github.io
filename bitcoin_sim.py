import numpy as np
import pandas as pd
import random

def simulate_bitcoin_prices(days=60, initial_price=65000, mu=0.0005, sigma=0.04):
    """
    Simulates Bitcoin price data using Geometric Brownian Motion.

    Args:
        days (int): Number of days to simulate.
        initial_price (float): Starting price of Bitcoin.
        mu (float): Drift parameter (daily return).
        sigma (float): Volatility parameter (daily standard deviation).

    Returns:
        pd.DataFrame: DataFrame containing 'Day' and 'Price' columns.
    """
    dt = 1
    prices = [initial_price]

    # Set seed for reproducibility
    np.random.seed(123)

    for _ in range(days - 1):
        prev_price = prices[-1]
        drift = (mu - 0.5 * sigma**2) * dt
        shock = sigma * np.sqrt(dt) * np.random.normal()
        price = prev_price * np.exp(drift + shock)
        prices.append(price)

    return pd.DataFrame({
        'Day': range(1, days + 1),
        'Price': prices
    })

def calculate_moving_averages(df):
    """
    Calculates 7-day and 30-day Simple Moving Averages.
    """
    df['SMA_7'] = df['Price'].rolling(window=7).mean()
    df['SMA_30'] = df['Price'].rolling(window=30).mean()
    return df

def run_trading_strategy(df, initial_cash=100000):
    """
    Implements the Golden Cross trading algorithm.
    """
    cash = initial_cash
    btc_holdings = 0
    portfolio_values = []

    print(f"{'Day':<5} {'Price':<10} {'SMA_7':<10} {'SMA_30':<10} {'Action':<10} {'Portfolio Value':<15} {'Holdings (BTC)':<15} {'Cash':<15}")
    print("-" * 95)

    # We need to iterate through the DataFrame.
    # Since we need previous values to detect crossover, we can just track state.
    # However, 'Golden Cross' strictly refers to the crossover event.
    # Strategy:
    #   - If SMA_7 > SMA_30 and we don't have BTC -> BUY
    #   - If SMA_7 < SMA_30 and we have BTC -> SELL

    position = "CASH" # CASH or BTC

    ledger = []

    for index, row in df.iterrows():
        day = row['Day']
        price = row['Price']
        sma_7 = row['SMA_7']
        sma_30 = row['SMA_30']

        action = "HOLD"

        # We can only trade if we have both MAs
        if not pd.isna(sma_7) and not pd.isna(sma_30):
            if sma_7 > sma_30 and position == "CASH":
                # Buy Signal (Golden Cross)
                btc_holdings = cash / price
                cash = 0
                position = "BTC"
                action = "BUY"
            elif sma_7 < sma_30 and position == "BTC":
                # Sell Signal (Death Cross)
                cash = btc_holdings * price
                btc_holdings = 0
                position = "CASH"
                action = "SELL"

        current_value = cash + (btc_holdings * price)
        portfolio_values.append(current_value)

        # Formatting for display
        sma_7_str = f"{sma_7:.2f}" if not pd.isna(sma_7) else "NaN"
        sma_30_str = f"{sma_30:.2f}" if not pd.isna(sma_30) else "NaN"

        print(f"{day:<5} ${price:<9.2f} ${sma_7_str:<9} ${sma_30_str:<9} {action:<10} ${current_value:<14.2f} {btc_holdings:<15.4f} ${cash:<14.2f}")

        ledger.append({
            'Day': day,
            'Price': price,
            'SMA_7': sma_7,
            'SMA_30': sma_30,
            'Action': action,
            'Portfolio Value': current_value
        })

    # Final summary
    final_value = portfolio_values[-1]
    return_pct = ((final_value - initial_cash) / initial_cash) * 100

    print("\n" + "="*30)
    print("FINAL PERFORMANCE SUMMARY")
    print("="*30)
    print(f"Initial Portfolio Value: ${initial_cash:.2f}")
    print(f"Final Portfolio Value:   ${final_value:.2f}")
    print(f"Return:                  {return_pct:.2f}%")
    print("="*30)

if __name__ == "__main__":
    # 1. Simulate Data
    # To ensure we have enough data for the 30-day MA to generate signals within the last portion of 60 days,
    # we might want to simulate more than 60 days, but the prompt says "simulates 60 days".
    # So I will simulate exactly 60 days. The 30-day MA will only appear on day 30.
    # This leaves 30 days for trading.
    print("Simulating 60 days of Bitcoin price data...")
    df = simulate_bitcoin_prices(days=60, initial_price=65000)

    # 2. Calculate MAs
    df = calculate_moving_averages(df)

    # 3. Run Strategy
    run_trading_strategy(df)
