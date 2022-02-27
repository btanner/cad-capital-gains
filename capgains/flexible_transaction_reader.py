import csv
import math

from click import ClickException
import dataclasses
from datetime import datetime
from decimal import Decimal, InvalidOperation
from capgains import transaction
from capgains import transactions
# import transactions
from typing import Any, Callable, Optional, Sequence

CSV_ENTRY = Sequence[str]


@dataclasses.dataclass
class TransactionParser:
    name: str
    date_fn: Callable[[CSV_ENTRY, ], datetime.date]
    description_fn: Callable[[CSV_ENTRY, ], str]
    ticker_fn: Callable[[CSV_ENTRY, ], str]
    action_fn: Callable[[CSV_ENTRY, ], transaction.TransactionType]
    qty_fn: Callable[[CSV_ENTRY, ], Decimal]
    price_fn: Callable[[CSV_ENTRY, ], Decimal]
    commission_fn: Callable[[CSV_ENTRY, ], Decimal]
    currency_fn: Callable[[CSV_ENTRY, ], Decimal]
    net_fn: Callable[[CSV_ENTRY, ], Decimal]

    def make_transaction(self, entry: CSV_ENTRY) -> transaction.Transaction:
        transaction_values = {
            'date': self.date_fn(entry),
            'description': self.description_fn(entry),
            'ticker': self.ticker_fn(entry),
            'action': self.action_fn(entry),
            'qty': self.qty_fn(entry),
            'price': self.price_fn(entry),
            'commission': self.commission_fn(entry),
            'currency': self.currency_fn(entry),
            'net': self.net_fn(entry),
        }
        return transaction.Transaction(**transaction_values)

def make_transaction_parser() -> TransactionParser:
    """Sample transaction parser for Questrade download."""

    def action_fn(entry: CSV_ENTRY):
        action_str = entry[2]
        if action_str == '':
            if entry[12].casefold() == 'dividends':
                action_str = 'div'
        return transaction.TransactionType.parse(action_str)

    parser = TransactionParser(
        name="Questrade Activity Summary Report",
        date_fn=lambda x: datetime.strptime(x[0].split(" ")[0], '%Y-%m-%d').date(),
        description_fn=lambda x: x[4],
        qty_fn=lambda x: abs(Decimal(x[5])),
        net_fn=lambda x: abs(Decimal(x[9])),
        price_fn=lambda x: Decimal(x[6]),
        commission_fn=lambda x: abs(Decimal(x[8])),
        action_fn=action_fn,
        currency_fn=lambda x: x[10],
        ticker_fn=lambda x: x[3],
    )
    return parser


def get_transactions(csv_file, parser: TransactionParser, skip_first_row: bool):
    """Convert the CSV-file entries into a list of Transactions."""
    keep_actions = (
        transaction.TransactionType.BUY, transaction.TransactionType.SELL, transaction.TransactionType.DIVIDEND,
        transaction.TransactionType.FEE)

    all_transactions = []
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        for entry_no, raw_entry in enumerate(reader):
            if skip_first_row and entry_no == 0:
                continue
            this_transaction = parser.make_transaction(raw_entry)
            if this_transaction.action not in keep_actions:
                continue
            all_transactions.append(this_transaction)
    all_transactions.sort(key=lambda x: x.date)
    return transactions.Transactions(all_transactions)