import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ta import momentum

# Step 1: Import the required libraries

# Step 2: Read the CSV file containing the BTC minute data into a pandas DataFrame
df = pd.read_csv('btc_minute_data_1min.csv')

# Step 3: Convert the 'timestamp' column to a datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Step 4: Calculate the RSI using the 'close' price
df['rsi'] = momentum.rsi(df['close'], window=14)

# Step 5: Create a column for the buy signal based on the RSI condition
df['buy_signal'] = np.where(df['rsi'] <= 30, 1, 0)

# Step 6: Initialize variables for tracking the trading positions, account balance, take profit, and stop loss
position = 0  # 0: out of the market, 1: long position
buy_price = 0  # Initial buy price
balance = df['close'].iloc[0]  # Initial account balance matching the first price in the data
take_profit_pct = 0.015  # Take profit percentage
stop_loss_pct = 0.01  # Stop loss percentage
fee_pct_mk = 0.00  # Trading fee percentage (maker)
fee_pct_tk = 0.00  # Trading fee percentage (taker)
take_profit_hits = 0  # Counter for take profit hits
total_sells = 0  # Counter for total sell signals

capital = [balance] * len(df)  # Initialize the capital list with the same length as the DataFrame

# Step 7: Loop through the DataFrame rows to execute the trading strategy
for i, row in df.iterrows():
    if position == 0 and row['buy_signal'] == 1:
        position = 1
        buy_price = row['close']
        take_profit_price = buy_price * ((1 + take_profit_pct)/((1-fee_pct_tk)*(1-fee_pct_mk)))
        stop_loss_price = buy_price * ((1 - stop_loss_pct)/((1-fee_pct_tk)*(1-fee_pct_mk)))
        balance *= (1 - fee_pct_tk)  # Deduct the trading fee
    elif position == 1 and (row['close'] >= take_profit_price or row['close'] <= stop_loss_price):
        position = 0
        sell_price = row['close']
        balance = (balance / buy_price) * sell_price
        balance *= (1 - fee_pct_mk)  # Deduct the trading fee
        total_sells += 1
        if row['close'] >= take_profit_price:
            take_profit_hits += 1
    capital[i] = balance  # Update the capital list at the current index

# Print the final account balance
print('Final Account Balance:', balance)

# Calculate the percentage of take profit hits
take_profit_percentage = (take_profit_hits / total_sells) * 100
print('Take Profit Hit Percentage:', take_profit_percentage)

# plt.figure(figsize=(16, 8))  # Increase the size of the plot
plt.plot(df['timestamp'], df['close'], label='BTC')
# plt.scatter(df[df['buy_signal'] == 1]['timestamp'], df[df['buy_signal'] == 1]['close'], color='green', marker='^', label='Buy Signal')
plt.plot(df['timestamp'], capital, label='RSI Strategy', color='blue')  # Add the capital changes to the plot
plt.legend()
plt.title('BTC Trading Strategy')
plt.xlabel('Timestamp')
plt.ylabel('Price')
plt.show()
