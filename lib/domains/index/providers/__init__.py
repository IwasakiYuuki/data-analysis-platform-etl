import logging
import datetime
import pandas as pd
from typing import List
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class IIndexProvider(metaclass=ABCMeta):
    
    @abstractmethod
    def get_index_data(
        self,
        tickers: List[str],
        start_date: datetime.date,
        end_date: datetime.date,
        interval: str,
    ) -> pd.DataFrame:
        """
        Fetch index data for given symbols and date range.

        Args:
            tickers (List[str]): List of index symbols (e.g., ['^GSPC', '^DJI']).
            start_date (datetime.date): Start date for the data.
            end_date (datetime.date): End date for the data.
            interval (str): Data interval (e.g., '1d', '1h').

        Returns:
            pd.DataFrame: DataFrame containing index data with columns 
        """
        pass
