import numpy as np
import pandas as pd
import yfinance as yf
import riskfolio as rf
import matplotlib.pyplot as plot
from warnings import filterwarnings

# Suppress warnings that clutter the output
filterwarnings('ignore') 

# --- 1. Data and Tickers ---
tickers = [
    "ICIL.NS", "UNIPARTS.NS", "KSOLVES.NS", "ACCELYA.NS", "THYROCARE.NS",
    "KAJARIACER.NS", "DALBHARAT.NS", "CYIENT.NS", "WAAREEENER.NS", "IRFC.NS",
    "LTIM.NS", "HDBFS.NS", "PCBL.NS", "INFY.NS", "RECLTD.NS",
    "360ONE.NS", "LTTS.NS", "CRISIL.NS", "CESC.NS", "TANLA.NS"
]

# Fetch 5-year historical data
data = yf.download(tickers, period="5y", interval="1d", auto_adjust=True, threads=True)
returns = data['Close'].pct_change().dropna()

# Current Market Prices (for final sizing and constraints)
cmps = data['Close'].iloc[-1].round(2)

# Dividend Payouts (from your scraped data)
div_payouts = pd.Series([
    6.50, 22.50, 5.00, 40.00, 7.00, 8.00, 4.00, 16.00, 2.00, 1.05, 22.00, 2.00, 6.00, 23.00,
    4.60, 6.00, 18.00, 16.00, 6.00, 6.00
], index=tickers)

# --- 2. Robust Model Parameters & Constraints ---

RM = 'CVaR' # Minimize Conditional Value-at-Risk
rf_rate = 0.0650
alpha = 0.95 # CVaR confidence level

# Constraints
target_min_div_yield = 0.015 # 1.5% target yield (Annualized)
max_leverage = 1.05 # Max 105% invested

# Calculate Current Dividend Yields for the constraint
div_yields = div_payouts / cmps
num_assets = len(tickers)

# --- 3. Portfolio Instantiation and Classic Estimation ---

port = rf.Portfolio(returns=returns, alpha=alpha)

# Estimate historical parameters (Mu and Covariance)
port.assets_stats(method_mu='hist', method_cov='hist')

# --- 4. Adding Quantitative Constraints ---

# 4.1. Maximum Leverage Constraint (W * 1.0 = Max_Leverage)
A_equal = np.ones((1, num_assets))
b_equal = np.array([max_leverage]) 

# 4.2. Minimum Dividend Yield Constraint (W * Y >= Y_target)
# This formally enforces the minimum fundamental metric target.
A_ineq = -div_yields.values.reshape(1, num_assets)
b_ineq = np.array([-target_min_div_yield])

# --- 5. Optimization: Min CVaR with Classic Mu and Constraints ---
w_cvar = port.optimization(
    model='Classic',  # Use standard historical mean returns (Mu)
    rm=RM,            # Minimize CVaR (Downside Risk)
    obj='MinRisk', 
    rf=rf_rate, 
    l=0,
    A_eq=A_equal, 
    b_eq=b_equal,
    A_ineq=A_ineq,
    b_ineq=b_ineq,
    hist=True
)

# --- 6. Final Results and Unit Sizing ---

budget = 10000
w_cvar['weights'] = w_cvar['weights'].astype(float).round(4) * 100

# Create Final DataFrame
final_df = pd.DataFrame(index=w_cvar.index)
final_df['Weights (%)'] = w_cvar['weights']
final_df['Allocation (₹)'] = (w_cvar['weights'] * budget / 100).round(2)
final_df['CMP (₹)'] = cmps
final_df['Div Announced (₹)'] = div_payouts
final_df['Units'] = np.floor(final_df['Allocation (₹)'] / final_df['CMP (₹)']).astype(int)
final_df['Invested (₹)'] = final_df['Units'] * final_df['CMP (₹)']
final_df['Balance (₹)'] = final_df['Allocation (₹)'] - final_df['Invested (₹)']

# Final Metrics
total_invested = final_df['Invested (₹)'].sum()
remaining_cash = budget - total_invested
actual_leverage = total_invested / budget
actual_div_yield = (final_df['Units'] * final_df['Div Announced (₹)']).sum() / total_invested

# --- 7. Print and Plot Results ---
print("\n" + "="*60)
print(f"## OPTIMIZATION SUMMARY (Min CVaR with Constraints: Max {max_leverage}x Leverage & Min {target_min_div_yield*100}% Yield)")
print("="*60)
# Print the final result table
print(final_df) 
print("\n" + "-"*60)
print(f"Initial Budget: ₹{budget:,.2f}")
print(f"Total Invested Amount: ₹{total_invested:,.2f}")
print(f"Effective Leverage: {actual_leverage:.4f}x")
print(f"Remaining Cash/Excess Funds: ₹{remaining_cash:,.2f}")
print(f"Actual Portfolio Dividend Yield: {actual_div_yield:.4f}")
print("-" * 60)

# Plotting the Min-CVaR Portfolio Weights
ax = rf.plot_pie(w=final_df['Weights (%)']/100, title="Min CVaR Constrained Portfolio Weights", others=0.01, nrow=25, cmap="Spectral", height=6, width=10)
plot.show()

# Plotting the Efficient Frontier (Classic Mu, CVaR Risk)
frontier = port.efficient_frontier(model='Classic', rm=RM, points=50, rf=rf_rate, hist=True)
ax = rf.plot_frontier(
    w_frontier=frontier, 
    mu=port.mu, 
    cov=port.cov, 
    returns=returns, 
    rm=RM, 
    rf=rf_rate, 
    cmap='viridis', 
    w=final_df['Weights (%)']/100,
    label='Min CVaR Constrained Portfolio'
)
plot.show()