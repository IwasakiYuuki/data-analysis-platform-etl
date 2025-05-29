import logging
import datetime
import pandas as pd
from typing import List
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class IStockProvider(metaclass=ABCMeta):
    
    @abstractmethod
    def get_stock_data(
        self,
        tickers: List[str],
        start_date: datetime.date,
        end_date: datetime.date,
        interval: str,
    ) -> pd.DataFrame:
        """
        指定されたティッカーシンボルの株価データを取得します。

        Args:
            tickers (List[str]): 株価ティッカーシンボルのリスト。
            start_date (datetime.date): データ取得開始日。
            end_date (datetime.date): データ取得終了日。
            interval (str): データの間隔 (例: '1d', '1h', '1m')。

        Returns:
            pd.DataFrame: 指定されたティッカーシンボルの株価データ。
        """
        pass

    @abstractmethod
    def get_stock_data_by_exchange(
        self,
        exchange: str,
        start_date: datetime.date,
        end_date: datetime.date,
        interval: str,
    ) -> pd.DataFrame:
        """
        指定された取引所の株価データを取得します。

        Args:
            exchange (str): 証券取引所名 (例: 'JPX')。
            start_date (datetime.date): データ取得開始日。
            end_date (datetime.date): データ取得終了日。
            interval (str): データの間隔 (例: '1d', '1h', '1m')。
        Returns:
            pd.DataFrame: 指定された取引所の株価データ。
        """
        pass

    @abstractmethod
    def get_stock_data_by_market(
        self,
        exchange:str,
        market: str,
        start_date: datetime.date,
        end_date: datetime.date,
        interval: str,
    ) -> pd.DataFrame:
        """
        指定された市場の株価データを取得します。

        Args:
            exchange (str): 証券取引所名 (例: 'JPX')。
            market (str): 市場名 (例: 'prime', 'standard')。
            start_date (datetime.date): データ取得開始日。
            end_date (datetime.date): データ取得終了日。
            interval (str): データの間隔 (例: '1d', '1h', '1m')。
        Returns:
            pd.DataFrame: 指定された市場の株価データ。
        """
        pass

