# Financial Analytics Toolkit

A lightweight Python toolkit for common corporate-finance calculations. The
first release includes discounted cash flow (DCF) valuation and frequently used
financial ratios, with no third-party runtime dependencies.

## Features

- Present value of projected free cash flows
- Gordon-growth terminal value
- Enterprise value and equity value bridge
- Profitability, liquidity, leverage, and efficiency ratios
- Input validation with clear error messages

## Quick start

```python
from src.dcf import enterprise_value
from src.financial_ratios import return_on_equity

valuation = enterprise_value(
    free_cash_flows=[100, 110, 121],
    discount_rate=0.10,
    terminal_growth_rate=0.03,
)

roe = return_on_equity(net_income=25, average_shareholders_equity=100)
print(valuation, roe)
```

Rates are expressed as decimals, so `0.10` means 10%.

## Project structure

```text
src/
  dcf.py                  # DCF valuation functions
  financial_ratios.py     # Financial ratio functions
requirements.txt          # Runtime dependencies
```

## Disclaimer

This project is for educational and analytical use. It is not financial or
investment advice.

