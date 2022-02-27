from click import ClickException
from datetime import timedelta
from decimal import Decimal
from capgains import transaction


class TickerGains:
    def __init__(self, ticker):
        self.ticker = ticker
        self.share_balance = 0
        self.total_acb = 0
        self.total_dividends = 0

    @property
    def acb_per_share(self):
        if self.share_balance == 0:
            return 0.
        else:
            return self.total_acb / self.share_balance

    def add_transactions(self, all_transactions, exchange_rates):
        """Adds all transactions and updates the calculated values"""
        for t in all_transactions:
            rate = exchange_rates[t.currency].get_rate(t.date)
            t.exchange_rate = rate
            self._add_transaction(t)
            if self._is_superficial_loss(t, all_transactions):
                self.total_acb -= t.capital_gain
                t.set_superficial_loss()

    def _superficial_window_filter(self, trans, min_date, max_date):
        """Filter out BUY transactions that fall within
        the 61 day superficial loss window"""
        return trans.date >= min_date and trans.date <= max_date

    def _is_superficial_loss(self, trans, all_transactions):
        """Figures out if the transaction is a superficial loss"""
        # Has to be a capital loss
        if (trans.capital_gain >= 0):
            return False
        min_date = trans.date - timedelta(days=30)
        max_date = trans.date + timedelta(days=30)
        filtered_transactions = list(filter(
            lambda t: self._superficial_window_filter(t, min_date, max_date),
            all_transactions))
        # Has to have a purchase either 30 days before or 30 days after
        if (not any(t.action == transaction.TransactionType.BUY for t in filtered_transactions)):
            return False
        # Has to have a positive share balance after 30 days
        transaction_idx = filtered_transactions.index(trans)
        balance = trans.share_balance
        for window_transaction in filtered_transactions[transaction_idx+1:]:
            if window_transaction.action == transaction.TransactionType.SELL:
                balance -= window_transaction.qty
            else:
                balance += window_transaction.qty
        return balance > 0

    def _add_transaction(self, trans: transaction.Transaction):
        """Adds a transaction and updates the calculated values."""
        old_acb_per_share = self.acb_per_share
        proceeds = (trans.qty * trans.price) * trans.exchange_rate  # noqa: E501
        net = trans.net * trans.exchange_rate
        if trans.action == transaction.TransactionType.SELL:
            self.share_balance -= trans.qty
            acb = old_acb_per_share * trans.qty
            capital_gain = proceeds - trans.expenses - acb
            self.total_acb -= acb
        elif trans.action == transaction.TransactionType.BUY:
            self.share_balance += trans.qty
            acb = proceeds + trans.expenses
            capital_gain = Decimal(0.0)
            self.total_acb += acb
        elif trans.action == transaction.TransactionType.DIVIDEND:
            self.total_dividends += net  # pre-multiplied by exchange rate
            proceeds = 0.
            capital_gain = 0.
            acb = 0.
        else:
            print(f'Different action: {trans.action}')
        if self.share_balance < 0:
            raise ValueError("Transaction caused negative share balance")

        trans.share_balance = self.share_balance
        trans.proceeds = proceeds
        trans.capital_gain = capital_gain
        trans.acb = acb
