import pytest
import numpy as np
import pandas as pd

from lib.domains.forex.models import ForexDataSchema
from lib.domains.forex.providers.yfinance import YFinanceForexProvider


@pytest.fixture
def sample_tickers1() -> list[str]:
    """
    Fixture to create a sample list of forex tickers.
    """
    return ['JPY=X', 'EURUSD=X']

@pytest.fixture
def sample_tickers2() -> list[str]:
    """
    Fixture to create another sample list of forex tickers.
    """
    return ['JPY=X', 'EURUSD=X', 'GBPUSD=X', 'AUDUSD=X', 'NZDUSD=X', 'EURJPY=X', 'GBPJPY=X']

@pytest.fixture
def sample_yfinance_forex_data_df1() -> pd.DataFrame:
    """
    Fixture to create a sample DataFrame for Yfinance forex data.

    Below is an example of the DataFrame structure:
    Price                            Close                     High                    Low               Open             Volume
    Ticker                           JPY=X      EURUSD=X       JPY=X      EURUSD=X     JPY=X      EURUSD=X JPY=X      EURUSD=X JPY=X    EURUSD=X
    Datetime
    2025-04-07 00:05:00+00:00  151.80         1.0850  151.85         1.0855  151.75         1.0845 151.78      1.0848 100000    50000
    2025-04-07 00:10:00+00:00  151.90         1.0860  151.95         1.0865  151.85         1.0855 151.88      1.0858 120000    60000
    ...
    """
    tickers = ['JPY=X', 'EURUSD=X']
    price_metrics = ['Close', 'High', 'Low', 'Open', 'Volume']

    columns = pd.MultiIndex.from_product(
        [price_metrics, tickers],
        names=['Price', 'Ticker']
    )

    index = pd.to_datetime(pd.date_range('2025-04-07 00:05:00+00:00', periods=10, freq='5min'))
    index.name = 'Datetime'
    
    data_values = np.zeros((len(index), len(price_metrics) * len(tickers)))
    
    # Data for JPY=X
    ticker_idx_jpy = tickers.index('JPY=X')
    col_offset = len(tickers) 
    data_values[:, price_metrics.index('Close') * col_offset + ticker_idx_jpy] = np.random.uniform(151.5, 152.5, size=len(index))
    data_values[:, price_metrics.index('High') * col_offset + ticker_idx_jpy] = np.random.uniform(151.6, 152.6, size=len(index))
    data_values[:, price_metrics.index('Low') * col_offset + ticker_idx_jpy] = np.random.uniform(151.4, 152.4, size=len(index))
    data_values[:, price_metrics.index('Open') * col_offset + ticker_idx_jpy] = np.random.uniform(151.5, 152.5, size=len(index))
    data_values[:, price_metrics.index('Volume') * col_offset + ticker_idx_jpy] = np.random.randint(50000, 200000, size=len(index))

    # Data for EURUSD=X
    ticker_idx_eurusd = tickers.index('EURUSD=X')
    data_values[:, price_metrics.index('Close') * col_offset + ticker_idx_eurusd] = np.random.uniform(1.0800, 1.0900, size=len(index))
    data_values[:, price_metrics.index('High') * col_offset + ticker_idx_eurusd] = np.random.uniform(1.0805, 1.0905, size=len(index))
    data_values[:, price_metrics.index('Low') * col_offset + ticker_idx_eurusd] = np.random.uniform(1.0795, 1.0895, size=len(index))
    data_values[:, price_metrics.index('Open') * col_offset + ticker_idx_eurusd] = np.random.uniform(1.0800, 1.0900, size=len(index))
    data_values[:, price_metrics.index('Volume') * col_offset + ticker_idx_eurusd] = np.random.randint(20000, 80000, size=len(index))

    # Introduce NaN values for the first row of EURUSD=X to simulate missing data
    if len(index) > 0:
        data_values[0, price_metrics.index('Close') * col_offset + ticker_idx_eurusd] = np.nan
        data_values[0, price_metrics.index('High') * col_offset + ticker_idx_eurusd] = np.nan
        data_values[0, price_metrics.index('Low') * col_offset + ticker_idx_eurusd] = np.nan
        data_values[0, price_metrics.index('Open') * col_offset + ticker_idx_eurusd] = np.nan
        data_values[0, price_metrics.index('Volume') * col_offset + ticker_idx_eurusd] = np.nan

    df = pd.DataFrame(data_values, index=index, columns=columns)
    
    for ticker in tickers:
        df[('Volume', ticker)] = df[('Volume', ticker)].astype('Int64')

    return df

@pytest.fixture
def sample_yfinance_forex_data_df2() -> pd.DataFrame:
    """
    Fixture to create a sample DataFrame for Yfinance forex data with 2 DIFFERENT tickers.
    Tickers: ['GBPUSD=X', 'AUDUSD=X']
    """
    tickers = ['GBPUSD=X', 'AUDUSD=X']
    price_metrics = ['Close', 'High', 'Low', 'Open', 'Volume']
    num_rows = 5

    columns = pd.MultiIndex.from_product(
        [price_metrics, tickers],
        names=['Price', 'Ticker']
    )

    index = pd.to_datetime(pd.date_range('2025-05-01 09:00:00+00:00', periods=num_rows, freq='h'))
    index.name = 'Datetime'

    data_values = np.zeros((len(index), len(price_metrics) * len(tickers)))

    col_offset = len(tickers)

    ticker_idx_gbpusd = tickers.index('GBPUSD=X')
    data_values[:, price_metrics.index('Close') * col_offset + ticker_idx_gbpusd] = [1.2500, 1.2515, 1.2520, 1.2510, 1.2530]
    data_values[:, price_metrics.index('High') * col_offset + ticker_idx_gbpusd] = [1.2505, 1.2520, 1.2525, 1.2515, 1.2535]
    data_values[:, price_metrics.index('Low') * col_offset + ticker_idx_gbpusd] = [1.2495, 1.2500, 1.2510, 1.2505, 1.2520]
    data_values[:, price_metrics.index('Open') * col_offset + ticker_idx_gbpusd] = [1.2498, 1.2502, 1.2518, 1.2512, 1.2525]
    data_values[:, price_metrics.index('Volume') * col_offset + ticker_idx_gbpusd] = [100000, 120000, 90000, 110000, 130000]

    ticker_idx_audusd = tickers.index('AUDUSD=X')
    data_values[:, price_metrics.index('Close') * col_offset + ticker_idx_audusd] = [0.6500, 0.6510, 0.6525, 0.6515, 0.6530]
    data_values[:, price_metrics.index('High') * col_offset + ticker_idx_audusd] = [0.6505, 0.6518, 0.6530, 0.6520, 0.6535]
    data_values[:, price_metrics.index('Low') * col_offset + ticker_idx_audusd] = [0.6490, 0.6495, 0.6510, 0.6505, 0.6515]
    data_values[:, price_metrics.index('Open') * col_offset + ticker_idx_audusd] = [0.6498, 0.6502, 0.6518, 0.6510, 0.6525]
    data_values[:, price_metrics.index('Volume') * col_offset + ticker_idx_audusd] = [50000, 60000, 45000, 55000, 65000]

    if num_rows > 0:
        data_values[0, price_metrics.index('Close') * col_offset + ticker_idx_audusd] = np.nan
        data_values[0, price_metrics.index('Volume') * col_offset + ticker_idx_audusd] = np.nan

    df = pd.DataFrame(data_values, index=index, columns=columns)
    
    for ticker in tickers:
        df[('Volume', ticker)] = df[('Volume', ticker)].astype('Int64')

    return df


@pytest.fixture
def sample_yfinance_forex_data_df3() -> pd.DataFrame:
    """
    Fixture to create a sample DataFrame for Yfinance forex data with 3 DIFFERENT tickers.
    Tickers: ['NZDUSD=X', 'EURJPY=X', 'GBPJPY=X']
    """
    tickers = ['NZDUSD=X', 'EURJPY=X', 'GBPJPY=X']
    price_metrics = ['Close', 'High', 'Low', 'Open', 'Volume']
    num_rows = 7

    columns = pd.MultiIndex.from_product(
        [price_metrics, tickers],
        names=['Price', 'Ticker']
    )

    index = pd.to_datetime(pd.date_range('2025-05-02 10:00:00+00:00', periods=num_rows, freq='30min'))
    index.name = 'Datetime'

    data_values = np.zeros((len(index), len(price_metrics) * len(tickers)))

    col_offset = len(tickers)

    ticker_idx_nzdusd = tickers.index('NZDUSD=X')
    data_values[:, price_metrics.index('Close') * col_offset + ticker_idx_nzdusd] = [0.6000, 0.6010, 0.6020, 0.6015, 0.6030, 0.6025, 0.6040]
    data_values[:, price_metrics.index('High') * col_offset + ticker_idx_nzdusd] = [0.6005, 0.6015, 0.6025, 0.6020, 0.6035, 0.6030, 0.6045]
    data_values[:, price_metrics.index('Low') * col_offset + ticker_idx_nzdusd] = [0.5995, 0.6000, 0.6010, 0.6005, 0.6015, 0.6010, 0.6025]
    data_values[:, price_metrics.index('Open') * col_offset + ticker_idx_nzdusd] = [0.5998, 0.6002, 0.6018, 0.6012, 0.6025, 0.6020, 0.6035]
    data_values[:, price_metrics.index('Volume') * col_offset + ticker_idx_nzdusd] = [200000, 210000, 190000, 205000, 220000, 215000, 230000]

    ticker_idx_eurjpy = tickers.index('EURJPY=X')
    data_values[:, price_metrics.index('Close') * col_offset + ticker_idx_eurjpy] = [165.00, 165.50, 166.00, 165.80, 166.50, 166.20, 167.00]
    data_values[:, price_metrics.index('High') * col_offset + ticker_idx_eurjpy] = [165.30, 165.80, 166.30, 166.00, 166.80, 166.50, 167.30]
    data_values[:, price_metrics.index('Low') * col_offset + ticker_idx_eurjpy] = [164.50, 164.80, 165.20, 165.00, 165.50, 165.30, 166.00]
    data_values[:, price_metrics.index('Open') * col_offset + ticker_idx_eurjpy] = [164.80, 165.00, 165.80, 165.50, 166.20, 166.00, 166.80]
    data_values[:, price_metrics.index('Volume') * col_offset + ticker_idx_eurjpy] = [80000, 85000, 75000, 82000, 90000, 88000, 95000]

    ticker_idx_gbpjpy = tickers.index('GBPJPY=X')
    data_values[:, price_metrics.index('Close') * col_offset + ticker_idx_gbpjpy] = [190.00, 189.00, 191.00, 190.50, 189.50, 192.00, 190.00]
    data_values[:, price_metrics.index('High') * col_offset + ticker_idx_gbpjpy] = [190.50, 189.50, 191.50, 191.00, 190.00, 192.50, 190.50]
    data_values[:, price_metrics.index('Low') * col_offset + ticker_idx_gbpjpy] = [189.00, 188.00, 189.50, 189.00, 188.50, 190.00, 189.00]
    data_values[:, price_metrics.index('Open') * col_offset + ticker_idx_gbpjpy] = [189.50, 188.50, 190.00, 190.00, 189.00, 191.00, 189.50]
    data_values[:, price_metrics.index('Volume') * col_offset + ticker_idx_gbpjpy] = [300000, 280000, 320000, 310000, 290000, 330000, 305000]

    if num_rows > 0:
        data_values[0, price_metrics.index('Close') * col_offset + ticker_idx_eurjpy] = np.nan
        data_values[0, price_metrics.index('Volume') * col_offset + ticker_idx_eurjpy] = np.nan

    df = pd.DataFrame(data_values, index=index, columns=columns)
    
    for ticker in tickers:
        df[('Volume', ticker)] = df[('Volume', ticker)].astype('Int64')

    return df


class TestYFinanceForexProvider:

    @pytest.fixture()
    def provider(self):
        """
        Fixture to create an instance of YFinanceForexProvider.
        """
        return YFinanceForexProvider()

    def test_convert_to_schema(self, provider, sample_yfinance_forex_data_df1):
        """
        Test the _convert_to_schema function with a sample DataFrame.
        """
        converted_df = provider._convert_to_schema(sample_yfinance_forex_data_df1)
        ForexDataSchema.validate(converted_df)
        # Check if NaNs were dropped
        assert not converted_df.isnull().any().any()
        # Check if datetime is timezone-naive
        assert converted_df['datetime'].dt.tz is None

    def test_gen_batched_tickers(self, provider, sample_tickers1, sample_tickers2):
        """
        Test the _gen_batched_tickers function with different batch sizes.
        """
        batches = 2
        batched_tickers1 = list(provider._gen_batched_tickers(sample_tickers1, batches))
        batched_tickers2 = list(provider._gen_batched_tickers(sample_tickers2, batches))
        
        # sample_tickers1 has 2 tickers, batches=2 -> 1 batch
        assert len(batched_tickers1) == 1
        assert batched_tickers1[0] == sample_tickers1

        # sample_tickers2 has 7 tickers, batches=2 -> 4 batches (2, 2, 2, 1)
        assert len(batched_tickers2) == 4
        assert batched_tickers2[0] == ['JPY=X', 'EURUSD=X']
        assert batched_tickers2[1] == ['GBPUSD=X', 'AUDUSD=X']
        assert batched_tickers2[2] == ['NZDUSD=X', 'EURJPY=X']
        assert batched_tickers2[3] == ['GBPJPY=X']


    def test_get_forex_data(
        self,
        mocker,
        provider,
        sample_tickers1,
        sample_yfinance_forex_data_df1,
        sample_yfinance_forex_data_df2,
    ):
        """
        Test the _get_forex_data function with a sample DataFrame.
        """
        # Mock yfinance.download to return the sample dataframes in sequence
        mock_response = [
            sample_yfinance_forex_data_df1,
            sample_yfinance_forex_data_df2
        ]
        mock_download = mocker.patch("yfinance.download", side_effect=mock_response)
        
        # Call the method under test
        result = provider._get_forex_data(
            tickers=sample_tickers1 + ['GBPUSD=X', 'AUDUSD=X'], # Combine tickers to simulate multiple batches
            start_date="2025-04-07",
            end_date="2025-04-08",
            interval="5m",
            batches=2, # Set batches to 2 to trigger multiple calls to yf.download
            threads=1,
            delay_sec=0 # No delay for tests
        )
        
        # Assertions
        # yf.download should be called twice (for ['JPY=X', 'EURUSD=X'] and ['GBPUSD=X', 'AUDUSD=X'])
        assert mock_download.call_count == 2
        
        # Check if the result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        
        # Validate the schema of the combined result
        ForexDataSchema.validate(result)
        
        # Check if all expected symbols are present in the result
        expected_symbols = sorted(sample_tickers1 + ['GBPUSD=X', 'AUDUSD=X'])
        actual_symbols = sorted(result['symbol'].unique().tolist())
        assert actual_symbols == expected_symbols
        
        # Check that NaNs introduced in fixtures are handled (dropped)
        assert not result.isnull().any().any()
        
        # Check the total number of rows (after dropping NaNs)
        # df1 has 10 rows, 1st row of EURUSD=X is NaN -> 9 rows for EURUSD=X, 10 for JPY=X
        # df2 has 5 rows, 1st row of AUDUSD=X is NaN -> 4 rows for AUDUSD=X, 5 for GBPUSD=X
        # Total expected rows: (10 + 9) + (5 + 4) = 19 + 9 = 28
        # However, _convert_to_schema drops rows where *any* column is NaN for a given ticker/datetime.
        # So, for sample_yfinance_forex_data_df1, the first row for EURUSD=X is dropped.
        # For sample_yfinance_forex_data_df2, the first row for AUDUSD=X is dropped.
        # JPY=X: 10 rows
        # EURUSD=X: 9 rows (1 dropped)
        # GBPUSD=X: 5 rows
        # AUDUSD=X: 4 rows (1 dropped)
        # Total: 10 + 9 + 5 + 4 = 28 rows
        assert len(result) == 28

