
"""
GIC.py - Easier way to track your GICs

Usage:

    date custom "GIC" [AccountName] [AccountFrom] [AccountInterest] [Principal] [Interest Rate] [Duration (in months)] [AccountTo]

Example:
    2022-11-29 custom "GIC" Assets:GIC:Flexible Assets:BANK:Chequing Income:GIC:Interest 5000 CAD 4.5 12

    date: 2022-11-29
    custom "GIC" -> tells the plugin to notice this statement
    Assets:GIC:Flexible -> The account created for the GIC
    Assets:BANK:Chequing -> The account to withdraw the chequing amount from
    Income:GIC:Interest -> The long-lived account that accumulates the total value accured by the GIC
    5000 CAD -> The principal amount of 5000 CAD
    4.5 -> The annualized interest rate of 4.5%
    12 -> The duration of the GIC (12 months)

AccountTo allows you to choose another account to deposit the money to. The default value is AccountFrom

"""

from beancount.parser import parser, booking
from beancount.core import data
from beancount.core.amount import Amount
from beancount.core.number import D
from beancount import loader
import datetime
import textwrap
Account = str

# defines the function to run when the plugin is called
__plugins__ = ('GIC_plugin',)

# Helper function to add months to a Date object
def addMonths(current_date, months):
    year = current_date.year + (current_date.month + months - 1) // 12
    month = (current_date.month + months - 1) % 12 + 1

    return datetime.date(year, month, current_date.day)

# Pulled from beancount
def parse(input_string):
    """Parse some input string and assert no errors.

    This parse function does not just create the object, it also triggers local
    interpolation to fill in the missing amounts.

    Args:
      input_string: Beancount input text.
    Returns:
      A list of directive objects.
    """
    entries, errors, options_map = parser.parse_string(textwrap.dedent(input_string))
    if errors:
        printer.print_errors(errors, file=sys.stderr)
        raise ValueError("Parsed text has errors")

    # Interpolation.
    entries, unused_balance_errors = booking.book(entries, options_map)

    # This is modified, because we are only parsing one transaction at a time
    return entries[0]


def calc_interest(interest, months, amount):
    return ((interest/100)*(months/12)+1)*amount

class GIC():
    dateStart: str
    dateEnd: str
    name: Account
    accountFrom: Account
    accountIncome: Account
    amount: Amount
    accountTo: Account
    interestRate: D
    months: D
    amountTo: Amount

    def __init__(self, dateStart, name, accountFrom, accountIncome, amount, interestRate, months, accountTo=None):
        self.name        = name.value
        self.accountFrom = accountFrom.value
        self.accountIncome = accountIncome.value

        self.amount      = amount.value
        self.interestRate    = interestRate.value

        self.dateStart   = dateStart.isoformat()
        self.months      = months.value

        self.accountTo = accountFrom.value if accountTo is None else accountTo.value
        self.dateEnd = addMonths(dateStart, int(months.value)).isoformat()

        interest = calc_interest(interestRate.value, months.value, amount.value.number)

        self.amountEnd = Amount(D(interest), amount.value.currency)

    def get_open_entry(self):
        parseString = f"{self.dateStart} open {self.name}"
        return parse(parseString)

    def get_principaldeposit_entry(self):
        parseString = f"{self.dateStart} *\n {self.name} {self.amount}\n {self.accountFrom}"
        return parse(parseString)

    def get_interestpayment_entry(self):
        parseString = f"{self.dateEnd} *\n {self.accountTo} {self.amountEnd}\n {self.name} -{self.amount}\n {self.accountIncome}"
        return parse(parseString)

    def get_close_entry(self):
        parseString = f"{self.dateEnd} close {self.name}"
        return parse(parseString)
    
    def get_entries(self):
        today = datetime.date.today()
        entries = []
        entries.append(self.get_open_entry())
        entries.append(self.get_principaldeposit_entry())
        if(today > datetime.date.fromisoformat(self.dateEnd)):
            entries.append(self.get_interestpayment_entry())
            entries.append(self.get_close_entry())
        return entries


def GIC_plugin(entries, option_map):

    gic_entries = []
    nongic_entries = []

    for entry in entries:
        if(isinstance(entry, data.Custom) and entry.type=='GIC'):
            gic_entries.append(entry)
        else:
            nongic_entries.append(entry)

    new_entries = []
    for entry in gic_entries:
        gic = GIC(entry.date, *(entry.values))
        new_entries.extend(gic.get_entries())

    new_entries.sort(key=data.entry_sortkey)
    return (nongic_entries + new_entries, [])

# filename = 'test.beancount'
# entries, errors, options = loader.load_file(filename)
# GIC_plugin(entries, options)
