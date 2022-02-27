from capgains.commands.capgains_show import capgains_show
from capgains.commands.capgains_calc import capgains_calc
# from capgains.transactions_reader import TransactionsReader
from capgains import flexible_transaction_reader
from capgains import transaction

transactions_csv = '/home/btanner/Downloads/ariel_cash_questrade_2021.csv'

parser = flexible_transaction_reader.make_transaction_parser()
print('parser made')
all_transactions = flexible_transaction_reader.get_transactions(transactions_csv, parser, skip_first_row=True)
all_tickers = all_transactions.tickers
if '' in all_tickers:
    all_tickers.remove('')
no_ticker_transactions = all_transactions.filter_by(tickers='')
capgains_show(no_ticker_transactions, tickers=None)
total_gains, total_dividends = capgains_calc(no_ticker_transactions, 2021, tickers=all_tickers)





# transactions = TransactionsReader.get_transactions(transactions_csv)
# # Pretty hacky, but fees will have no ticker, so handle separately.
# all_tickers = transactions.tickers
# if '' in all_tickers:
#     all_tickers.remove('')
# no_ticker_transactions = transactions.filter_by(tickers='')
# # capgains_show(transactions, tickers=None)
# total_gains, total_dividends = capgains_calc(transactions, 2021, tickers=all_tickers)
#
fee_transactions = no_ticker_transactions.filter_by(action=transaction.TransactionType.FEE)
total_fees = 0
for t in fee_transactions:
    total_fees += t.net
print(f'Totals:\tFees:{total_fees:.2f}\tGains:{total_gains:.2f}\tDividends:{total_dividends:.2f}')

