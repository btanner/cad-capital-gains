from decimal import Decimal
import enum
import datetime


class TransactionType(enum.Enum):
    BUY = enum.auto()
    SELL = enum.auto()
    DIVIDEND = enum.auto()
    DEPOSIT = enum.auto()
    WITHDRAWAL = enum.auto()
    FEE = enum.auto()
    EXCHANGE = enum.auto()
    CONVERT = enum.auto

    @classmethod
    def parse(cls, str_type: str) -> 'TransactionType':
        str_type_lower = str_type.casefold()
        if str_type_lower == 'buy':
            return cls.BUY
        elif str_type_lower == 'sell':
            return cls.SELL
        elif str_type_lower == 'div' or str_type_lower == 'dividends':
            return cls.DIVIDEND
        elif str_type_lower == 'fch':
            return cls.FEE
        elif str_type_lower == 'fxt':
            return cls.EXCHANGE
        elif str_type_lower == 'con':
            return cls.CONVERT
        elif str_type_lower == 'dep':
            return cls.DEPOSIT
        else:
            raise ValueError(f'Unknown action: {str_type}')


class Transaction:
    """Represents a transaction entry from the CSV-file"""

    def __init__(self, date: datetime.date, description: str, ticker: str, action: TransactionType, qty: Decimal,
                 price: Decimal,
                 commission: Decimal, currency: Decimal, net: Decimal):
        self.date = date
        self.description = description
        self.ticker = ticker
        self.action = action
        self.qty = Decimal(qty)
        self.price = Decimal(price)
        self.net = Decimal(net)
        self.commission = Decimal(commission)
        self.currency = currency
        self.exchange_rate = None
        self._share_balance = Decimal(0.0)
        self.proceeds = Decimal(0.0)
        self.capital_gain = Decimal(0.0)
        self.acb = Decimal(0.0)
        self._superficial_loss = False


    @property
    def share_balance(self):
        return self._share_balance

    @share_balance.setter
    def share_balance(self, share_balance):
        if (share_balance < 0):
            raise ValueError("Share balance cannot be negative")
        self._share_balance = Decimal(share_balance)

    @property
    def superficial_loss(self):
        return self._superficial_loss

    @property
    def expenses(self):
        return self.commission * self.exchange_rate

    def set_superficial_loss(self):
        self._superficial_loss = True
        self.capital_gain = Decimal(0.0)
