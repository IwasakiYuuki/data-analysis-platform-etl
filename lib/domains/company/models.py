from datetime import datetime
from typing import Any
from numpy import datetime64
import pandera.pandas as pa
from pandera.typing.pandas import Series

def NullableField(**kwargs):
    """
    Create a nullable field for Pandera schemas.
    This is a convenience function to create nullable fields in Pandera schemas.
    """
    return pa.Field(nullable=True, **kwargs)


class NullableColumn(pa.Column):
    """
    A Pandera column that allows for nullable values.
    This is a convenience class to create nullable columns in Pandera schemas.
    """
    def __init__(self, **kwargs):
        super().__init__(nullable=True, **kwargs)


class CompanyInfoDataSchema(pa.DataFrameModel):
    """
    Schema for company info data.
    """
    symbol: str = pa.Field(description="The symbol of the company. eg. 'AAPL' for Apple inc.")
    shortname: Any = NullableField(description="Short name of the company")
    longbusinesssummary: Any = NullableField(description="Long business summary of the company")
    sector: Any = NullableField(description="Sector of the company")
    industry: Any = NullableField(description="Industry of the company")
    fulltimeemployees: Any = NullableField(description="Number of full-time employees in the company")
    country: Any = NullableField(description="Country where the company is located")
    website: Any = NullableField(description="Website of the company")
    marketcap: Any = NullableField(description="Market capitalization of the company")
    currency: Any = NullableField(description="Currency in which the company operates")
    exchange: Any = NullableField(description="Stock exchange where the company is listed")
    quotetype: Any = NullableField(description="Type of the quote, e.g., 'EQUITY'")
    market: Any = NullableField(description="Market where the company operates")
    address1: Any = NullableField(description="Primary address of the company")
    city: Any = NullableField(description="City where the company is located")
    state: Any = NullableField(description="State where the company is located")
    zip: Any = NullableField(description="ZIP code of the company's location")
    phone: Any = NullableField(description="Phone number of the company")


class CompanyFinancialsDataSchema(pa.DataFrameModel):
    """
    Schema for company financials data.
    """
    report_date: datetime64 = pa.Field(description="Date of the financial report")
    symbol: str = pa.Field(description="The symbol of the company. eg. 'AAPL' for Apple inc.")
    period_type: str = pa.Field(description="Type of the period, e.g., 'annual' or 'quarterly'")
    # Revenue
    total_revenue: Any = NullableField(description="Total revenue of the company")
    operating_revenue: Any = NullableField(description="Operating revenue of the company")
    # Cost of Revenue
    cost_of_revenue: Any = NullableField(description="Cost of revenue for the company")
    reconciled_cost_of_revenue: Any = NullableField(description="Reconciled cost of revenue for the company")
    # Gross Profit
    gross_profit: Any = NullableField(description="Gross profit of the company")
    # Operating Expenses
    operating_expense: Any = NullableField(description="Total operating expenses of the company")
    selling_general_and_administration: Any = NullableField(description="Selling, general and administrative expenses")
    general_and_administrative_expense: Any = NullableField(description="General and administrative expenses")
    selling_and_marketing_expense: Any = NullableField(description="Selling and marketing expenses")
    research_and_development: Any = NullableField(description="Research and development expenses")
    other_operating_expenses: Any = NullableField(description="Other operating expenses")
    rent_expense_supplemental: Any = NullableField(description="Supplemental rent expense")
    rent_and_landing_fees: Any = NullableField(description="Rent and landing fees")
    # Depreciation and Amortization
    depreciation_and_amortization_in_income_statement: Any = NullableField(description="Depreciation and amortization in income statement")
    depreciation_income_statement: Any = NullableField(description="Depreciation in income statement")
    depreciation_amortization_depletion_income_statement: Any = NullableField(description="Depreciation, amortization, and depletion in income statement")
    amortization: Any = NullableField(description="Amortization expense")
    amortization_of_intangibles_income_statement: Any = NullableField(description="Amortization of intangibles in income statement")
    reconciled_depreciation: Any = NullableField(description="Reconciled depreciation")
    # Operating Income
    operating_income: Any = NullableField(description="Operating income of the company")
    total_operating_income_as_reported: Any = NullableField(description="Total operating income as reported")
    # Other Income/Expense
    other_income_expense: Any = NullableField(description="Other income and expenses")
    net_interest_income: Any = NullableField(description="Net interest income")
    interest_income: Any = NullableField(description="Interest income")
    interest_expense: Any = NullableField(description="Interest expense")
    net_non_operating_interest_income_expense: Any = NullableField(description="Net non-operating interest income/expense")
    interest_income_non_operating: Any = NullableField(description="Non-operating interest income")
    interest_expense_non_operating: Any = NullableField(description="Non-operating interest expense")
    other_non_operating_income_expenses: Any = NullableField(description="Other non-operating income and expenses")
    total_other_finance_cost: Any = NullableField(description="Total other finance cost")
    # Unusual Items
    total_unusual_items: Any = NullableField(description="Total unusual items")
    total_unusual_items_excluding_goodwill: Any = NullableField(description="Total unusual items excluding goodwill")
    special_income_charges: Any = NullableField(description="Special income charges")
    other_special_charges: Any = NullableField(description="Other special charges")
    write_off: Any = NullableField(description="Write-off expense")
    restructuring_and_mergern_acquisition: Any = NullableField(description="Restructuring and merger & acquisition expenses")
    impairment_of_capital_assets: Any = NullableField(description="Impairment of capital assets")
    gain_on_sale_of_ppe: Any = NullableField(description="Gain on sale of property, plant, and equipment")
    gain_on_sale_of_business: Any = NullableField(description="Gain on sale of business")
    gain_on_sale_of_security: Any = NullableField(description="Gain on sale of security")
    # Earnings from Equity Interest
    earnings_from_equity_interest: Any = NullableField(description="Earnings from equity interest")
    # Pretax Income
    pretax_income: Any = NullableField(description="Income before tax")
    # Income Tax Expense
    tax_provision: Any = NullableField(description="Income tax provision")
    tax_effect_of_unusual_items: Any = NullableField(description="Tax effect of unusual items")
    tax_rate_for_calcs: Any = NullableField(description="Tax rate used for calculations")
    # Net Income from Continuous Operations
    net_income_continuous_operations: Any = NullableField(description="Net income from continuous operations")
    net_income_from_continuing_operation_net_minority_interest: Any = NullableField(description="Net income from continuing operations, net of minority interest")
    # Net Income from Discontinuous Operations
    net_income_discontinuous_operations: Any = NullableField(description="Net income from discontinuous operations")
    # Net Income
    net_income_from_continuing_and_discontinued_operation: Any = NullableField(description="Net income from continuing and discontinued operations")
    net_income: Any = NullableField(description="Net income")
    normalized_income: Any = NullableField(description="Normalized income")
    # Non-controlling Interests
    minority_interests: Any = NullableField(description="Minority interests")
    net_income_including_noncontrolling_interests: Any = NullableField(description="Net income including noncontrolling interests")
    # Net Income Attributable to Common Stockholders
    otherunder_preferred_stock_dividend: Any = NullableField(description="Other/under preferred stock dividend")
    net_income_common_stockholders: Any = NullableField(description="Net income attributable to common stockholders")
    diluted_ni_availto_com_stockholders: Any = NullableField(description="Diluted net income available to common stockholders")
    # Per Share Information
    basic_average_shares: Any = NullableField(description="Basic average shares outstanding")
    diluted_average_shares: Any = NullableField(description="Diluted average shares outstanding")
    basic_eps: Any = NullableField(description="Basic earnings per share")
    diluted_eps: Any = NullableField(description="Diluted earnings per share")
    # EBITDA / EBIT
    ebitda: Any = NullableField(description="Earnings Before Interest, Taxes, Depreciation, and Amortization")
    normalized_ebitda: Any = NullableField(description="Normalized Earnings Before Interest, Taxes, Depreciation, and Amortization")
    ebit: Any = NullableField(description="Earnings Before Interest and Taxes")
    # Other
    total_expenses: Any = NullableField(description="Total expenses of the company")


class CompanyBalanceSheetDataSchema(pa.DataFrameModel):
    """
    Schema for company balance sheet data.
    """

    report_date: datetime64 = pa.Field(description="Date of the financial report")
    symbol: str = pa.Field(description="The symbol of the company. eg. 'AAPL' for Apple inc.")
    period_type: str = pa.Field(description="Type of the period, e.g., 'annual' or 'quarterly'")
    # Current Assets
    current_assets: Any = NullableField(description="Total current assets of the company")
    cash_cash_equivalents_and_short_term_investments: Any = NullableField(description="Cash, cash equivalents, and short-term investments")
    cash_and_cash_equivalents: Any = NullableField(description="Cash and cash equivalents")
    restricted_cash: Any = NullableField(description="Restricted cash")
    cash_financial: Any = NullableField(description="Cash (financial institutions)")
    cash_cash_equivalents_and_federal_funds_sold: Any = NullableField(description="Cash, cash equivalents, and federal funds sold")
    other_short_term_investments: Any = NullableField(description="Other short-term investments")
    trading_securities: Any = NullableField(description="Trading securities")
    receivables: Any = NullableField(description="Total receivables")
    accounts_receivable: Any = NullableField(description="Accounts receivable")
    gross_accounts_receivable: Any = NullableField(description="Gross accounts receivable")
    allowance_for_doubtful_accounts_receivable: Any = NullableField(description="Allowance for doubtful accounts receivable")
    other_receivables: Any = NullableField(description="Other receivables")
    taxes_receivable: Any = NullableField(description="Taxes receivable")
    inventory: Any = NullableField(description="Total inventory")
    finished_goods: Any = NullableField(description="Finished goods inventory")
    work_in_process: Any = NullableField(description="Work in process inventory")
    raw_materials: Any = NullableField(description="Raw materials inventory")
    other_inventories: Any = NullableField(description="Other inventories")
    prepaid_assets: Any = NullableField(description="Prepaid assets")
    current_deferred_assets: Any = NullableField(description="Current deferred assets")
    assets_held_for_sale_current: Any = NullableField(description="Assets held for sale (current)")
    hedging_assets_current: Any = NullableField(description="Hedging assets (current)")
    other_current_assets: Any = NullableField(description="Other current assets")
    # Non-current Assets
    total_non_current_assets: Any = NullableField(description="Total non-current assets of the company")
    net_ppe: Any = NullableField(description="Net property, plant, and equipment")
    gross_ppe: Any = NullableField(description="Gross property, plant, and equipment")
    accumulated_depreciation: Any = NullableField(description="Accumulated depreciation")
    properties: Any = NullableField(description="Total properties")
    land_and_improvements: Any = NullableField(description="Land and improvements")
    buildings_and_improvements: Any = NullableField(description="Buildings and improvements")
    machinery_furniture_equipment: Any = NullableField(description="Machinery, furniture, and equipment")
    construction_in_progress: Any = NullableField(description="Construction in progress")
    other_properties: Any = NullableField(description="Other properties")
    investment_properties: Any = NullableField(description="Investment properties")
    goodwill_and_other_intangible_assets: Any = NullableField(description="Goodwill and other intangible assets")
    goodwill: Any = NullableField(description="Goodwill")
    other_intangible_assets: Any = NullableField(description="Other intangible assets")
    investments_and_advances: Any = NullableField(description="Investments and advances")
    investmentin_financial_assets: Any = NullableField(description="Investment in financial assets")
    available_for_sale_securities: Any = NullableField(description="Available-for-sale securities")
    long_term_equity_investment: Any = NullableField(description="Long-term equity investment")
    investments_in_other_ventures_under_equity_method: Any = NullableField(description="Investments in other ventures under equity method")
    investmentsin_subsidiariesat_cost: Any = NullableField(description="Investments in subsidiaries at cost")
    other_investments: Any = NullableField(description="Other investments")
    non_current_deferred_taxes_assets: Any = NullableField(description="Non-current deferred tax assets")
    defined_pension_benefit: Any = NullableField(description="Defined pension benefit assets")
    non_current_prepaid_assets: Any = NullableField(description="Non-current prepaid assets")
    non_current_deferred_assets: Any = NullableField(description="Non-current deferred assets")
    other_non_current_assets: Any = NullableField(description="Other non-current assets")
    # Total Assets
    total_assets: Any = NullableField(description="Total assets of the company")
    # Current Liabilities
    current_liabilities: Any = NullableField(description="Total current liabilities of the company")
    current_debt_and_capital_lease_obligation: Any = NullableField(description="Current debt and capital lease obligation")
    current_debt: Any = NullableField(description="Current debt")
    current_capital_lease_obligation: Any = NullableField(description="Current capital lease obligation")
    payables: Any = NullableField(description="Total payables")
    accounts_payable: Any = NullableField(description="Accounts payable")
    other_payable: Any = NullableField(description="Other payable")
    total_tax_payable: Any = NullableField(description="Total tax payable")
    current_provisions: Any = NullableField(description="Current provisions")
    pensionand_other_post_retirement_benefit_plans_current: Any = NullableField(description="Pension and other post-retirement benefit plans (current)")
    other_current_liabilities: Any = NullableField(description="Other current liabilities")
    derivative_product_liabilities: Any = NullableField(description="Derivative product liabilities")
    # Non-current Liabilities
    total_non_current_liabilities_net_minority_interest: Any = NullableField(description="Total non-current liabilities, net of minority interest")
    long_term_debt_and_capital_lease_obligation: Any = NullableField(description="Long-term debt and capital lease obligation")
    long_term_debt: Any = NullableField(description="Long-term debt")
    long_term_capital_lease_obligation: Any = NullableField(description="Long-term capital lease obligation")
    non_current_deferred_taxes_liabilities: Any = NullableField(description="Non-current deferred tax liabilities")
    non_current_deferred_revenue: Any = NullableField(description="Non-current deferred revenue")
    non_current_pension_and_other_postretirement_benefit_plans: Any = NullableField(description="Non-current pension and other postretirement benefit plans")
    long_term_provisions: Any = NullableField(description="Long-term provisions")
    tradeand_other_payables_non_current: Any = NullableField(description="Trade and other payables (non-current)")
    other_non_current_liabilities: Any = NullableField(description="Other non-current liabilities")
    # Total Liabilities
    total_liabilities_net_minority_interest: Any = NullableField(description="Total liabilities, net of minority interest")
    net_debt: Any = NullableField(description="Net debt")
    total_debt: Any = NullableField(description="Total debt")
    capital_lease_obligations: Any = NullableField(description="Capital lease obligations")
    # Equity and Capital Surplus
    total_equity_gross_minority_interest: Any = NullableField(description="Total equity, gross of minority interest")
    stockholders_equity: Any = NullableField(description="Total stockholders' equity")
    common_stock_equity: Any = NullableField(description="Common stock equity")
    capital_stock: Any = NullableField(description="Capital stock")
    common_stock: Any = NullableField(description="Common stock")
    additional_paid_in_capital: Any = NullableField(description="Additional paid-in capital")
    share_issued: Any = NullableField(description="Shares issued")
    ordinary_shares_number: Any = NullableField(description="Number of ordinary shares")
    # Retained Earnings
    retained_earnings: Any = NullableField(description="Retained earnings")
    # Other Comprehensive Income
    fixed_assets_revaluation_reserve: Any = NullableField(description="Fixed assets revaluation reserve")
    other_equity_interest: Any = NullableField(description="Other equity interest")
    # Treasury Stock
    treasury_stock: Any = NullableField(description="Treasury stock")
    treasury_shares_number: Any = NullableField(description="Number of treasury shares")
    # Non-controlling Interests
    minority_interest: Any = NullableField(description="Minority interest")
    # Total Net Assets (or Total Equity)
    total_capitalization: Any = NullableField(description="Total capitalization")
    tangible_book_value: Any = NullableField(description="Tangible book value")
    invested_capital: Any = NullableField(description="Invested capital")
    working_capital: Any = NullableField(description="Working capital")
    net_tangible_assets: Any = NullableField(description="Net tangible assets")


class CompanyCashFlowDataSchema(pa.DataFrameModel):
    """
    Schema for company cash flow data.
    """
    report_date: datetime64 = pa.Field(description="Date of the financial report")
    symbol: str = pa.Field(description="The symbol of the company. eg. 'AAPL' for Apple inc.")
    period_type: str = pa.Field(description="Type of the period, e.g., 'annual' or 'quarterly'")
    # Operating Activities
    operating_cash_flow: Any = NullableField(description="Cash flow from operating activities")
    net_income_from_continuing_operations: Any = NullableField(description="Net income from continuing operations")
    depreciation_and_amortization: Any = NullableField(description="Depreciation and amortization")
    depreciation: Any = NullableField(description="Depreciation expense")
    amortization_cash_flow: Any = NullableField(description="Amortization expense (cash flow)")
    deferred_tax: Any = NullableField(description="Deferred tax")
    gain_loss_on_sale_of_ppe: Any = NullableField(description="Gain or loss on sale of property, plant, and equipment")
    gain_loss_on_investment_securities: Any = NullableField(description="Gain or loss on investment securities")
    gain_loss_on_sale_of_business: Any = NullableField(description="Gain or loss on sale of business")
    net_foreign_currency_exchange_gain_loss: Any = NullableField(description="Net foreign currency exchange gain or loss")
    stock_based_compensation: Any = NullableField(description="Stock-based compensation expense")
    provisionand_write_offof_assets: Any = NullableField(description="Provision and write-off of assets")
    pension_and_employee_benefit_expense: Any = NullableField(description="Pension and employee benefit expense")
    other_non_cash_items: Any = NullableField(description="Other non-cash items")
    change_in_working_capital: Any = NullableField(description="Change in working capital")
    change_in_receivables: Any = NullableField(description="Change in receivables")
    change_in_inventory: Any = NullableField(description="Change in inventory")
    change_in_payable: Any = NullableField(description="Change in payables")
    change_in_prepaid_assets: Any = NullableField(description="Change in prepaid assets")
    change_in_accrued_expense: Any = NullableField(description="Change in accrued expense")
    change_in_other_current_assets: Any = NullableField(description="Change in other current assets")
    change_in_other_current_liabilities: Any = NullableField(description="Change in other current liabilities")
    taxes_refund_paid: Any = NullableField(description="Taxes refund paid")
    dividend_received_cfo: Any = NullableField(description="Dividends received (operating activities)")
    interest_received_cfo: Any = NullableField(description="Interest received (operating activities)")
    interest_paid_cfo: Any = NullableField(description="Interest paid (operating activities)")
    # Investing Activities
    investing_cash_flow: Any = NullableField(description="Cash flow from investing activities")
    capital_expenditure: Any = NullableField(description="Capital expenditure")
    capital_expenditure_reported: Any = NullableField(description="Capital expenditure as reported")
    net_ppe_purchase_and_sale: Any = NullableField(description="Net property, plant, and equipment purchase and sale")
    purchase_of_ppe: Any = NullableField(description="Purchase of property, plant, and equipment")
    sale_of_ppe: Any = NullableField(description="Sale of property, plant, and equipment")
    net_investment_purchase_and_sale: Any = NullableField(description="Net investment purchase and sale")
    purchase_of_investment: Any = NullableField(description="Purchase of investment")
    sale_of_investment: Any = NullableField(description="Sale of investment")
    net_investment_properties_purchase_and_sale: Any = NullableField(description="Net investment properties purchase and sale")
    purchase_of_investment_properties: Any = NullableField(description="Purchase of investment properties")
    sale_of_investment_properties: Any = NullableField(description="Sale of investment properties")
    net_intangibles_purchase_and_sale: Any = NullableField(description="Net intangibles purchase and sale")
    purchase_of_intangibles: Any = NullableField(description="Purchase of intangibles")
    sale_of_intangibles: Any = NullableField(description="Sale of intangibles")
    net_business_purchase_and_sale: Any = NullableField(description="Net business purchase and sale")
    purchase_of_business: Any = NullableField(description="Purchase of business")
    sale_of_business: Any = NullableField(description="Sale of business")
    dividends_received_cfi: Any = NullableField(description="Dividends received (investing activities)")
    interest_received_cfi: Any = NullableField(description="Interest received (investing activities)")
    net_other_investing_changes: Any = NullableField(description="Net other investing changes")
    # Financing Activities
    financing_cash_flow: Any = NullableField(description="Cash flow from financing activities")
    net_issuance_payments_of_debt: Any = NullableField(description="Net issuance and payments of debt")
    issuance_of_debt: Any = NullableField(description="Issuance of debt")
    repayment_of_debt: Any = NullableField(description="Repayment of debt")
    net_long_term_debt_issuance: Any = NullableField(description="Net long-term debt issuance")
    long_term_debt_issuance: Any = NullableField(description="Long-term debt issuance")
    long_term_debt_payments: Any = NullableField(description="Long-term debt payments")
    net_short_term_debt_issuance: Any = NullableField(description="Net short-term debt issuance")
    short_term_debt_issuance: Any = NullableField(description="Short-term debt issuance")
    short_term_debt_payments: Any = NullableField(description="Short-term debt payments")
    net_common_stock_issuance: Any = NullableField(description="Net common stock issuance")
    issuance_of_capital_stock: Any = NullableField(description="Issuance of capital stock")
    common_stock_issuance: Any = NullableField(description="Common stock issuance")
    repurchase_of_capital_stock: Any = NullableField(description="Repurchase of capital stock")
    common_stock_payments: Any = NullableField(description="Common stock payments")
    cash_dividends_paid: Any = NullableField(description="Cash dividends paid")
    common_stock_dividend_paid: Any = NullableField(description="Common stock dividend paid")
    interest_paid_cff: Any = NullableField(description="Interest paid (financing activities)")
    net_other_financing_charges: Any = NullableField(description="Net other financing charges")
    # Net Change in Cash
    changes_in_cash: Any = NullableField(description="Net change in cash and cash equivalents")
    effect_of_exchange_rate_changes: Any = NullableField(description="Effect of exchange rate changes on cash")
    beginning_cash_position: Any = NullableField(description="Beginning cash position")
    end_cash_position: Any = NullableField(description="End cash position")
    other_cash_adjustment_outside_changein_cash: Any = NullableField(description="Other cash adjustment outside change in cash")
    # Free Cash Flow
    free_cash_flow: Any = NullableField(description="Free cash flow")
