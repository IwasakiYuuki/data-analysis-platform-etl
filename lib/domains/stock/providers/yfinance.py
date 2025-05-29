import logging
import itertools
import datetime
import yfinance as yf
import pandas as pd
from typing import Generator, List

from lib.domains.stock.providers import IStockProvider
from lib.domains.stock.models import StockDataSchema

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class YFinanceProvider(IStockProvider):
    NUM_FETCH_BATCHES = 4
    NUM_FETCH_THREADS = 4

    def __init__(
        self,
        fetch_batches: int | None = None,
        fetch_threads: int | None = None,
    ):
        """
        Initialize the YFinanceProvider with optional batch and thread settings.
        
        Args:
            num_fetch_batches (int|None): Number of batches for fetching data.
            num_fetch_threads (int|None): Number of threads for fetching data.
        """
        self.fetch_batches = fetch_batches if fetch_batches is not None else self.NUM_FETCH_BATCHES
        self.fetch_threads = fetch_threads if fetch_threads is not None else self.NUM_FETCH_THREADS


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

        batch_dfs = []
        try:
            for batch in self._gen_batched_tickers(tickers, batches):
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
        except Exception as e:
            logger.error(f"Failed to fetch stock data: {e}")
        finally:
            combined_data = pd.concat(batch_dfs, axis=0)
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
        raise NotImplementedError("This method is not implemented in YFinanceProvider.")

    def get_stock_data_by_market(
        self,
        exchange: str,
        market: str,
        start_date: datetime.date,
        end_date: datetime.date,
        interval: str,
    ) -> pd.DataFrame:
        raise NotImplementedError("This method is not implemented in YFinanceProvider.")
