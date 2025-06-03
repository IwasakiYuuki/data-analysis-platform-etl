import pytest
import pandas as pd
import numpy as np
import datetime

from lib.domains.company.models import (
    CompanyBalanceSheetDataSchema,
    CompanyCashFlowDataSchema,
    CompanyFinancialsDataSchema,
    CompanyInfoDataSchema,
)
from lib.domains.company.providers.yfinance import YFinanceCompanyProvider


@pytest.fixture
def sample_tickers() -> list[str]:
    """
    Fixture to create a sample list of company tickers.
    """
    return ['AAPL', 'MSFT']

@pytest.fixture
def sample_yfinance_info_dict_aapl() -> dict:
    """
    Fixture to create a sample dictionary for yfinance Ticker().info for AAPL.
    """
    return {
        'symbol': 'AAPL',
        'longName': 'Apple Inc.',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'fullTimeEmployees': 164000,
        'marketCap': 3000000000000,
        'trailingPE': 30.0,
        'forwardPE': 28.0,
        'currency': 'USD',
        'exchange': 'NASDAQ',
        'country': 'United States',
        'website': 'https://www.apple.com',
        'someOtherInfo': 'value1', # Include extra fields to test column filtering
        'another_field': 'value2',
    }

@pytest.fixture
def sample_yfinance_info_dict_msft() -> dict:
    """
    Fixture to create a sample dictionary for yfinance Ticker().info for MSFT.
    """
    return {
        'symbol': 'MSFT',
        'longName': 'Microsoft Corp.',
        'sector': 'Technology',
        'industry': 'Software—Infrastructure',
        'fullTimeEmployees': 221000,
        'marketCap': 2500000000000,
        'trailingPE': 35.0,
        'forwardPE': 32.0,
        'currency': 'USD',
        'exchange': 'NASDAQ',
        'country': 'United States',
        'website': 'https://www.microsoft.com',
    }

@pytest.fixture
def sample_yfinance_financials_df_aapl() -> pd.DataFrame:
    """
    Fixture to create a sample DataFrame for yfinance Ticker().financials for AAPL.
    """
    dates = pd.to_datetime(['2023-09-30', '2022-09-30', '2021-09-30', '2020-09-30'])
    data = {
        'Total Revenue': [383285000000, 394328000000, 365817000000, 274515000000],
        'Net Income': [96995000000, 99803000000, 94680000000, 57411000000],
        'Operating Expense': [292785000000, 292785000000, 272785000000, 200785000000],
        'EBIT': [114301000000, 119437000000, 108949000000, 67091000000],
        'Research And Development': [29915000000, 26251000000, 22614000000, 18752000000],
        'Selling General And Administrative': [24932000000, 25109000000, 21973000000, 19916000000],
        'Interest Expense': [3933000000, 2931000000, 2645000000, 2873000000],
        'Income Tax Expense': [16741000000, 19300000000, 14527000000, 9680000000],
        'Other Income Expense': [1000000000, 500000000, 200000000, 100000000], # Example of extra column
    }
    df = pd.DataFrame(data, index=dates)
    df.index.name = 'Date'
    return df

@pytest.fixture
def sample_yfinance_financials_df_msft() -> pd.DataFrame:
    """
    Fixture to create a sample DataFrame for yfinance Ticker().financials for MSFT.
    """
    dates = pd.to_datetime(['2023-06-30', '2022-06-30', '2021-06-30', '2020-06-30'])
    data = {
        'Total Revenue': [211915000000, 198270000000, 168088000000, 143015000000],
        'Net Income': [72361000000, 72738000000, 61271000000, 44281000000],
        'Operating Expense': [140000000000, 120000000000, 100000000000, 80000000000],
        'EBIT': [88000000000, 90000000000, 75000000000, 55000000000],
    }
    df = pd.DataFrame(data, index=dates)
    df.index.name = 'Date'
    return df

@pytest.fixture
def sample_yfinance_balance_sheet_df_aapl() -> pd.DataFrame:
    """
    Fixture to create a sample DataFrame for yfinance Ticker().balance_sheet for AAPL.
    """
    dates = pd.to_datetime(['2023-09-30', '2022-09-30', '2021-09-30', '2020-09-30'])
    data = {
        'Total Assets': [352583000000, 352755000000, 351002000000, 323888000000],
        'Total Liabilities Net Minority Interest': [290437000000, 293603000000, 287912000000, 258549000000],
        'Total Equity Gross Minority Interest': [62146000000, 59152000000, 63090000000, 65339000000],
        'Cash And Cash Equivalents': [29960000000, 23646000000, 34940000000, 38016000000],
        'Accounts Payable': [62611000000, 64115000000, 54763000000, 42296000000],
    }
    df = pd.DataFrame(data, index=dates)
    df.index.name = 'Date'
    return df

@pytest.fixture
def sample_yfinance_cashflow_df_aapl() -> pd.DataFrame:
    """
    Fixture to create a sample DataFrame for yfinance Ticker().cashflow for AAPL.
    """
    dates = pd.to_datetime(['2023-09-30', '2022-09-30', '2021-09-30', '2020-09-30'])
    data = {
        'Operating Cash Flow': [110543000000, 122151000000, 104038000000, 81941000000],
        'Investing Cash Flow': [-11156000000, -22378000000, -14545000000, -11100000000],
        'Financing Cash Flow': [-108470000000, -109736000000, -93354000000, -87664000000],
        'Capital Expenditure': [-10959000000, -10708000000, -11164000000, -7309000000],
        'Dividends Paid': [-15000000000, -14800000000, -14500000000, -14000000000],
    }
    df = pd.DataFrame(data, index=dates)
    df.index.name = 'Date'
    return df


class TestYFinanceCompanyProvider:

    @pytest.fixture()
    def provider(self):
        """
        Fixture to create an instance of YFinanceCompanyProvider.
        """
        return YFinanceCompanyProvider(fetch_delay_sec=0) # No delay for tests

    def test_convert_financial_df_to_schema(self, provider, sample_yfinance_financials_df_aapl):
        """
        Test the _convert_financial_df_to_schema function with a sample DataFrame.
        """
        symbol = 'AAPL'
        period_type = 'annual'
        converted_df = provider._convert_financial_df_to_schema(
            sample_yfinance_financials_df_aapl.copy(), # Use a copy to avoid modifying fixture
            symbol,
            period_type
        )

        assert isinstance(converted_df, pd.DataFrame)
        assert 'report_date' in converted_df.columns
        assert 'symbol' in converted_df.columns
        assert 'period_type' in converted_df.columns
        assert all(col.islower() and '_' not in col.replace(' ', '') for col in converted_df.columns if col not in ['report_date', 'symbol', 'period_type'])
        assert converted_df['symbol'].iloc[0] == symbol
        assert converted_df['period_type'].iloc[0] == period_type
        assert converted_df.index.name is None # Ensure index is reset

    def test_convert_info_dict_to_schema(self, provider, sample_yfinance_info_dict_aapl):
        """
        Test the _convert_info_dict_to_schema function with a sample dictionary.
        """
        symbol = 'AAPL'
        converted_df = provider._convert_info_dict_to_schema(
            sample_yfinance_info_dict_aapl.copy(), # Use a copy to avoid modifying fixture
            symbol
        )

        assert isinstance(converted_df, pd.DataFrame)
        assert 'symbol' in converted_df.columns
        assert 'longname' in converted_df.columns # Check for lowercased and underscore-replaced column
        assert converted_df['symbol'].iloc[0] == symbol
        assert converted_df.shape[0] == 1 # Should be a single row DataFrame
        assert converted_df.index.name is None # Ensure index is reset

    def test_get_company_info_data_success(
        self,
        mocker,
        provider,
        sample_tickers,
        sample_yfinance_info_dict_aapl,
        sample_yfinance_info_dict_msft,
    ):
        """
        Test get_company_info_data with successful data retrieval for multiple tickers.
        """
        mock_ticker_aapl = mocker.MagicMock()
        mock_ticker_aapl.info = sample_yfinance_info_dict_aapl

        mock_ticker_msft = mocker.MagicMock()
        mock_ticker_msft.info = sample_yfinance_info_dict_msft

        # Mock yfinance.Ticker to return specific mock objects based on ticker symbol
        mocker.patch('yfinance.Ticker', side_effect=lambda t: {
            'AAPL': mock_ticker_aapl,
            'MSFT': mock_ticker_msft,
        }.get(t))
        
        # Mock time.sleep to prevent actual delays during tests
        mocker.patch('time.sleep')

        result_df = provider.get_company_info_data(tickers=sample_tickers)

        assert isinstance(result_df, pd.DataFrame)
        CompanyInfoDataSchema.validate(result_df) # Validate against the schema

        assert sorted(result_df['symbol'].unique()) == sorted(sample_tickers)
        assert len(result_df) == len(sample_tickers) # One row per ticker

        # Check if data from both tickers is present
        aapl_data = result_df[result_df['symbol'] == 'AAPL'].iloc[0]
        msft_data = result_df[result_df['symbol'] == 'MSFT'].iloc[0]

        assert aapl_data['longname'] == sample_yfinance_info_dict_aapl['longName']
        assert msft_data['sector'] == sample_yfinance_info_dict_msft['sector']
        
        # Ensure extra columns not in schema are dropped
        assert 'some_other_info' not in result_df.columns
        assert 'another_field' not in result_df.columns


    def test_get_company_financials_data_success(
        self,
        mocker,
        provider,
        sample_tickers,
        sample_yfinance_financials_df_aapl,
        sample_yfinance_financials_df_msft,
    ):
        """
        Test get_company_financials_data with successful data retrieval for multiple tickers.
        """
        mock_ticker_aapl = mocker.MagicMock()
        mock_ticker_aapl.financials = sample_yfinance_financials_df_aapl

        mock_ticker_msft = mocker.MagicMock()
        mock_ticker_msft.financials = sample_yfinance_financials_df_msft

        mocker.patch('yfinance.Ticker', side_effect=lambda t: {
            'AAPL': mock_ticker_aapl,
            'MSFT': mock_ticker_msft,
        }.get(t))
        mocker.patch('time.sleep')

        result_df = provider.get_company_financials_data(tickers=sample_tickers, period_type="annual")

        assert isinstance(result_df, pd.DataFrame)
        CompanyFinancialsDataSchema.validate(result_df)

        assert sorted(result_df['symbol'].unique()) == sorted(sample_tickers)
        assert len(result_df) == len(sample_tickers) * len(sample_yfinance_financials_df_aapl) # 4 annual reports per ticker

        # Check some specific data points
        aapl_revenue = result_df[(result_df['symbol'] == 'AAPL') & (result_df['report_date'] == datetime.date(2023, 9, 30))]['total_revenue'].iloc[0]
        assert aapl_revenue == sample_yfinance_financials_df_aapl.loc['2023-09-30', 'Total Revenue']

        msft_net_income = result_df[(result_df['symbol'] == 'MSFT') & (result_df['report_date'] == datetime.date(2022, 6, 30))]['net_income'].iloc[0]
        assert msft_net_income == sample_yfinance_financials_df_msft.loc['2022-06-30', 'Net Income']
        
        # Ensure extra columns not in schema are dropped
        assert 'other_income_expense' not in result_df.columns


    def test_get_company_balance_sheet_data_success(
        self,
        mocker,
        provider,
        sample_tickers,
        sample_yfinance_balance_sheet_df_aapl,
    ):
        """
        Test get_company_balance_sheet_data with successful data retrieval.
        """
        mock_ticker_aapl = mocker.MagicMock()
        mock_ticker_aapl.balance_sheet = sample_yfinance_balance_sheet_df_aapl

        # Only mock AAPL for simplicity, as MSFT balance sheet fixture is not provided
        mocker.patch('yfinance.Ticker', side_effect=lambda t: {
            'AAPL': mock_ticker_aapl,
            'MSFT': mocker.MagicMock(balance_sheet=pd.DataFrame()), # Simulate no data for MSFT
        }.get(t))
        mocker.patch('time.sleep')

        result_df = provider.get_company_balance_sheet_data(tickers=['AAPL'], period_type="annual")

        assert isinstance(result_df, pd.DataFrame)
        CompanyBalanceSheetDataSchema.validate(result_df)

        assert sorted(result_df['symbol'].unique()) == ['AAPL']
        assert len(result_df) == len(sample_yfinance_balance_sheet_df_aapl)

        aapl_total_assets = result_df[(result_df['symbol'] == 'AAPL') & (result_df['report_date'] == datetime.date(2023, 9, 30))]['total_assets'].iloc[0]
        assert aapl_total_assets == sample_yfinance_balance_sheet_df_aapl.loc['2023-09-30', 'Total Assets']


    def test_get_company_cashflow_data_success(
        self,
        mocker,
        provider,
        sample_tickers,
        sample_yfinance_cashflow_df_aapl,
    ):
        """
        Test get_company_cashflow_data with successful data retrieval.
        """
        mock_ticker_aapl = mocker.MagicMock()
        mock_ticker_aapl.cashflow = sample_yfinance_cashflow_df_aapl

        mocker.patch('yfinance.Ticker', side_effect=lambda t: {
            'AAPL': mock_ticker_aapl,
            'MSFT': mocker.MagicMock(cashflow=pd.DataFrame()), # Simulate no data for MSFT
        }.get(t))
        mocker.patch('time.sleep')

        result_df = provider.get_company_cashflow_data(tickers=['AAPL'], period_type="annual")

        assert isinstance(result_df, pd.DataFrame)
        CompanyCashFlowDataSchema.validate(result_df)

        assert sorted(result_df['symbol'].unique()) == ['AAPL']
        assert len(result_df) == len(sample_yfinance_cashflow_df_aapl)

        aapl_operating_cash_flow = result_df[(result_df['symbol'] == 'AAPL') & (result_df['report_date'] == datetime.date(2023, 9, 30))]['operating_cash_flow'].iloc[0]
        assert aapl_operating_cash_flow == sample_yfinance_cashflow_df_aapl.loc['2023-09-30', 'Operating Cash Flow']


    def test_get_company_data_no_data(self, mocker, provider, sample_tickers):
        """
        Test that an empty DataFrame is returned when yfinance provides no data.
        """
        mock_ticker_aapl = mocker.MagicMock()
        mock_ticker_aapl.info = {} # Empty dict for info
        mock_ticker_aapl.financials = pd.DataFrame() # Empty DataFrame for financials

        mock_ticker_msft = mocker.MagicMock()
        mock_ticker_msft.info = {}
        mock_ticker_msft.financials = pd.DataFrame()

        mocker.patch('yfinance.Ticker', side_effect=lambda t: {
            'AAPL': mock_ticker_aapl,
            'MSFT': mock_ticker_msft,
        }.get(t))
        mocker.patch('time.sleep')
        mocker.patch('lib.domains.company.providers.yfinance.logger.warning') # Mock warning log

        # Test info data
        result_info_df = provider.get_company_info_data(tickers=sample_tickers)
        assert isinstance(result_info_df, pd.DataFrame)
        assert result_info_df.empty
        assert provider.logger.warning.called # Check if warning was logged

        # Test financials data
        result_financials_df = provider.get_company_financials_data(tickers=sample_tickers)
        assert isinstance(result_financials_df, pd.DataFrame)
        assert result_financials_df.empty
        assert provider.logger.warning.called # Check if warning was logged


    def test_get_company_data_exception(self, mocker, provider, sample_tickers):
        """
        Test that exceptions during data fetching are handled and logged.
        """
        mock_ticker_aapl = mocker.MagicMock()
        mock_ticker_aapl.info.side_effect = Exception("Network error for AAPL")
        mock_ticker_aapl.financials.side_effect = Exception("API limit for AAPL")

        mock_ticker_msft = mocker.MagicMock()
        mock_ticker_msft.info = sample_yfinance_info_dict_msft # MSFT works
        mock_ticker_msft.financials = sample_yfinance_financials_df_msft # MSFT works

        mocker.patch('yfinance.Ticker', side_effect=lambda t: {
            'AAPL': mock_ticker_aapl,
            'MSFT': mock_ticker_msft,
        }.get(t))
        mocker.patch('time.sleep')
        mocker.patch('lib.domains.company.providers.yfinance.logger.error') # Mock error log

        # Test info data: AAPL fails, MSFT succeeds
        result_info_df = provider.get_company_info_data(tickers=sample_tickers)
        assert isinstance(result_info_df, pd.DataFrame)
        assert not result_info_df.empty
        assert 'AAPL' not in result_info_df['symbol'].unique() # AAPL data should be missing
        assert 'MSFT' in result_info_df['symbol'].unique() # MSFT data should be present
        assert provider.logger.error.called # Check if error was logged

        # Reset mock for next test
        provider.logger.error.reset_mock()

        # Test financials data: AAPL fails, MSFT succeeds
        result_financials_df = provider.get_company_financials_data(tickers=sample_tickers)
        assert isinstance(result_financials_df, pd.DataFrame)
        assert not result_financials_df.empty
        assert 'AAPL' not in result_financials_df['symbol'].unique() # AAPL data should be missing
        assert 'MSFT' in result_financials_df['symbol'].unique() # MSFT data should be present
        assert provider.logger.error.called # Check if error was logged
