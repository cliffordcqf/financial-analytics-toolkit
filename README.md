# Financial Analytics Toolkit

A lightweight Python toolkit for common corporate-finance calculations. The
first release includes discounted cash flow (DCF) valuation and frequently used
financial ratios, with no third-party runtime dependencies.

## Features

- Present value of projected free cash flows
- Gordon-growth terminal value
- Enterprise value and equity value bridge
- NPV, IRR, and simple payback period
- CAPM cost of equity, after-tax debt cost, and WACC
- Profitability, liquidity, leverage, and efficiency ratios
- Input validation with clear error messages

## Quick start

```python
from src.dcf import enterprise_value
from src.financial_ratios import return_on_equity
from src.investment_metrics import internal_rate_of_return, net_present_value
from src.capital_cost import cost_of_equity_capm, weighted_average_cost_of_capital

valuation = enterprise_value(
    free_cash_flows=[100, 110, 121],
    discount_rate=0.10,
    terminal_growth_rate=0.03,
)

roe = return_on_equity(net_income=25, average_shareholders_equity=100)
npv = net_present_value(0.10, [-1000, 400, 400, 400])
irr = internal_rate_of_return([-1000, 400, 400, 400])
cost_of_equity = cost_of_equity_capm(0.03, 1.2, 0.09)
wacc = weighted_average_cost_of_capital(750, 250, cost_of_equity, 0.05, 0.25)
print(valuation, roe, npv, irr, wacc)
```

Rates are expressed as decimals, so `0.10` means 10%.

## Project structure

```text
src/
  capital_cost.py         # Cost of capital functions
  dcf.py                  # DCF valuation functions
  financial_ratios.py     # Financial ratio functions
  investment_metrics.py   # Capital budgeting functions
requirements.txt          # Runtime dependencies
```

## Disclaimer

This project is for educational and analytical use. It is not financial or
investment advice.

