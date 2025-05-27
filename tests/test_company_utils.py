import unittest
from unittest import mock
import pandas as pd
import datetime
import os
import tempfile
import logging

# Suppress logging from yfinance if it's chatty during tests
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# テスト対象の関数をインポート
from utils.company_utils import (
    get_company_info_from_yfinance,
    get_financial_statements_from_yfinance,
    process_company_info_data,
    process_financial_data
)
# 設定値をインポート (アサーションで使用)
from utils.config import HDFS_PATHS, DEFAULT_REQUEST_DELAY

# yfinance.Ticker クラスのモック
class MockTicker:
    def __init__(self, ticker_symbol, info_data=None, financials_data=None,
                 quarterly_financials_data=None, balance_sheet_data=None,
                 quarterly_balance_sheet_data=None, cashflow_data=None,
                 quarterly_cashflow_data=None, raise_exception=False):
        self.ticker_symbol = ticker_symbol
        self._info = info_data if info_data is not None else {}
        self._financials = financials_data if financials_data is not None else pd.DataFrame()
        self._quarterly_financials = quarterly_financials_data if quarterly_financials_data is not None else pd.DataFrame()
        self._balance_sheet = balance_sheet_data if balance_sheet_data is not None else pd.DataFrame()
        self._quarterly_balance_sheet = quarterly_balance_sheet_data if quarterly_balance_sheet_data is not None else pd.DataFrame()
        self._cashflow = cashflow_data if cashflow_data is not None else pd.DataFrame()
        self._quarterly_cashflow = quarterly_cashflow_data if quarterly_cashflow_data is not None else pd.DataFrame()
        self._raise_exception = raise_exception

    @property
    def info(self):
        if self._raise_exception:
            raise Exception("Mock Ticker Info Error")
        return self._info

    @property
    def financials(self):
        if self._raise_exception:
            raise Exception("Mock Ticker Financials Error")
        return self._financials

    @property
    def quarterly_financials(self):
        if self._raise_exception:
            raise Exception("Mock Ticker Quarterly Financials Error")
        return self._quarterly_financials

    @property
    def balance_sheet(self):
        if self._raise_exception:
            raise Exception("Mock Ticker Balance Sheet Error")
        return self._balance_sheet

    @property
    def quarterly_balance_sheet(self):
        if self._raise_exception:
            raise Exception("Mock Ticker Quarterly Balance Sheet Error")
        return self._quarterly_balance_sheet

    @property
    def cashflow(self):
        if self._raise_exception:
            raise Exception("Mock Ticker Cashflow Error")
        return self._cashflow

    @property
    def quarterly_cashflow(self):
        if self._raise_exception:
            raise Exception("Mock Ticker Cashflow Error")
        return self._quarterly_cashflow

class TestCompanyUtils(unittest.TestCase):

    @staticmethod
    def _create_mock_financial_df_output(ticker, st_type, period, date_obj, value):
        """
        Helper function to create mock financial DataFrame in the expected output format
        This simulates the DataFrame returned by get_financial_statements_from_yfinance
        """
        data_dict = {
            'report_date': [date_obj], # This should be datetime.date object
            'symbol': [ticker],
            'year': [date_obj.year],
            'month': [date_obj.month],
            'day': [date_obj.day],
            'statement_type': [st_type],
            'period_type': [period],
        }
        # Add specific metrics based on statement type
        if st_type == 'financials':
            # Use the actual cleaned column names from yfinance income statement
            data_dict.update({
                'tax_effect_of_unusual_items': [value * 0.01],
                'tax_rate_for_calcs': [value * 0.001],
                'normalized_ebitda': [value * 1.1],
                'total_unusual_items': [value * 0.02],
                'total_unusual_items_excluding_goodwill': [value * 0.015],
                'net_income_from_continuing_operation_net_minority_interest': [value * 0.8],
                'reconciled_depreciation': [value * 0.05],
                'reconciled_cost_of_revenue': [value * 0.4],
                'ebitda': [value * 1.05],
                'ebit': [value * 1.0],
                'net_interest_income': [value * 0.005],
                'interest_expense': [value * 0.01],
                'interest_income': [value * 0.005],
                'normalized_income': [value * 0.9],
                'net_income_from_continuing_and_discontinued_operation': [value * 0.85],
                'total_expenses': [value * 0.6],
                'total_operating_income_as_reported': [value * 0.4],
                'diluted_average_shares': [100000000],
                'basic_average_shares': [100000000],
                'diluted_eps': [value / 100000000],
                'basic_eps': [value / 100000000],
                'diluted_ni_availto_com_stockholders': [value * 0.78],
                'average_dilution_earnings': [value * 0.0001],
                'net_income_common_stockholders': [value * 0.75],
                'otherunder_preferred_stock_dividend': [value * 0.002],
                'net_income': [value * 0.7],
                'minority_interests': [value * 0.003],
                'net_income_including_noncontrolling_interests': [value * 0.703],
                'net_income_continuous_operations': [value * 0.7],
                'tax_provision': [value * 0.1],
                'pretax_income': [value * 0.8],
                'other_income_expense': [value * 0.001],
                'other_non_operating_income_expenses': [value * 0.0005],
                'earnings_from_equity_interest': [value * 0.0002],
                'gain_on_sale_of_security': [value * 0.0001],
                'net_non_operating_interest_income_expense': [value * 0.0003],
                'total_other_finance_cost': [value * 0.0004],
                'interest_expense_non_operating': [value * 0.0002],
                'interest_income_non_operating': [value * 0.0001],
                'operating_income': [value * 0.35],
                'operating_expense': [value * 0.25],
                'selling_general_and_administration': [value * 0.15],
                'gross_profit': [value * 0.6],
                'cost_of_revenue': [value * 0.4],
                'total_revenue': [value],
                'operating_revenue': [value],
            })
        elif st_type == 'balance_sheet':
            # Use the actual cleaned column names from yfinance balance sheet
            data_dict.update({
                'treasury_shares_number': [1000000],
                'ordinary_shares_number': [200000000],
                'share_issued': [200000000],
                'net_debt': [value * 0.1],
                'total_debt': [value * 0.15],
                'tangible_book_value': [value * 0.8],
                'invested_capital': [value * 0.9],
                'working_capital': [value * 0.3],
                'net_tangible_assets': [value * 0.75],
                'capital_lease_obligations': [value * 0.01],
                'common_stock_equity': [value * 0.6],
                'total_capitalization': [value * 0.7],
                'total_equity_gross_minority_interest': [value * 0.65],
                'minority_interest': [value * 0.005],
                'stockholders_equity': [value * 0.645],
                'other_equity_interest': [value * 0.001],
                'treasury_stock': [value * 0.002],
                'retained_earnings': [value * 0.5],
                'additional_paid_in_capital': [value * 0.1],
                'capital_stock': [value * 0.05],
                'common_stock': [value * 0.05],
                'total_liabilities_net_minority_interest': [value * 0.3],
                'total_non_current_liabilities_net_minority_interest': [value * 0.2],
                'other_non_current_liabilities': [value * 0.05],
                'employee_benefits': [value * 0.02],
                'non_current_pension_and_other_postretirement_benefit_plans': [value * 0.01],
                'non_current_deferred_liabilities': [value * 0.03],
                'non_current_deferred_taxes_liabilities': [value * 0.02],
                'long_term_debt_and_capital_lease_obligation': [value * 0.1],
                'long_term_capital_lease_obligation': [value * 0.005],
                'long_term_debt': [value * 0.095],
                'current_liabilities': [value * 0.1],
                'other_current_liabilities': [value * 0.03],
                'current_debt_and_capital_lease_obligation': [value * 0.02],
                'current_capital_lease_obligation': [value * 0.001],
                'current_debt': [value * 0.019],
                'other_current_borrowings': [value * 0.005],
                'commercial_paper': [value * 0.002],
                'payables_and_accrued_expenses': [value * 0.04],
                'current_accrued_expenses': [value * 0.01],
                'payables': [value * 0.02],
                'other_payable': [value * 0.01],
                'total_tax_payable': [value * 0.005],
                'income_tax_payable': [value * 0.003],
                'accounts_payable': [value * 0.015],
                'total_assets': [value],
                'total_non_current_assets': [value * 0.7],
                'other_non_current_assets': [value * 0.05],
                'non_current_deferred_assets': [value * 0.02],
                'non_current_deferred_taxes_assets': [value * 0.01],
                'non_current_accounts_receivable': [value * 0.03],
                'investments_and_advances': [value * 0.1],
                'investmentin_financial_assets': [value * 0.05],
                'available_for_sale_securities': [value * 0.03],
                'long_term_equity_investment': [value * 0.02],
                'investmentsin_joint_venturesat_cost': [value * 0.01],
                'investmentsin_associatesat_cost': [value * 0.005],
                'goodwill_and_other_intangible_assets': [value * 0.2],
                'other_intangible_assets': [value * 0.05],
                'net_ppe': [value * 0.3],
                'accumulated_depreciation': [value * 0.1],
                'gross_ppe': [value * 0.4],
                'construction_in_progress': [value * 0.02],
                'other_properties': [value * 0.01],
                'machinery_furniture_equipment': [value * 0.15],
                'buildings_and_improvements': [value * 0.1],
                'land_and_improvements': [value * 0.02],
                'properties': [value * 0.01],
                'current_assets': [value * 0.3],
                'other_current_assets': [value * 0.05],
                'inventory': [value * 0.08],
                'finished_goods': [value * 0.03],
                'work_in_process': [value * 0.02],
                'raw_materials': [value * 0.03],
                'receivables': [value * 0.1],
                'receivables_adjustments_allowances': [value * 0.001],
                'other_receivables': [value * 0.02],
                'taxes_receivable': [value * 0.005],
                'accounts_receivable': [value * 0.07],
                'cash_cash_equivalents_and_short_term_investments': [value * 0.05],
                'other_short_term_investments': [value * 0.02],
                'cash_and_cash_equivalents': [value * 0.03],
                'cash_equivalents': [value * 0.01],
                'cash_financial': [value * 0.005],
            })
        elif st_type == 'cashflow':
            data_dict.update({
                'operating_cash_flow': [value],
                'investing_cash_flow': [value * 0.05],
                'financing_cash_flow': [value * -0.02],
                'capital_expenditure': [value * -0.1],
                'dividends_paid': [value * -0.03],
                'issuance_of_stock': [value * 0.01],
                'repurchase_of_stock': [value * -0.015],
                'net_change_in_cash': [value * 0.005],
                'depreciation': [value * 0.04],
                'stock_based_compensation': [value * 0.008],
                'deferred_income_tax': [value * 0.002],
                'accounts_receivable': [value * -0.01],
                'accounts_payable_cashflow': [value * 0.005],
                'change_in_working_capital': [value * 0.003],
                'other_operating_activities': [value * 0.001],
                'other_investing_activities': [value * 0.0005],
                'other_financing_activities': [value * 0.0002],
                'free_cash_flow': [value * 0.9],
                'effect_of_exchange_rate_changes': [value * 0.0001],
                'net_income_cash_flow': [value * 0.8],
                'purchase_of_investments': [value * -0.04],
                'sale_of_investments': [value * 0.01],
                'net_borrowings': [value * 0.005],
                'cash_flow_from_discontinued_operations': [value * 0.0001],
                'change_in_inventory': [value * -0.005],
                'change_in_other_current_assets': [value * -0.002],
                'change_in_other_current_liabilities': [value * 0.001],
                'change_in_other_non_current_assets': [value * 0.0001],
                'change_in_other_non_current_liabilities': [value * 0.0001],
                'change_in_deferred_revenue': [value * 0.0003],
                'change_in_deferred_income_tax': [value * 0.0001],
                'change_in_accounts_receivable': [value * -0.001],
                'change_in_accounts_payable': [value * 0.0005],
                'change_in_inventory_cashflow': [value * -0.0005],
                'change_in_other_working_capital': [value * 0.0003],
                'net_cash_provided_by_operating_activities': [value * 0.95],
                'net_cash_used_for_investing_activities': [value * -0.06],
                'net_cash_used_by_financing_activities': [value * -0.01],
            })
        
        df = pd.DataFrame(data_dict)
        return df

    @mock.patch('utils.company_utils.yf.Ticker')
    @mock.patch('utils.company_utils.time.sleep')
    def test_get_company_info_from_yfinance_success(self, mock_sleep, mock_ticker):
        """企業情報の取得が成功した場合のテスト"""
        mock_info = {
            'shortName': 'Test Company',
            'longBusinessSummary': 'Summary',
            'sector': 'Tech',
            'industry': 'Software',
            'fullTimeEmployees': 1000,
            'country': 'USA',
            'website': 'http://test.com',
            'marketCap': 1000000000,
            'currency': 'USD',
            'exchange': 'NYSE',
            'quoteType': 'EQUITY',
            'market': 'us_market',
            'address1': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip': '90210',
            'phone': '555-1234',
        }
        mock_ticker.return_value = MockTicker('TEST', info_data=mock_info)

        result = get_company_info_from_yfinance('TEST')

        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertEqual(result['symbol'].iloc[0], 'TEST')
        self.assertEqual(result['shortName'].iloc[0], 'Test Company')
        mock_sleep.assert_called_once_with(DEFAULT_REQUEST_DELAY)

    @mock.patch('utils.company_utils.yf.Ticker')
    @mock.patch('utils.company_utils.time.sleep')
    def test_get_company_info_from_yfinance_no_data(self, mock_sleep, mock_ticker):
        """企業情報が見つからない場合のテスト"""
        mock_ticker.return_value = MockTicker('TEST', info_data={}) # Empty info dict
        
        result = get_company_info_from_yfinance('TEST')
        
        self.assertIsNone(result)
        mock_sleep.assert_called_once_with(DEFAULT_REQUEST_DELAY)

    @mock.patch('utils.company_utils.yf.Ticker')
    @mock.patch('utils.company_utils.time.sleep')
    def test_get_company_info_from_yfinance_exception(self, mock_sleep, mock_ticker):
        """企業情報取得時に例外が発生した場合のテスト"""
        mock_ticker.return_value = MockTicker('TEST', raise_exception=True)
        
        result = get_company_info_from_yfinance('TEST')
        
        self.assertIsNone(result)
        # sleep should still be called because it's before the property access
        mock_sleep.assert_called_once_with(DEFAULT_REQUEST_DELAY)

    @mock.patch('utils.company_utils.yf.Ticker')
    @mock.patch('utils.company_utils.time.sleep')
    def test_get_financial_statements_from_yfinance_success(self, mock_sleep, mock_ticker):
        """財務諸表データの取得が成功した場合のテスト (年次/四半期、損益計算書/貸借対照表/キャッシュフロー)"""
        test_cases = [
            # (statement_type, period, mock_ticker_attr, expected_column, expected_value, date_obj)
            ('financials', 'annual', 'financials', 'total_revenue', 1000, datetime.date(2023, 12, 31)),
            ('balance_sheet', 'quarterly', 'quarterly_balance_sheet', 'total_assets', 2000, datetime.date(2023, 9, 30)),
            ('cashflow', 'annual', 'cashflow', 'operating_cash_flow', 300, datetime.date(2023, 12, 31)),
            ('financials', 'quarterly', 'quarterly_financials', 'total_revenue', 100, datetime.date(2023, 9, 30)),
            ('balance_sheet', 'annual', 'balance_sheet', 'total_assets', 200, datetime.date(2023, 12, 31)),
            ('cashflow', 'quarterly', 'quarterly_cashflow', 'operating_cash_flow', 30, datetime.date(2023, 9, 30)),
        ]

        for st_type, period, mock_attr, expected_col, expected_val, date_obj in test_cases:
            with self.subTest(f"type={st_type}, period={period}"):
                # Prepare mock data for the current test case
                mock_data = pd.DataFrame({
                    pd.to_datetime(date_obj): [expected_val, expected_val * 0.5]
                }, index=[expected_col.replace('_', ' ').title(), 'Some Other Metric']) # yfinance uses title case for index

                # Dynamically set the correct attribute on MockTicker
                mock_ticker_kwargs = {f"{mock_attr}_data": mock_data}
                mock_ticker.return_value = MockTicker('TEST', **mock_ticker_kwargs)

                result = get_financial_statements_from_yfinance('TEST', st_type, period)

                self.assertIsNotNone(result)
                self.assertIsInstance(result, pd.DataFrame)
                self.assertFalse(result.empty)
                self.assertEqual(result['symbol'].iloc[0], 'TEST')
                self.assertEqual(result[expected_col].iloc[0], expected_val)
                self.assertEqual(result['period_type'].iloc[0], period)
                self.assertEqual(result['statement_type'].iloc[0], st_type)
                self.assertEqual(result['year'].iloc[0], date_obj.year)
                self.assertEqual(result['month'].iloc[0], date_obj.month)
                self.assertEqual(result['day'].iloc[0], date_obj.day)
                self.assertEqual(result['report_date'].iloc[0], date_obj)
                mock_sleep.assert_called_once_with(DEFAULT_REQUEST_DELAY)
                mock_sleep.reset_mock() # Reset mock for next iteration

    @mock.patch('utils.company_utils.yf.Ticker')
    @mock.patch('utils.company_utils.time.sleep')
    def test_get_financial_statements_from_yfinance_empty_data(self, mock_sleep, mock_ticker):
        """財務諸表データが空の場合のテスト"""
        mock_ticker.return_value = MockTicker('TEST', financials_data=pd.DataFrame()) # Empty DataFrame
        
        result = get_financial_statements_from_yfinance('TEST', 'financials', 'annual')
        
        self.assertIsNone(result)
        mock_sleep.assert_called_once_with(DEFAULT_REQUEST_DELAY)

    @mock.patch('utils.company_utils.yf.Ticker')
    @mock.patch('utils.company_utils.time.sleep')
    def test_get_financial_statements_from_yfinance_exception(self, mock_sleep, mock_ticker):
        """財務諸表取得時に例外が発生した場合のテスト"""
        mock_ticker.return_value = MockTicker('TEST', raise_exception=True)
        
        result = get_financial_statements_from_yfinance('TEST', 'financials', 'annual')
        
        self.assertIsNone(result)
        # sleep should still be called because it's before the property access
        mock_sleep.assert_called_once_with(DEFAULT_REQUEST_DELAY)

    @mock.patch('utils.company_utils.yf.Ticker')
    @mock.patch('utils.company_utils.time.sleep')
    def test_get_financial_statements_from_yfinance_invalid_statement_type(self, mock_sleep, mock_ticker):
        """無効なstatement_typeが指定された場合のテスト"""
        # ValueErrorがtryブロックの外で発生するため、テストで捕捉できる
        with self.assertRaises(ValueError) as cm:
            get_financial_statements_from_yfinance('TEST', 'invalid_type', 'annual')
        self.assertIn("Invalid statement_type", str(cm.exception))
        mock_sleep.assert_not_called() # 入力値が無効な場合はsleepは呼び出されない

    @mock.patch('utils.company_utils.get_stock_list')
    @mock.patch('utils.company_utils.WebHDFSHook')
    @mock.patch('utils.company_utils.get_company_info_from_yfinance')
    @mock.patch('utils.company_utils.tempfile.NamedTemporaryFile')
    @mock.patch('utils.company_utils.os.remove')
    def test_process_company_info_data_success(self, mock_os_remove, mock_temp_file, mock_get_company_info, mock_hdfs_hook_class, mock_get_stock_list):
        """企業情報処理とHDFSアップロードが成功した場合のテスト"""
        mock_get_stock_list.return_value = ['TEST1.T', 'TEST2.T']
        
        mock_info_data1 = pd.DataFrame([{
            'symbol': 'TEST1.T', 'shortName': 'Comp1', 'sector': 'Tech'
        }])
        mock_info_data2 = pd.DataFrame([{
            'symbol': 'TEST2.T', 'shortName': 'Comp2', 'sector': 'Finance'
        }])
        mock_get_company_info.side_effect = [mock_info_data1, mock_info_data2]

        # Mock tempfile to return a mock file object
        mock_file = mock.MagicMock()
        mock_file.name = "/tmp/mock_company_info.csv"
        mock_temp_file.return_value.__enter__.return_value = mock_file

        mock_hdfs_hook = mock.MagicMock()
        mock_hdfs_hook_class.return_value = mock_hdfs_hook

        process_company_info_data(hdfs_conn_id="test_hdfs_conn", market="prime")

        mock_get_stock_list.assert_called_once_with("prime")
        self.assertEqual(mock_get_company_info.call_count, 2)
        mock_temp_file.assert_called_once_with(mode='w', delete=False, suffix=".csv")
        # mock_file.to_csv.assert_called_once() は不要なため削除
        mock_hdfs_hook.load_file.assert_called_once_with(
            source="/tmp/mock_company_info.csv",
            destination=f"{HDFS_PATHS['company_info']}/company_info.csv",
            overwrite=True
        )
        mock_os_remove.assert_called_once_with("/tmp/mock_company_info.csv")

    @mock.patch('utils.company_utils.get_stock_list')
    @mock.patch('utils.company_utils.WebHDFSHook')
    @mock.patch('utils.company_utils.get_company_info_from_yfinance')
    @mock.patch('utils.company_utils.tempfile.NamedTemporaryFile')
    @mock.patch('utils.company_utils.os.remove')
    def test_process_company_info_data_no_data(self, mock_os_remove, mock_temp_file, mock_get_company_info, mock_hdfs_hook_class, mock_get_stock_list):
        """企業情報が取得できない場合のテスト"""
        mock_get_stock_list.return_value = ['TEST1.T']
        mock_get_company_info.return_value = None # No data returned

        mock_hdfs_hook = mock.MagicMock()
        mock_hdfs_hook_class.return_value = mock_hdfs_hook

        process_company_info_data(hdfs_conn_id="test_hdfs_conn", market="prime")

        mock_get_stock_list.assert_called_once_with("prime")
        mock_get_company_info.assert_called_once_with('TEST1.T')
        mock_hdfs_hook.load_file.assert_not_called() # Should not call load_file
        mock_os_remove.assert_not_called() # Should not create/remove temp file

    @mock.patch('utils.company_utils.get_stock_list')
    @mock.patch('utils.company_utils.WebHDFSHook')
    @mock.patch('utils.company_utils.get_company_info_from_yfinance')
    @mock.patch('utils.company_utils.tempfile.NamedTemporaryFile')
    @mock.patch('utils.company_utils.os.remove')
    def test_process_company_info_data_hdfs_error(self, mock_os_remove, mock_temp_file, mock_get_company_info, mock_hdfs_hook_class, mock_get_stock_list):
        """企業情報HDFSアップロード時にエラーが発生した場合のテスト"""
        mock_get_stock_list.return_value = ['TEST1.T']
        mock_info_data1 = pd.DataFrame([{
            'symbol': 'TEST1.T', 'shortName': 'Comp1', 'sector': 'Tech'
        }])
        mock_get_company_info.return_value = mock_info_data1

        mock_file = mock.MagicMock()
        mock_file.name = "/tmp/mock_company_info.csv"
        mock_temp_file.return_value.__enter__.return_value = mock_file

        mock_hdfs_hook = mock.MagicMock()
        mock_hdfs_hook_class.return_value = mock_hdfs_hook
        mock_hdfs_hook.load_file.side_effect = Exception("HDFS Upload Error") # Simulate HDFS error

        process_company_info_data(hdfs_conn_id="test_hdfs_conn", market="prime")

        mock_hdfs_hook.load_file.assert_called_once()
        mock_os_remove.assert_called_once_with("/tmp/mock_company_info.csv") # Temp file should still be removed

    @mock.patch('utils.company_utils.get_stock_list')
    @mock.patch('utils.company_utils.WebHDFSHook')
    @mock.patch('utils.company_utils.get_financial_statements_from_yfinance')
    @mock.patch('utils.company_utils.write_to_hdfs')
    @mock.patch('utils.company_utils.logging.error') # Add this mock
    def test_process_financial_data_hdfs_error(self, mock_logging_error, mock_write_to_hdfs, mock_get_financial_statements, mock_hdfs_hook_class, mock_get_stock_list):
        """財務諸表HDFSアップロード時にエラーが発生した場合のテスト"""
        mock_get_stock_list.return_value = ['TEST1.T', 'TEST2.T'] # 複数のティッカーを使用

        # 2つのティッカーと6つの組み合わせ (2期間 * 3ステートメントタイプ) のための side_effect を拡張
        mock_get_financial_statements.side_effect = [
            # Annual Financials
            self._create_mock_financial_df_output('TEST1.T', 'financials', 'annual', datetime.date(2023, 12, 31), 100),
            self._create_mock_financial_df_output('TEST2.T', 'financials', 'annual', datetime.date(2023, 12, 31), 150),
            # Annual Balance Sheet
            self._create_mock_financial_df_output('TEST1.T', 'balance_sheet', 'annual', datetime.date(2023, 12, 31), 200),
            self._create_mock_financial_df_output('TEST2.T', 'balance_sheet', 'annual', datetime.date(2023, 12, 31), 250),
            # Annual Cashflow
            self._create_mock_financial_df_output('TEST1.T', 'cashflow', 'annual', datetime.date(2023, 12, 31), 300),
            self._create_mock_financial_df_output('TEST2.T', 'cashflow', 'annual', datetime.date(2023, 12, 31), 350),
            # Quarterly Financials
            self._create_mock_financial_df_output('TEST1.T', 'financials', 'quarterly', datetime.date(2023, 9, 30), 10),
            self._create_mock_financial_df_output('TEST2.T', 'financials', 'quarterly', datetime.date(2023, 9, 30), 15),
            # Quarterly Balance Sheet
            self._create_mock_financial_df_output('TEST1.T', 'balance_sheet', 'quarterly', datetime.date(2023, 9, 30), 20),
            self._create_mock_financial_df_output('TEST2.T', 'balance_sheet', 'quarterly', datetime.date(2023, 9, 30), 25),
            # Quarterly Cashflow
            self._create_mock_financial_df_output('TEST1.T', 'cashflow', 'quarterly', datetime.date(2023, 9, 30), 30),
            self._create_mock_financial_df_output('TEST2.T', 'cashflow', 'quarterly', datetime.date(2023, 9, 30), 35),
        ]
        
        mock_write_to_hdfs.side_effect = Exception("HDFS Write Error") # Simulate HDFS error

        mock_hdfs_hook = mock.MagicMock()
        mock_hdfs_hook_class.return_value = mock_hdfs_hook

        process_financial_data(hdfs_conn_id="test_hdfs_conn", market="prime")

        mock_get_stock_list.assert_called_once_with("prime")
        self.assertEqual(mock_get_financial_statements.call_count, 12) # 2 tickers * 2 periods * 3 statement types
        self.assertEqual(mock_write_to_hdfs.call_count, 6) # Still 6 calls, one for each (period, st_type) combination

        # Assert that logging.error was called for each failed write attempt
        # There are 6 combinations (period, st_type), and for each, write_to_hdfs is called.
        # If write_to_hdfs fails, logging.error is called.
        self.assertEqual(mock_logging_error.call_count, 6)
        # Check one of the error messages (the exact message format depends on the function's logging)
        # The format string is "Error processing financial data for %s, %s, %s: %s"
        mock_logging_error.assert_any_call(
            mock.ANY, # The format string
            'TEST1.T', 'financials', 'annual', mock.ANY # The exception object
        )
        mock_logging_error.assert_any_call(
            mock.ANY, # The format string
            'TEST2.T', 'cashflow', 'quarterly', mock.ANY # The exception object
        )
        
        # write_to_hdfs への呼び出しを検証
        # 渡されたDataFrameの内容を一部検証 (最初の呼び出しのDataFrame)
        # これは 'annual', 'financials' の TEST1.T と TEST2.T の結合されたDataFrameになる
        df_passed_to_hdfs_annual_financials = mock_write_to_hdfs.call_args_list[0].args[0]
        self.assertIsInstance(df_passed_to_hdfs_annual_financials, pd.DataFrame)
        self.assertIn('Date', df_passed_to_hdfs_annual_financials.index.name) # write_to_hdfs は 'Date' をインデックスとして期待
        
        # Dateインデックスが非ユニークになるため、.loc[date] は Series を返す
        # .iloc[0] と .iloc[1] でそれぞれのティッカーのデータを検証
        self.assertEqual(df_passed_to_hdfs_annual_financials['symbol'].loc[datetime.date(2023, 12, 31)].iloc[0], 'TEST1.T')
        self.assertEqual(df_passed_to_hdfs_annual_financials['total_revenue'].loc[datetime.date(2023, 12, 31)].iloc[0], 100)

        self.assertEqual(df_passed_to_hdfs_annual_financials['symbol'].loc[datetime.date(2023, 12, 31)].iloc[1], 'TEST2.T')
        self.assertEqual(df_passed_to_hdfs_annual_financials['total_revenue'].loc[datetime.date(2023, 12, 31)].iloc[1], 150)
