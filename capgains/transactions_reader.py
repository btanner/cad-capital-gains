"""Deprecated in favour of flexible_transaction_reader but tests and references not removed yet."""
import csv
import math

from click import ClickException
import dataclasses
from datetime import datetime
from decimal import Decimal, InvalidOperation
from .transaction import Transaction
from .transactions import Transactions
from typing import Any, Optional


@dataclasses.dataclass
class ParsedEntry:
    """Matches structure of Transaction but we'll build each incrementally."""
    date: Any=None
    description: str='?'
    ticker: str='?'
    action: str='?'
    qty: float = math.inf
    price: float = math.inf
    commission: float = math.inf
    currency: str = '?'
    net: float = math.inf

class TransactionsReader:
    """An interface that converts a CSV-file with transaction entries into a
    list of Transactions.
    """
    file_columns = [
        "transaction_date",
        "settle_date",
        "action",
        "symbol",
        "description",
        "qty",
        "price",
        "gross",
        "commission",
        "net",
        "currency",
        "account",
        "activity",
        "account_type",
    ]
    keep_actions = ['buy', 'sell', 'div', 'fch']
    skip_actions = ['fxt', 'con', 'dep']

    @classmethod
    def get_transactions(cls, csv_file):
        """Convert the CSV-file entries into a list of Transactions."""
        transactions = []
        pass_through_cols = {"description":"description", "action":"action", "currency":"currency","symbol":"ticker"}
        try:
            with open(csv_file, newline='') as f:
                reader = csv.reader(f)
                last_date = None
                for entry_no, raw_entry in enumerate(reader):
                    pass_through_vals = {v:raw_entry[cls.file_columns.index(k)] for k,v in pass_through_cols.items()}
                    if pass_through_vals['action'] == '':
                        # For some reason, some of these are mislabeled.
                        if raw_entry[cls.file_columns.index('activity')].casefold() == 'dividends':
                            pass_through_vals['action'] = 'div'
                        else:
                            print(f'WARNING - missing action for {raw_entry}')
                    pass_through_vals['action'] = pass_through_vals['action'].casefold()
                    if pass_through_vals['action'] not in cls.keep_actions:
                        # Probably should discard this row, but not before we make sure we expect to discard it.
                        if pass_through_vals['action'] not in cls.skip_actions:
                            print(f"Unknown action: {pass_through_vals['action']} not in our skip list. Entry:{raw_entry}")
                        else:
                            continue
                    entry = ParsedEntry(**pass_through_vals)
                    if entry_no == 0:
                        print('Skipping header row.')
                        continue
                    actual_num_columns = len(raw_entry)
                    expected_num_columns = len(cls.file_columns)
                    if actual_num_columns != expected_num_columns:
                        # Each line in the CSV file should have the same number
                        # of columns as we expect
                        raise ClickException(
                            "Transaction entry {}: expected {} columns, entry has {}"  # noqa: E501
                            .format(entry_no,
                                    expected_num_columns,
                                    actual_num_columns))
                    date_idx = cls.file_columns.index("transaction_date")
                    date_str = raw_entry[date_idx]
                    try:
                       entry.date = datetime.strptime(
                            date_str.split(" ")[0],
                            '%Y-%m-%d').date()
                    except ValueError:
                        raise ClickException(
                            "The date ({}) was not entered in the correct format (YYYY-MM-DD)"  # noqa: E501
                            .format(date_str))
                    qty_idx = cls.file_columns.index("qty")
                    qty_str = raw_entry[qty_idx]
                    try:
                        entry.qty = abs(Decimal(qty_str))  # We expect sold shares to be positive numbers.
                    except InvalidOperation:
                        raise ClickException(
                            "The quantity entered {} is not a valid number"
                            .format(qty_str))
                    net_idx = cls.file_columns.index("net")
                    net_str = raw_entry[net_idx]
                    try:
                        entry.net = abs(Decimal(net_str))
                    except InvalidOperation:
                        raise ClickException(
                            "The net entered {} is not a valid number"
                            .format(net_str))
                    price_idx = cls.file_columns.index("price")
                    price_str = raw_entry[price_idx]
                    try:
                        entry.price = Decimal(price_str)
                    except InvalidOperation:
                        raise ClickException(
                            "The price entered {} is not a valid number"
                            .format(price_str))
                    commission_idx = cls.file_columns.index("commission")
                    commission_str = raw_entry[commission_idx]
                    try:
                        entry.commission = Decimal(commission_str)
                    except InvalidOperation:
                        raise ClickException(
                            "The commission entered {} is not a valid number"
                            .format(commission_str))
                    transaction = Transaction(**dataclasses.asdict(entry))
                    transactions.append(transaction)
            transactions.sort(key=lambda x: x.date)

            return Transactions(transactions)
        except FileNotFoundError:
            raise ClickException("File not found: {}".format(csv_file))
        except OSError:
            raise OSError("Could not open {} for reading".format(csv_file))
