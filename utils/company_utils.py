import pandas as pd
import yfinance as yf
import datetime
import time
import tempfile
import os
import logging
from airflow.providers.apache.hdfs.hooks.webhdfs import WebHDFSHook

from utils.config import HDFS_PATHS, DEFAULT_REQUEST_DELAY
from utils.stock_utils import get_stock_list
from utils.data_utils import write_to_hdfs

def get_company_info_from_yfinance(ticker: str):
    """
    yfinanceから企業情報を取得する。
    """
    try:
        tk = yf.Ticker(ticker)
        time.sleep(DEFAULT_REQUEST_DELAY) # API呼び出し前に遅延を挿入
        info = tk.info
        if info:
            # 必要な情報のみを抽出
            selected_info = {
                'symbol': ticker,
                'shortName': info.get('shortName'),
                'longBusinessSummary': info.get('longBusinessSummary'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'fullTimeEmployees': info.get('fullTimeEmployees'),
                'country': info.get('country'),
                'website': info.get('website'),
                'marketCap': info.get('marketCap'),
                'currency': info.get('currency'),
                'exchange': info.get('exchange'),
                'quoteType': info.get('quoteType'),
                'market': info.get('market'),
                'address1': info.get('address1'),
                'city': info.get('city'),
                'state': info.get('state'),
                'zip': info.get('zip'),
                'phone': info.get('phone'),
            }
            return pd.DataFrame([selected_info])
        return None
    except Exception as e:
        print(f"Error fetching company info for {ticker}: {e}")
        return None

def get_financial_statements_from_yfinance(ticker: str, statement_type: str, period: str = 'annual'):
    """
    yfinanceから財務諸表データを取得する。
    statement_type: 'financials' (損益計算書), 'balance_sheet' (貸借対照表), 'cashflow' (キャッシュフロー計算書)
    period: 'annual' or 'quarterly'
    """
    # 入力値の検証をtryブロックの外に移動
    if statement_type not in ['financials', 'balance_sheet', 'cashflow']:
        raise ValueError("Invalid statement_type. Must be 'financials', 'balance_sheet', or 'cashflow'.")

    try:
        tk = yf.Ticker(ticker)
        time.sleep(DEFAULT_REQUEST_DELAY) # API呼び出し前に遅延を挿入

        if statement_type == 'financials':
            data = tk.financials if period == 'annual' else tk.quarterly_financials
        elif statement_type == 'balance_sheet':
            data = tk.balance_sheet if period == 'annual' else tk.quarterly_balance_sheet
        elif statement_type == 'cashflow':
            data = tk.cashflow if period == 'annual' else tk.quarterly_cashflow
        
        if data is not None and not data.empty:
            # yfinanceの財務データは通常、指標がインデックス、日付がカラムの形式
            # 転置して日付をインデックス、指標をカラムにする
            df = data.T
            df.index.name = 'report_date' # インデックスに名前を付ける
            df = df.reset_index() # インデックス（日付）をカラムに変換

            df['symbol'] = ticker # ティッカーシンボル情報を追加
            
            # カラム名をクリーンアップ (特殊文字やスペースをアンダースコアに変換)
            df.columns = [col.replace(' ', '_').replace('.', '').replace('/', '_').replace('-', '_').lower() for col in df.columns]
            
            # report_dateがdatetime.dateオブジェクトであることを保証
            df['report_date'] = pd.to_datetime(df['report_date']).dt.date
            
            # 日付関連のカラムを追加
            df['year'] = pd.to_datetime(df['report_date']).dt.year
            df['month'] = pd.to_datetime(df['report_date']).dt.month
            df['day'] = pd.to_datetime(df['report_date']).dt.day
            df['statement_type'] = statement_type
            df['period_type'] = period

            return df
        return None
    except Exception as e:
        print(f"Error fetching {period} {statement_type} for {ticker}: {e}")
        return None

def process_company_info_data(hdfs_conn_id: str, market: str = "prime"):
    """
    企業情報を取得し、HDFSに出力する。
    """
    tickers = get_stock_list(market)
    hdfs_hook = WebHDFSHook(webhdfs_conn_id=hdfs_conn_id)
    
    all_company_info = pd.DataFrame()
    
    for ticker in tickers:
        info_data = get_company_info_from_yfinance(ticker)
        if info_data is not None and not info_data.empty:
            all_company_info = pd.concat([all_company_info, info_data], ignore_index=True)
    
    if not all_company_info.empty:
        # HDFSパスの設定
        hdfs_path = HDFS_PATHS["company_info"]
        
        # 一時ファイルに書き込む
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".csv") as tmp_file:
            all_company_info.to_csv(tmp_file, index=False)
            tmp_file_path = tmp_file.name
        
        try:
            # HDFSに書き込む (上書き)
            # 企業情報は頻繁に変わらないため、固定ファイル名で上書き
            hdfs_hook.load_file(
                source=tmp_file_path,
                destination=f"{hdfs_path}/company_info.csv",
                overwrite=True
            )
            print(f"Successfully wrote company info data to HDFS path: {hdfs_path}/company_info.csv")
        except Exception as e:
            print(f"Error writing company info data to HDFS: {e}")
        finally:
            os.remove(tmp_file_path)
    else:
        print(f"No company info data to write to HDFS for market: {market}")

def process_financial_data(hdfs_conn_id: str, market: str = "prime"):
    """
    財務諸表データを取得し、HDFSに出力する。
    """
    tickers = get_stock_list(market)
    hdfs_hook = WebHDFSHook(webhdfs_conn_id=hdfs_conn_id)
    
    statement_types = ['financials', 'balance_sheet', 'cashflow']
    periods = ['annual', 'quarterly']

    for period in periods:
        for st_type in statement_types:
            combined_financial_data = pd.DataFrame()
            for ticker in tickers:
                financial_data = get_financial_statements_from_yfinance(ticker, st_type, period)
                if financial_data is not None and not financial_data.empty:
                    combined_financial_data = pd.concat([combined_financial_data, financial_data], ignore_index=True)
            
            if not combined_financial_data.empty:
                # HDFSパスの設定
                # Hiveのパーティション形式に合わせたパスを構築
                hdfs_base_path_for_write = f"{HDFS_PATHS['financials']}/period_type={period}/statement_type={st_type}"
                
                # write_to_hdfsは'Date'カラムを期待するので、'report_date'をリネーム
                # そして、indexを日付にする
                combined_financial_data_for_write = combined_financial_data.rename(columns={'report_date': 'Date'})
                combined_financial_data_for_write = combined_financial_data_for_write.set_index('Date')

                try:
                    # write_to_hdfs を呼び出す
                    write_to_hdfs(combined_financial_data_for_write, hdfs_hook, hdfs_base_path_for_write)
                    print(f"Successfully wrote {period} {st_type} data to HDFS path: {hdfs_base_path_for_write}")
                except Exception as e:
                    # Log the error but allow the process to continue for other data types
                    logging.error(f"Error writing {period} {st_type} data to HDFS path {hdfs_base_path_for_write}: {e}")
            else:
                print(f"No {period} {st_type} data to write to HDFS for market: {market}")

