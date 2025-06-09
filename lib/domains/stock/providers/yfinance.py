import logging
import itertools
import datetime
from time import sleep
import yfinance as yf
import pandas as pd
from typing import Generator, List

from lib.domains.stock.providers import IStockProvider
from lib.domains.stock.models import StockDataSchema

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class YFinanceStockProvider(IStockProvider):
    FETCH_BATCHES = 4
    FETCH_THREADS = 4
    FETCH_DELAY_SEC = 1

    def __init__(
        self,
        fetch_batches: int | None = None,
        fetch_threads: int | None = None,
        fetch_delay_sec: int | None = None,
    ):
        """
        Initialize the YFinanceProvider with optional batch and thread settings.
        
        Args:
            num_fetch_batches (int|None): Number of batches for fetching data.
            num_fetch_threads (int|None): Number of threads for fetching data.
        """
        self.fetch_batches = fetch_batches if fetch_batches is not None else self.FETCH_BATCHES
        self.fetch_threads = fetch_threads if fetch_threads is not None else self.FETCH_THREADS
        self.fetch_delay_sec = fetch_delay_sec if fetch_delay_sec is not None else self.FETCH_DELAY_SEC

    def _get_tickers(
        self,
        exchange: str = "JPX",
        market: str = "prime",
    ) -> List[str]:
        """
        Get the list of stock tickers from the provider.
        Currently, this method supported JPX (Japan Exchange Group).

        Args:
            exchange (str): The stock exchange to fetch tickers from (default is "JPX").
            market (str): The market segment to fetch tickers from (default is "prime").
        
        Returns:
            List[str]: List of stock ticker symbols.
        """
        # For now, we only support JPX (Japan Exchange Group).
        if exchange != "JPX":
            raise NotImplementedError(f"Exchange {exchange} is not supported by YFinanceProvider.")
        if market not in ["prime", "standard", "growth", "eft"]:
            raise ValueError(f"Market {market} is not supported by YFinanceProvider.")

        JPX_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
        MARKET_COLUMN_NAMES = {
            "prime": "プライム（内国株式）",
            "standard": "スタンダード（内国株式）",
            "growth": "グロース（内国株式）",
            "eft": "ETF・ETN",
        }

        df_jpx = pd.read_excel(JPX_URL)
        stock_series = df_jpx["コード"][df_jpx["市場・商品区分"] == MARKET_COLUMN_NAMES[market]]
        stock_list = list(stock_series.astype(str) + ".T")
        return stock_list

    def _convert_to_schema(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Convert the DataFrame to StockDataSchema.
        
        Args:
            data (pd.DataFrame): The stock data DataFrame.
        
        Returns:
            StockDataSchema: The validated stock data schema.
        """
        data_swapped = data.swaplevel(0, 1, axis=1)
        data_stacked = data_swapped.stack(level="Ticker", future_stack=True)
        data_dropped = data_stacked.dropna(how="any")
        data_reordered = data_dropped.reorder_levels(["Ticker", "Datetime"])
        data_reindexed = data_reordered.reset_index()
        data_converted = data_reindexed.rename({
            "Datetime": "datetime",
            "Ticker": "symbol",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }, axis=1)
        data_converted["datetime"] = data_converted["datetime"].dt.tz_localize(None)
        data_converted["volume"] = data_converted["volume"].astype(int)
        StockDataSchema.validate(data_converted)
        return data_converted

    def _gen_batched_tickers(
        self,
        tickers: List[str],
        batches: int,
    ) -> Generator[List[str], None, None]:
        it = iter(tickers)
        while True:
            batch = list(itertools.islice(it, batches))
            if not batch:
                break
            yield batch

    def _get_stock_data(
        self,
        tickers: List[str],
        start_date: datetime.date,
        end_date: datetime.date,
        interval: str,
        batches: int | None = None,
        threads: int | None = None,
        delay_sec: int | None = None,
    ) -> pd.DataFrame:
        """
        Fetch stock data from Yahoo Finance.

        This method retrieves stock data for the specified tickers and date range in parallel.

        Args:
            tickers (List[str]): List of stock ticker symbols.
            start_date (datetime.date): Start date for the data.
            end_date (datetime.date): End date for the data.
            interval (str): Data interval (e.g., '1d', '1h', '1m').
        
        Returns:
            pd.DataFrame: Stock data DataFrame.
        """
        if batches is None:
            batches = self.fetch_batches
        if threads is None:
            threads = self.fetch_threads
        if delay_sec is None:
            delay_sec = self.fetch_delay_sec

        batch_dfs = []
        for batch in self._gen_batched_tickers(tickers, batches):
            try:
                data = yf.download(
                    tickers=batch,
                    start=start_date,
                    end=end_date,
                    interval=interval,
                    group_by="Ticker",
                    threads=threads,  # type: ignore
                )
                if not isinstance(data, pd.DataFrame) or data.empty:
                    raise ValueError("No data returned from Yahoo Finance.")
                data_converted = self._convert_to_schema(data)
                batch_dfs.append(data_converted)
                sleep(delay_sec)
            except Exception as e:
                logger.error(f"Failed to fetch stock data: {e}")

        combined_data = pd.concat(batch_dfs, axis=0)
        combined_data = combined_data.reindex(columns=StockDataSchema.to_schema().columns.keys())
        StockDataSchema.validate(combined_data)
        return combined_data

    def get_stock_data(
        self,
        tickers: List[str],
        start_date: datetime.date,
        end_date: datetime.date,
        interval: str,
    ) -> pd.DataFrame:
        return self._get_stock_data(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            batches=self.fetch_batches,
            threads=self.fetch_threads,
        )

    def get_stock_data_by_exchange(
        self,
        exchange: str,
        start_date: datetime.date,
        end_date: datetime.date,
        interval: str,
    ) -> pd.DataFrame:
        tickers = self._get_tickers(exchange=exchange)
        return self.get_stock_data(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
        )

    def get_stock_data_by_market(
        self,
        exchange: str,
        market: str,
        start_date: datetime.date,
        end_date: datetime.date,
        interval: str,
    ) -> pd.DataFrame:
        tickers = self._get_tickers(
            exchange=exchange,
            market=market
        )
        return self.get_stock_data(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
        )
