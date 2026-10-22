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
- Scope 1/2/3 inventory, emissions intensity, and reduction tracking
- Simple/log returns, historical volatility, and downside deviation
- IFRS 9 SPPI structured screening with pass/fail/review outcomes
- CAS 22 classification and balanced journal-entry templates
- CAS 6 commissioned-software recognition and CAS 14 contractor journal templates
- CAS 22 three-stage expected credit loss and scenario weighting
- Bond pricing, yield to maturity, duration, and convexity
- Profitability, liquidity, leverage, and efficiency ratios
- Input validation with clear error messages

## Quick start

```python
from src.dcf import enterprise_value
from src.financial_ratios import return_on_equity
from src.investment_metrics import internal_rate_of_return, net_present_value
from src.capital_cost import cost_of_equity_capm, weighted_average_cost_of_capital
from src.carbon_accounting import emissions_from_activity, greenhouse_gas_inventory
from src.risk_metrics import annualized_volatility, simple_returns
from src.sppi import assess_sppi
from src.cas_financial_instruments import classify_financial_asset, initial_recognition_entry
from src.expected_credit_loss import ECLScenario, probability_weighted_ecl
from src.fixed_income import bond_price, modified_duration, yield_to_maturity

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
scope_1 = emissions_from_activity(5_000, 0.20)
inventory = greenhouse_gas_inventory({"scope_1": scope_1, "scope_2": 4_200})
returns = simple_returns([100, 102, 101, 105])
volatility = annualized_volatility(returns)
sppi = assess_sppi(contingent_feature=True, contingent_related_to_basic_lending=False)
plain_sppi = assess_sppi()
classification = classify_financial_asset(plain_sppi, "hold_to_collect")
entry = initial_recognition_entry(classification, fair_value=1_000, transaction_costs=10)
ecl = probability_weighted_ecl([
    ECLScenario("base", 0.7, 0.02, 0.40, 1_000, 0.98),
    ECLScenario("downside", 0.3, 0.08, 0.55, 1_000, 0.95),
])
price = bond_price(1_000, 0.05, 5, 0.06)
ytm = yield_to_maturity(price, 1_000, 0.05, 5)
duration = modified_duration(1_000, 0.05, 5, ytm)
print(valuation, roe, npv, irr, wacc, inventory, volatility, sppi.status, entry, ecl, price, ytm, duration)
```

Rates are expressed as decimals, so `0.10` means 10%.

Carbon calculations are unit-agnostic. Supply activity data and emission
factors in compatible units, and use authoritative factors for the relevant
country, reporting period, and methodology.

## Project structure

```text
src/
  capital_cost.py         # Cost of capital functions
  carbon_accounting.py    # Carbon inventory and intensity functions
  cas_financial_instruments.py  # CAS 22 classification and journal entries
  cas_software_development.py # Commissioned-software accounting
  dcf.py                  # DCF valuation functions
  expected_credit_loss.py # CAS 22 ECL calculations
  fixed_income.py         # Bond pricing and interest-rate risk
  financial_ratios.py     # Financial ratio functions
  investment_metrics.py   # Capital budgeting functions
  risk_metrics.py         # Return and volatility functions
  sppi.py                 # IFRS 9 SPPI screening helper
requirements.txt          # Runtime dependencies
```

## Disclaimer

This project is for educational and analytical use. It is not financial or
investment advice. The SPPI helper is a preliminary screen and does not replace
review of contractual terms or professional accounting judgement. CAS journal
entries are templates whose account mapping must be aligned with the entity's
accounting policies and chart of accounts.


## CAS commissioned software accounting

`src.cas_software_development` reuses the existing `JournalEntry` / `JournalLine`
types. Monetary inputs are numeric, finite, in one consistent currency; costs
and revenue exclude VAT. Rates/tax eligibility are not inferred from a contract.

| Client substance | Treatment for the current cost tranche |
| --- | --- |
| Software service / SaaS access | Expense as consumed; advance payments remain prepayments |
| Acquisition of a controlled software asset | Capitalize if benefits are probable and cost reliably measured |
| Outsourced internal R&D: research or inseparable stages | Expense |
| Internal R&D: development | Capitalize only with general asset recognition and all five CAS 6 development criteria |

The five criteria are technical feasibility, intention to complete, ability to
use/sell, evidence of benefits (including usefulness for internal use), adequate
resources, and reliable measurement of development costs. Flags represent
reviewed evidence, not an automatic legal or accounting conclusion. A contract
called “commissioned development” does not by itself establish its substance.
Apply criteria to each tranche when incurred: earlier expenses cannot be added
back later. Training, maintenance and nonqualifying expenditure must be split
out. No R&D tax super-deduction or corporate income-tax result is implied.

```python
from src.cas_software_development import (
    SoftwareRecognition, software_cost_treatment,
    client_software_cost_entry, client_software_ready_entry,
    software_cash_entry, contractor_software_revenue_entry,
    contractor_software_cost_entry, contractor_software_cost_release_entry,
)

research = SoftwareRecognition("internal_rd", stage="research")
assert software_cost_treatment(research) == "expense"
expense = client_software_cost_entry(research, 100_000)
# Dr 管理费用—研发费用 100,000 / Cr 应付账款 100,000

qualified = SoftwareRecognition(
    nature="internal_rd", stage="development", controlled=True,
    probable_benefits=True, reliable_measurement=True,
    technically_feasible=True, intention_to_complete=True,
    ability_to_use_or_sell=True, adequate_resources=True,
    development_costs_measurable=True,
)
assert software_cost_treatment(qualified) == "capitalize"
client = client_software_cost_entry(
    qualified, 800_000, vat_amount=48_000, deductible_vat=True,
)
# Dr 研发支出—资本化支出 800,000; Dr 进项税额 48,000; Cr 应付账款 848,000
ready = client_software_ready_entry(qualified, 800_000, ready_for_use=True)
# Dr 无形资产—软件 / Cr 研发支出—资本化支出 800,000
payment = software_cash_entry("client", 848_000)
# Dr 应付账款 / Cr 银行存款 848,000

# Separate supplier ledger: assume CAS 14 recognition is established and
# the right to payment is unconditional; VAT is payable at this time.
revenue = contractor_software_revenue_entry(
    800_000, recognition_confirmed=True, vat_amount=48_000,
)
# Dr 应收账款 848,000; Cr 主营业务收入 800,000; Cr 销项税额 48,000
receipt = software_cash_entry("contractor", 848_000)
# Costs of future performance qualify only if ALL CAS 14 article 26 criteria
# hold and no other standard applies. Current/past performance is expensed.
cost = contractor_software_cost_entry(300_000, future_performance_asset=True)
release = contractor_software_cost_release_entry(300_000)
# Dr 合同履约成本 / Cr 应付账款; then Dr 主营业务成本 / Cr 合同履约成本
```

If VAT is not deductible it is included in client expense/asset cost. The VAT
amount above is illustrative, not a prescribed tax rate. Set
`unconditional_receivable=False` for contractor contract assets. Determine
point-in-time vs over-time revenue under CAS 14 independently of client
capitalization; use **incremental** revenue for the current period, never repeat
cumulative revenue. `recognition_confirmed=False` rejects revenue recognition.

`software_cash_entry(..., advance=True)` records client prepayments / contractor
contract liabilities **only before a VAT tax point**. These stateless templates
do not apply advances, reconcile outstanding balances, or prevent duplicate
posting. Offset advances separately against payables / revenue and related VAT;
do not post a full settlement as well. Different VAT and revenue timing, payroll,
multiple performance obligations, financing, impairment, amortization and tax
returns need separate handling. Start amortization when available for use under
the entity's policy; the ready-entry helper only transfers the reconciled asset
balance. Purchased software accumulates in a pending-use intangible subaccount
and transfers to the software subaccount when ready. Expense account mapping
assumes administrative/internal use and should be adapted to actual function.

### Accounting sources

- [CAS 6 — Intangible Assets, articles 3–9, 12–13 and 17](https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46242.htm)
- [CAS 14 — Revenue, articles 4, 11–13, 26–30 and 41](https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201709/t20170907_2694006.htm)
- [Ministry of Finance: 2022 annual-report implementation notice](https://www.mof.gov.cn/jrttts/202212/t20221226_3859893.htm)

Run all tests (including unchanged fixed-income regression tests):

```sh
python -m unittest discover -s tests -v
```
