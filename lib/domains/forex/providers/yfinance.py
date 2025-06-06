import logging
import itertools
import datetime
from time import sleep
import yfinance as yf
import pandas as pd
from typing import Generator, List

from lib.domains.forex.providers import IForexProvider
from lib.domains.forex.models import ForexDataSchema

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class YFinanceForexProvider(IForexProvider):
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

    def _convert_tickers(self, tickers: List[str]) -> List[str]:
        """
        Convert ticker symbols to Yahoo Finance format.

        Args:
            tickers (List[str]): List of forex ticker symbols.

        Returns:
            List[str]: Converted list of ticker symbols.
        """
        return [f"{ticker}=X" for ticker in tickers]

    def _convert_to_schema(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Convert the DataFrame to ForexDataSchema.
        
        Args:
            data (pd.DataFrame): The forex data DataFrame.
        
        Returns:
            ForexDataSchema: The validated forex data schema.
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
        data_converted["symbol"] = data_converted["symbol"].str[:-2]  # Remove '=X'
        ForexDataSchema.validate(data_converted)
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

    def _get_forex_data(
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
        Fetch forex data from Yahoo Finance.

        This method retrieves forex data for the specified tickers and date range in parallel.

        Args:
            tickers (List[str]): List of forex ticker symbols.
            start_date (datetime.date): Start date for the data.
            end_date (datetime.date): End date for the data.
            interval (str): Data interval (e.g., '1d', '1h', '1m').
        
        Returns:
            pd.DataFrame: Forex data DataFrame.
        """
        if batches is None:
            batches = self.fetch_batches
        if threads is None:
            threads = self.fetch_threads
        if delay_sec is None:
            delay_sec = self.fetch_delay_sec

        tickers = self._convert_tickers(tickers)

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
                logger.error(f"Failed to fetch forex data: {e}")

        combined_data = pd.concat(batch_dfs, axis=0)
        combined_data = combined_data.reindex(columns=ForexDataSchema.to_schema().columns.keys())
        ForexDataSchema.validate(combined_data)
        return combined_data

    def get_forex_data(
        self,
        tickers: List[str],
        start_date: datetime.date,
        end_date: datetime.date,
        interval: str,
    ) -> pd.DataFrame:
        return self._get_forex_data(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            batches=self.fetch_batches,
            threads=self.fetch_threads,
        )
