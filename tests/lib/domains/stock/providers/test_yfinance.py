import pytest
import numpy as np
import pandas as pd

from lib.domains.stock.models import StockDataSchema
from lib.domains.stock.providers.yfinance import YFinanceStockProvider


@pytest.fixture
def sample_tickers1() -> list[str]:
    """
    Fixture to create a sample list of stock tickers.
    """
    return ['7203.T', '7205.T']

@pytest.fixture
def sample_tickers2() -> list[str]:
    """
    Fixture to create another sample list of stock tickers.
    """
    return ['7203.T', '7205.T', 'AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA']

@pytest.fixture
def sample_yfinance_stock_data_df1() -> pd.DataFrame:
    """
    Fixture to create a sample DataFrame for Yfinance stock data.

    Below is an example of the DataFrame structure:
    Price                            Close                     High                    Low               Open             Volume
    Ticker                          7203.T      7205.T       7203.T      7205.T     7203.T      7205.T 7203.T      7205.T 7203.T    7205.T
    Datetime
    2025-04-07 00:05:00+00:00  2432.741575         NaN  2331.287784         NaN  2723965.0         NaN    0.0         NaN    0.0       NaN
    2025-04-07 00:10:00+00:00  2294.764805  370.308026  2337.868966  359.082142  2572358.0  383.390617    0.0  375.448679    0.0  367985.0
    2025-04-07 00:15:00+00:00  2225.707060  342.218765  2191.500711  390.527587  2700707.0  408.076634    0.0  355.100487    0.0  248036.0
    2025-04-07 00:20:00+00:00  2419.760427  385.457861  2273.334572  396.078692   148169.0  407.407540    0.0  340.856281    0.0  319082.0
    2025-04-07 00:25:00+00:00  2487.374358  385.084353  2441.070336  349.085567  2570378.0  414.254395    0.0  354.440064    0.0   60330.0
    2025-04-07 00:30:00+00:00  2216.883962  346.099965  2379.786488  411.902255   101262.0  413.251455    0.0  393.888631    0.0  178618.0
    2025-04-07 00:35:00+00:00  2245.466191  363.017425  2437.889858  389.421264  1870788.0  409.273138    0.0  414.381827    0.0  290734.0
    2025-04-07 00:40:00+00:00  2494.787228  344.681226  2200.150607  396.556810  2405864.0  409.210597    0.0  376.723229    0.0   26846.0
    2025-04-07 00:45:00+00:00  2282.725415  367.591492  2339.581925  370.835351  2563453.0  405.474858    0.0  348.158964    0.0  263237.0
    2025-04-07 00:50:00+00:00  2459.217545  416.562925  2434.363504  410.104839  1079049.0  343.578525    0.0  400.214746    0.0  258315.0
    """
    tickers = ['7203.T', '7205.T']
    price_metrics = ['Close', 'High', 'Low', 'Open', 'Volume']

    columns = pd.MultiIndex.from_product(
        [price_metrics, tickers],
        names=['Price', 'Ticker']
    )

    index = pd.to_datetime(pd.date_range('2025-04-07 00:05:00+00:00', periods=10, freq='5min'))
    data_values = np.zeros((len(index), len(price_metrics) * len(tickers)))
    
    data_values[:, 0] = np.random.uniform(2200, 2500, size=len(index)) # Close
    data_values[:, 1] = np.random.uniform(2250, 2550, size=len(index)) # High
    data_values[:, 2] = np.random.uniform(2150, 2450, size=len(index)) # Low
    data_values[:, 3] = np.random.uniform(2200, 2500, size=len(index)) # Open
    data_values[:, 4] = np.random.randint(0, 3000000, size=len(index)) # Volume (int)

    ticker_idx_7205 = tickers.index('7205.T')
    col_offset = len(tickers) 

    data_values[:, price_metrics.index('Close') * col_offset + ticker_idx_7205] = np.random.uniform(340, 420, size=len(index))
    data_values[:, price_metrics.index('High') * col_offset + ticker_idx_7205] = np.random.uniform(345, 425, size=len(index))
    data_values[:, price_metrics.index('Low') * col_offset + ticker_idx_7205] = np.random.uniform(335, 415, size=len(index))
    data_values[:, price_metrics.index('Open') * col_offset + ticker_idx_7205] = np.random.uniform(340, 420, size=len(index))
    data_values[:, price_metrics.index('Volume') * col_offset + ticker_idx_7205] = np.random.randint(0, 500000, size=len(index))

    # 複数の銘柄を含む場合にNaNが含まれる可能性がある
    if len(index) > 0:
        data_values[0, price_metrics.index('Close') * col_offset + ticker_idx_7205] = np.nan
        data_values[0, price_metrics.index('High') * col_offset + ticker_idx_7205] = np.nan
        data_values[0, price_metrics.index('Low') * col_offset + ticker_idx_7205] = np.nan
        data_values[0, price_metrics.index('Open') * col_offset + ticker_idx_7205] = np.nan
        data_values[0, price_metrics.index('Volume') * col_offset + ticker_idx_7205] = np.nan


    df = pd.DataFrame(data_values, index=index, columns=columns)
    df.index.name = 'Datetime'
    return df

@pytest.fixture
def sample_yfinance_stock_data_df2() -> pd.DataFrame:
    """
    Fixture to create a sample DataFrame for Yfinance stock data with 2 DIFFERENT tickers.
    Tickers: ['AAPL', 'MSFT']
    """
    tickers = ['AAPL', 'MSFT']
    price_metrics = ['Close', 'High', 'Low', 'Open', 'Volume']
    num_rows = 5

    columns = pd.MultiIndex.from_product(
        [price_metrics, tickers],
        names=['Price', 'Ticker']
    )

    index = pd.to_datetime(pd.date_range('2025-05-01 09:00:00+00:00', periods=num_rows, freq='h'))
    index.name = 'Datetime'

    data_values = np.zeros((len(index), len(price_metrics) * len(tickers)))

    ticker_idx_aapl = tickers.index('AAPL')
    col_offset = len(tickers)

    data_values[:, price_metrics.index('Close') * col_offset + ticker_idx_aapl] = [170.0, 171.5, 172.0, 171.0, 173.0]
    data_values[:, price_metrics.index('High') * col_offset + ticker_idx_aapl] = [170.5, 172.0, 172.5, 171.5, 173.5]
    data_values[:, price_metrics.index('Low') * col_offset + ticker_idx_aapl] = [169.5, 170.0, 171.0, 170.5, 172.0]
    data_values[:, price_metrics.index('Open') * col_offset + ticker_idx_aapl] = [169.8, 170.2, 171.8, 171.2, 172.5]
    data_values[:, price_metrics.index('Volume') * col_offset + ticker_idx_aapl] = [100000, 120000, 90000, 110000, 130000]

    ticker_idx_msft = tickers.index('MSFT')
    data_values[:, price_metrics.index('Close') * col_offset + ticker_idx_msft] = [400.0, 401.0, 402.5, 401.5, 403.0]
    data_values[:, price_metrics.index('High') * col_offset + ticker_idx_msft] = [400.5, 401.8, 403.0, 402.0, 403.5]
    data_values[:, price_metrics.index('Low') * col_offset + ticker_idx_msft] = [399.0, 399.5, 401.0, 400.5, 401.5]
    data_values[:, price_metrics.index('Open') * col_offset + ticker_idx_msft] = [399.8, 400.2, 401.8, 401.0, 402.5]
    data_values[:, price_metrics.index('Volume') * col_offset + ticker_idx_msft] = [50000, 60000, 45000, 55000, 65000]

    if num_rows > 0:
        data_values[0, price_metrics.index('Close') * col_offset + ticker_idx_msft] = np.nan
        data_values[0, price_metrics.index('Volume') * col_offset + ticker_idx_msft] = np.nan

    df = pd.DataFrame(data_values, index=index, columns=columns)
    
    for ticker in tickers:
        df[('Volume', ticker)] = df[('Volume', ticker)].astype('Int64')

    return df


@pytest.fixture
def sample_yfinance_stock_data_df3() -> pd.DataFrame:
    """
    Fixture to create a sample DataFrame for Yfinance stock data with 3 DIFFERENT tickers.
    Tickers: ['GOOG', 'AMZN', 'TSLA']
    """
    tickers = ['GOOG', 'AMZN', 'TSLA']
    price_metrics = ['Close', 'High', 'Low', 'Open', 'Volume']
    num_rows = 7 # 行数を設定

    columns = pd.MultiIndex.from_product(
        [price_metrics, tickers],
        names=['Price', 'Ticker']
    )

    index = pd.to_datetime(pd.date_range('2025-05-02 10:00:00+00:00', periods=num_rows, freq='30min'))
    index.name = 'Datetime'

    data_values = np.zeros((len(index), len(price_metrics) * len(tickers)))

    col_offset = len(tickers)

    ticker_idx_goog = tickers.index('GOOG')
    data_values[:, price_metrics.index('Close') * col_offset + ticker_idx_goog] = [180.0, 181.0, 182.0, 181.5, 183.0, 182.5, 184.0]
    data_values[:, price_metrics.index('High') * col_offset + ticker_idx_goog] = [180.5, 181.5, 182.5, 182.0, 183.5, 183.0, 184.5]
    data_values[:, price_metrics.index('Low') * col_offset + ticker_idx_goog] = [179.5, 180.0, 181.0, 180.5, 181.5, 181.0, 182.5]
    data_values[:, price_metrics.index('Open') * col_offset + ticker_idx_goog] = [179.8, 180.2, 181.8, 181.2, 182.5, 182.0, 183.5]
    data_values[:, price_metrics.index('Volume') * col_offset + ticker_idx_goog] = [200000, 210000, 190000, 205000, 220000, 215000, 230000]

    ticker_idx_amzn = tickers.index('AMZN')
    data_values[:, price_metrics.index('Close') * col_offset + ticker_idx_amzn] = [150.0, 150.5, 151.0, 150.8, 151.5, 151.2, 152.0]
    data_values[:, price_metrics.index('High') * col_offset + ticker_idx_amzn] = [150.3, 150.8, 151.3, 151.0, 151.8, 151.5, 152.3]
    data_values[:, price_metrics.index('Low') * col_offset + ticker_idx_amzn] = [149.5, 149.8, 150.2, 150.0, 150.5, 150.3, 151.0]
    data_values[:, price_metrics.index('Open') * col_offset + ticker_idx_amzn] = [149.8, 150.0, 150.8, 150.5, 151.2, 151.0, 151.8]
    data_values[:, price_metrics.index('Volume') * col_offset + ticker_idx_amzn] = [80000, 85000, 75000, 82000, 90000, 88000, 95000]

    ticker_idx_tsla = tickers.index('TSLA')
    data_values[:, price_metrics.index('Close') * col_offset + ticker_idx_tsla] = [250.0, 248.0, 252.0, 251.0, 249.0, 253.0, 250.0]
    data_values[:, price_metrics.index('High') * col_offset + ticker_idx_tsla] = [251.0, 249.0, 253.0, 252.0, 250.0, 254.0, 251.0]
    data_values[:, price_metrics.index('Low') * col_offset + ticker_idx_tsla] = [249.0, 247.0, 250.0, 249.5, 248.0, 251.0, 248.5]
    data_values[:, price_metrics.index('Open') * col_offset + ticker_idx_tsla] = [249.5, 248.5, 251.0, 250.5, 248.5, 252.0, 249.0]
    data_values[:, price_metrics.index('Volume') * col_offset + ticker_idx_tsla] = [300000, 280000, 320000, 310000, 290000, 330000, 305000]

    if num_rows > 0:
        data_values[0, price_metrics.index('Close') * col_offset + ticker_idx_amzn] = np.nan
        data_values[0, price_metrics.index('Volume') * col_offset + ticker_idx_amzn] = np.nan

    df = pd.DataFrame(data_values, index=index, columns=columns)
    
    for ticker in tickers:
        df[('Volume', ticker)] = df[('Volume', ticker)].astype('Int64')

    return df


class TestYFinanceStockProvider:

    @pytest.fixture()
    def provider(self):
        """
        Fixture to create an instance of YFinanceProvider.
        """
        return YFinanceStockProvider()

    def test_convert_to_schema(self, provider, sample_yfinance_stock_data_df1):
        """
        Test the _convert_to_schema function with a sample DataFrame.
        """
        provider._convert_to_schema(sample_yfinance_stock_data_df1)

    def test_gen_batched_tickers(self, provider, sample_tickers1, sample_tickers2):
        """
        Test the _gen_batched_tickers function with different batch sizes.
        """
        batches = 2
        batched_tickers1 = list(provider._gen_batched_tickers(sample_tickers1, batches))
        batched_tickers2 = list(provider._gen_batched_tickers(sample_tickers2, batches))
        assert len(batched_tickers1) == 1
        assert len(batched_tickers2) == 4

    def test_get_stock_data(
        self,
        mocker,
        provider,
        sample_tickers1,
        sample_yfinance_stock_data_df1,
        sample_yfinance_stock_data_df2,
    ):
        """
        Test the _get_stock_data function with a sample DataFrame.
        """
        mock_response = [
            sample_yfinance_stock_data_df1,
            sample_yfinance_stock_data_df2
        ]
        mock = mocker.patch("yfinance.download", side_effect=mock_response)
        result = provider._get_stock_data(
            sample_tickers1,
            "2025-04-07",
            "2025-04-08",
            "5m",
            batches=1,
            threads=1
        )
        assert mock.call_count == 2
        assert isinstance(result, pd.DataFrame)
        StockDataSchema.validate(result)
