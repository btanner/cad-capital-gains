from capgains.commands.capgains_show import capgains_show
from capgains.commands.capgains_calc import capgains_calc
from capgains import flexible_transaction_reader
from capgains import transaction
from capgains import transactions
from capgains import handy_parser
from capgains import ticker_gains
import csv
from typing import Sequence

# TODO(bttanner): Write code to import tickers that we dumped EOY 2021.

def dump_tickers(out_csv_file: str, tickers: Sequence[ticker_gains.TickerGains]):
    with open(out_csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Symbol/Ticker', 'TotalACB', 'ShareBalance', 'ACBPERSHARE'])
        for ticker in tickers:
            if ticker.share_balance == 0 and ticker.total_acb != 0:
                raise ValueError(f'Ticker has no shares but ACB:{ticker}')
            if ticker.share_balance != 0:
                writer.writerow([ticker.ticker, ticker.total_acb, ticker.share_balance, ticker.acb_per_share])

def do_questrade_summary(year: int):
    transactions_csv = f'/home/btanner/Downloads/ariel_cash_questrade_{year}.csv'
    output_csv = f'/home/btanner/Downloads/ariel_cash_questrade_{year}_year_end_acb.csv'
    parser = handy_parser.make_questrade_parser()
    all_transactions = flexible_transaction_reader.get_transactions(transactions_csv, parser, skip_first_row=True)
    all_tickers = all_transactions.tickers
    if '' in all_tickers:
        all_tickers.remove('')
    no_ticker_transactions = all_transactions.filter_by(tickers='')
    # capgains_show(no_ticker_transactions, tickers=None)
    total_gains, total_dividends, final_ticker_gains = capgains_calc(no_ticker_transactions, year, tickers=all_tickers)
    fee_transactions = no_ticker_transactions.filter_by(action=transaction.TransactionType.FEE)
    total_fees = 0
    for t in fee_transactions:
        total_fees += t.net
    print(f'Totals:\tFees:{total_fees:.2f}\tGains:{total_gains:.2f}\tDividends:{total_dividends:.2f}')
    dump_tickers(output_csv, final_ticker_gains)


def do_morgan_stanley_summary():
    release_transactions_csv = '/home/btanner/Downloads/goog_releases_2021_usd.csv'
    release_parser = handy_parser.make_morgan_stanley_shares_released_parser(default_currency='USD')
    release_transactions = flexible_transaction_reader.get_transactions(release_transactions_csv, release_parser, skip_first_row=True)
    print('SUMMARY OF RELEASES WITHOUT SALES')
    capgains_calc(release_transactions, 2021, tickers=['GOOG'])
    sales_transactions_csv = '/home/btanner/Downloads/goog_sales_2021_usd.csv'
    sales_parser = handy_parser.make_morgan_stanley_shares_withdraw_parser(default_currency='USD')
    sales_transactions = flexible_transaction_reader.get_transactions(sales_transactions_csv, sales_parser,
                                                                        skip_first_row=True)
    all_raw_transactions = sales_transactions.transactions
    all_raw_transactions.extend(release_transactions.transactions)
    all_raw_transactions.sort(key=lambda x: x.date)
    all_transactions = transactions.Transactions(all_raw_transactions)
    capgains_calc(all_transactions, 2021, tickers=['GOOG'])


# do_morgan_stanley_summary()
do_questrade_summary(2021)
