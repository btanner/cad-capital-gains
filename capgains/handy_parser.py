from capgains import flexible_transaction_reader
from capgains import transaction
import datetime
from decimal import Decimal
import math

def make_questrade_parser() -> flexible_transaction_reader.TransactionParser:
    """Sample transaction parser for Questrade download."""

    def action_fn(entry: flexible_transaction_reader.CSV_ENTRY):
        action_str = entry[2]
        if action_str == '':
            if entry[12].casefold() == 'dividends':
                action_str = 'div'
        return transaction.TransactionType.parse(action_str)

    parser = flexible_transaction_reader.TransactionParser(
        name="Questrade Activity Summary Report",
        date_fn=lambda x: datetime.datetime.strptime(x[0].split(" ")[0], '%Y-%m-%d').date(),
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

def make_morgan_stanley_shares_released_parser(default_currency: str) -> flexible_transaction_reader.TransactionParser:
    """Sample transaction parser for Morgan Stanley RSU-released download.
    Header looks like:
    Date  OrderNumber  Plan  Type  OrderStatus  Price	Quantity  NetShareProceeds  NetShareProceeds  TaxPaymentMethod

    First NetShareProceeds is shares, second is $$$.
    """
    parser = flexible_transaction_reader.TransactionParser(
        name="Morgan Stanley Share Released Report",
        date_fn=lambda x: datetime.datetime.strptime(x[0], '%d-%b-%Y').date(),
        description_fn=lambda x: x[3],
        qty_fn=lambda x: abs(Decimal(x[6])),
        net_fn=lambda x: -math.inf,  # Want this to screw up some math if used accidentally.
        price_fn=lambda x: Decimal(x[5].replace('$', '').replace(',','')),  # Download format determines default currency
        commission_fn=lambda x: abs(Decimal(0.)),
        action_fn=lambda x: transaction.TransactionType.BUY,
        currency_fn=lambda x: default_currency,
        ticker_fn=lambda x: "GOOG",
    )
    return parser


def make_morgan_stanley_shares_withdraw_parser(default_currency: str) -> flexible_transaction_reader.TransactionParser:
    """Sample transaction parser for Morgan Stanley RSU-withdrawn download.
    Header looks like:
    Date  OrderNumber  Plan  Type  OrderStatus  Price	Quantity  NetAmount  NetShareProceeds  TaxPaymentMethod

    Download format on their website determines currency, it's not obvious in the file.
    Also, monetary values are $xxx,yyy.zzz, need to strip out $ and ,
    """
    parser = flexible_transaction_reader.TransactionParser(
        name="Morgan Stanley Share Withdrawn Report",
        date_fn=lambda x: datetime.datetime.strptime(x[0], '%d-%b-%Y').date(),
        description_fn=lambda x: x[3],
        qty_fn=lambda x: abs(Decimal(x[6])),
        net_fn=lambda x: Decimal(x[7].replace('$', '').replace(',','')),
        price_fn=lambda x: Decimal(x[5].replace('$', '').replace(',','')),
        commission_fn=lambda x: abs(Decimal(0.)),
        action_fn=lambda x: transaction.TransactionType.SELL,
        currency_fn=lambda x: default_currency,
        ticker_fn=lambda x: "GOOG",
    )
    return parser