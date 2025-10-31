import yfinance as yf
import numpy as np
import pandas as pd
import datetime
from datetime import date
import time
from py_vollib.black_scholes.greeks import analytical as greeks
import colorama
from colorama import Fore, Style


def print_three_side_by_side(df1, df2, df3, title1, title2, title3):
    """Prints three pandas DataFrames side-by-side."""
    
    # Set display options temporarily for clean output
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        df1_str = df1.to_string()
        df2_str = df2.to_string(header=True)
        df3_str = df3.to_string()
    
    lines1 = df1_str.split('\n')
    lines2 = df2_str.split('\n')
    lines3 = df3_str.split('\n')

    # Calculate required padding widths
    max_len1 = max(len(line) for line in lines1)
    max_len2 = max(len(line) for line in lines2)
    
    # Define the print format string for alignment
    format_str = f"{{:<{max_len1}}}  {{:<{max_len2}}}  {{}}"
    
    # Print the combined titles
    print(format_str.format(title1, title2, title3))
    #print("-" * (max_len1 + max_len2 + len(title3) + 6)) # Separator line
    
    # Prepare content lines for alignment
    max_lines = max(len(lines1), len(lines2), len(lines3))
    
    lines1.extend([''] * (max_lines - len(lines1)))
    lines2.extend([''] * (max_lines - len(lines2)))
    lines3.extend([''] * (max_lines - len(lines3)))

    # Print the content line by line
    # Note: df2 does NOT have its header printed in df2_str, so we print the header manually here.
    
    # Print Headers (Line 1 of df1_str and df3_str, Line 0 of df2_str is body)
    print(format_str.format(lines1[0], lines2[0], lines3[0]))
    
    # Print Separator (Line 2 of df1_str and df3_str, Line 1 of df2_str is body)
    print(format_str.format(lines1[1], lines2[1], lines3[1]))

    # Print Body (Starting from Line 2 of all three lists)
    for line1, line2, line3 in zip(lines1[2:], lines2[2:], lines3[2:]):
        print(format_str.format(line1, line2, line3))
        
    print("\n")


comp = input("Enter Ticker symbol: ")
nifty  = yf.Ticker(f"{comp}")
data = nifty.history(period="5y")
option_chain = nifty.option_chain()
calls = option_chain.calls
puts = option_chain.puts

calls = option_chain.calls
puts = option_chain.puts
calls['BA_Spread'] = calls['ask'] - calls['bid']
puts['BA_Spread'] = puts['ask'] - puts['bid']
sorted_calls = calls.drop(['currency', 'inTheMoney', 'contractSize', 'lastTradeDate', 'bid', 'ask', 'volume', 'change', 'percentChange', 'lastPrice'], axis=1)
sorted_puts = puts.drop(['currency', 'inTheMoney', 'contractSize', 'lastTradeDate', 'bid', 'ask', 'volume', 'change', 'percentChange', 'lastPrice', 'contractSymbol'], axis=1)
required_chain = sorted_calls.merge(sorted_puts, on='strike', suffixes=('_call', '_put'))




s = data['Close'].iloc[-1]
rf = 0.065
exp_date = nifty.options[0]
exp_date = date.fromisoformat(exp_date)
time_to_expiry = (exp_date - date.today()).days
t = time_to_expiry/365.0

greeks_input = pd.concat([
    calls[['strike', 'impliedVolatility']].assign(contract_type='call'),
    puts[['strike', 'impliedVolatility']].assign(contract_type='put')
], ignore_index=True)

# Rename the implied volatility column for consistent access
greeks_input.rename(columns={'impliedVolatility': 'sigma'}, inplace=True)

def calculate_greeks(row, s, r, t):
    K = row['strike']
    sigma = row['sigma']
    flag = 'c' if row['contract_type'] == 'call' else 'p'

    delta = greeks.delta(flag, s, K, t, r, sigma)
    gamma = greeks.gamma(flag, s, K, t, r, sigma)
    theta = greeks.theta(flag, s, K, t, r, sigma)
    vega = greeks.vega(flag, s, K, t, r, sigma)
    rho = greeks.rho(flag, s, K, t, r, sigma)

    return {
        'Delta' : delta,
        'Gamma' : gamma,
        'Theta' : theta,
        'Vega' : vega,
        'Rho' : rho
    }

greeks_df_list = greeks_input.apply(
    calculate_greeks,
    args=(s, rf, t),
    axis=1,
    result_type='expand'
)

greeks_df = pd.concat([greeks_input, greeks_df_list], axis=1).round(4)
call_greeks_df = greeks_df[greeks_df['contract_type'] == 'call'].drop(columns=['contract_type'])
put_greeks_df = greeks_df[greeks_df['contract_type'] == 'put'].drop(columns=['contract_type'])
top_15_call_strikes = calls.nlargest(15, 'openInterest')['strike'].tolist()
top_15_put_strikes = puts.nlargest(15, 'openInterest')['strike'].tolist()

filtered_call_greeks_df = call_greeks_df[
    call_greeks_df['strike'].isin(top_15_call_strikes)
].reset_index(drop=True)
filtered_put_greeks_df = put_greeks_df[
    put_greeks_df['strike'].isin(top_15_put_strikes)
].reset_index(drop=True)



comp_name = comp
cmp = data['Close'].iloc[-1] 
avg_implied_vol = (calls['impliedVolatility'].mean() + puts['impliedVolatility'].mean()) / 2

high_call_oi_strike = calls.loc[calls['openInterest'].idxmax(), 'strike']
high_put_oi_strike = puts.loc[puts['openInterest'].idxmax(), 'strike']
# Note: This is less readable, but uses correct ternary syntax.
volume_spike_call = True if calls[calls['strike'] == high_call_oi_strike]['volume'].iloc[0] > calls['volume'].mean() else False
volume_spike_put = True if puts[puts['strike'] == high_put_oi_strike]['volume'].iloc[0] > puts['volume'].mean() else False
# 3. Construct the Summary DataFrame (Transpose it immediately for a vertical display)
summary_data = {
    'Name': [comp_name],
    'CMP': [f"${cmp:.2f}"],
    'Avg. Implied Vol': [f"{avg_implied_vol:.2%}"],
    'High Call OI Strike': [high_call_oi_strike],
    'High Put OI Strike': [high_put_oi_strike],
    'Call Volume Spike' : [volume_spike_call],
    'Put Volume Spike' : [volume_spike_put]
}
summary_df = pd.DataFrame(summary_data).T.rename(columns={0: 'Value'})


equal_tos = 152
dashes = 68

print("\n" + "="*equal_tos)
print(" "*dashes + "OPTION CHAIN")
print("="*equal_tos)

#pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 10)
print(required_chain)

print("\n" + "=" * 120 + " "*2 + "="*27)
print( " "*56 +"Greeks")
print("=" * 120 + " "*2 + "="*27)

print_three_side_by_side(
    filtered_call_greeks_df,
    filtered_put_greeks_df,
    summary_df, 
    title1=Fore.GREEN + " "*28 + "CALLS" + " "*15 + Style.RESET_ALL,
    title2=Fore.RED + " "*35 + "PUTS" + " "*20 + Style.RESET_ALL,
    title3=Fore.YELLOW + " "*20 + "ANALYSIS SUMMARY" + Style.RESET_ALL
)

time.sleep(600)