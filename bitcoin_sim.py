import math
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
        list[dict]: List of dictionaries containing 'Day' and 'Price'.
    """
    dt = 1
    prices = [initial_price]

    # Set seed for reproducibility
    random.seed(123)

    for _ in range(days - 1):
        prev_price = prices[-1]
        drift = (mu - 0.5 * sigma**2) * dt
        # random.gauss(0, 1) generates a number from standard normal distribution (mean=0, std=1)
        shock = sigma * math.sqrt(dt) * random.gauss(0, 1)
        price = prev_price * math.exp(drift + shock)
        prices.append(price)

    # Return a list of dictionaries to mimic DataFrame structure
    data = []
    for i, p in enumerate(prices):
        data.append({
            'Day': i + 1,
            'Price': p
        })
    return data

def calculate_moving_averages(data):
    """
    Calculates 7-day and 30-day Simple Moving Averages.
    """
    # Extract prices for easier calculation
    prices = [d['Price'] for d in data]

    for i in range(len(data)):
        # Calculate SMA_7
        if i >= 6: # need 7 data points (indices i-6 to i is 7 points)
            sma_7 = sum(prices[i-6:i+1]) / 7
            data[i]['SMA_7'] = sma_7
        else:
            data[i]['SMA_7'] = None

        # Calculate SMA_30
        if i >= 29:
            sma_30 = sum(prices[i-29:i+1]) / 30
            data[i]['SMA_30'] = sma_30
        else:
            data[i]['SMA_30'] = None

    return data

def run_trading_strategy(data, initial_cash=100000):
    """
    Implements the Golden Cross trading algorithm.
    """
    cash = initial_cash
    btc_holdings = 0
    portfolio_values = []

    print(f"{'Day':<5} {'Price':<10} {'SMA_7':<10} {'SMA_30':<10} {'Action':<10} {'Portfolio Value':<15} {'Holdings (BTC)':<15} {'Cash':<15}")
    print("-" * 95)

    # We need to iterate through the data.
    # Strategy:
    #   - If SMA_7 > SMA_30 and we don't have BTC -> BUY
    #   - If SMA_7 < SMA_30 and we have BTC -> SELL

    position = "CASH" # CASH or BTC

    ledger = []

    for row in data:
        day = row['Day']
        price = row['Price']
        sma_7 = row['SMA_7']
        sma_30 = row['SMA_30']

        action = "HOLD"

        # We can only trade if we have both MAs
        if sma_7 is not None and sma_30 is not None:
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
        sma_7_str = f"{sma_7:.2f}" if sma_7 is not None else "NaN"
        sma_30_str = f"{sma_30:.2f}" if sma_30 is not None else "NaN"

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
    print("Simulating 60 days of Bitcoin price data...")
    data = simulate_bitcoin_prices(days=60, initial_price=65000)

    # 2. Calculate MAs
    data = calculate_moving_averages(data)

    # 3. Run Strategy
    run_trading_strategy(data)
