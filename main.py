import os
import pandas as pd
import datetime as dt
from datetime import timedelta
from matplotlib import pyplot as plt


pd.set_option('display.max_rows', 10)


class Entry:
    def __init__(self, date=dt.date.today(), category=None, credit=0.0, debit=0.0, remark=None, balance=None):
        self.date = parse_date(date) if isinstance(date, str) else date
        self.category = category
        self.credit = credit
        self.debit = debit
        self.remark = remark
        self.balance = balance

    def entry(self):
        return {
            'date': self.date, 'category': self.category, 'credit': self.credit,
            'debit': self.debit, 'remark': self.remark, 'balance': self.balance
        }

    def copy(self):
        return Entry(date=self.date, category=self.category, credit=self.credit, debit=self.debit,
                     remark=self.remark, balance=self.balance)

    def __getitem__(self, item):
        return self.entry().__getitem__(item)

    def __repr__(self):
        return self.entry().__repr__()


class Food(Entry):
    def __init__(self, food_debit, food_remark, food_date=None):
        if food_date:
            super().__init__(date=food_date, category="Food", debit=food_debit, remark=food_remark)
        else:
            super().__init__(category="Food", debit=food_debit, remark=food_remark)


class Breakfast(Food):
    def __init__(self, food_debit, food_date=None):
        if food_date:
            super().__init__(food_debit, "Breakfast", food_date)
        else:
            super().__init__(food_debit, "Breakfast")


class Lunch(Food):
    def __init__(self, food_debit, food_date=None):
        if food_date:
            super().__init__(food_debit, "Lunch", food_date)
        else:
            super().__init__(food_debit, "Lunch")


class Dinner(Food):
    def __init__(self, food_debit, food_date=None):
        if food_date:
            super().__init__(food_debit, "Dinner", food_date)
        else:
            super().__init__(food_debit, "Dinner")


class ExpenseManager:
    def __init__(self, csv_filename):
        self.filename = csv_filename
        self.df = pd.read_csv(csv_filename,
                              names=['date', 'category', 'credit', 'debit', 'remark', 'balance'],
                              skiprows=1)
        self._preprocess_df()
        self.balance = self.df['balance'].iloc[-1]
        self.view_month = dt.date.today().month

    def __repr__(self):
        return f'ExpenseManager(Entries: {len(self.df) - 1}, Balance: {round(self.balance, 2)})'

    ''' ################# Private methods ################## '''

    def _map_str_to_date(self):
        self.df['date'] = self.df['date'] \
            .map(lambda d: dt.datetime.strptime(d, "%Y-%m-%d").date() if isinstance(d, str) else d)

    def _map_float_to_rounded(self):
        self.df['balance'] = self.df['balance'].map(lambda flt: round(flt, 2))

    def _preprocess_df(self):
        self._map_str_to_date()
        self._map_float_to_rounded()

    def _add_dummy_entry(self):
        self._add_entry(Entry(balance=0.0).entry)
        self._save_file()

    def _calculate_balance(self, expense_entry):
        new_balance = self.balance
        new_balance += expense_entry['credit'] - expense_entry['debit']
        return new_balance

    def _add_entry(self, entry_dict):
        self.df = self.df.append(entry_dict, ignore_index=True)

    def _save_file(self):
        self.balance = self.df['balance'].iloc[-1]
        self._preprocess_df()
        self.df.to_csv(self.filename, index=False)

    def _get_df_by_month(self):
        month_mask = self.df['date'].map(lambda d: d.month) == self.view_month
        filtered_df = self.df[month_mask]
        return filtered_df

    def _get_grouped_datebalance(self):
        filtered_df = self._get_df_by_month()
        return filtered_df[['date', 'balance']].groupby('date', as_index=False).agg(lambda s: s.iloc[-1])

    ''' ################# CRUD methods ################# '''

    def add(self, expense_entry):
        if expense_entry['balance'] is None:
            expense_entry.balance = self._calculate_balance(expense_entry)

        self._add_entry(expense_entry.entry())
        self._save_file()
        print(f"Added entry.")

    def clear(self):
        if get_confirmation():
            self.df = self.df.iloc[0: 0]
            print(f"Cleared entries.")
            self._save_file()
        else:
            print("No changes made.")

    def remove(self, *indices):
        if not indices:
            return

        self.df = self.df.drop(list(map(int, indices)))
        self._save_file()

        if len(indices) > 1:
            print("Deleted specified entries.")
        else:
            print("Deleted entry.")

    def set_month(self, value):
        if value not in range(1, 12):
            return
        self.view_month = value

    def view(self, *num):
        filtered_df = self._get_df_by_month()
        if num:
            return filtered_df.tail(num[0])
        return filtered_df

    def usage(self):
        filtered_df = self._get_grouped_datebalance()
        usage_list = []

        for i in range(len(filtered_df['date']) - 1):
            balance_before = filtered_df['balance'][i]
            balance_after = filtered_df['balance'][i + 1]
            usage_list.append(round(balance_after - balance_before, 2))

        string_usage_list = list(map(lambda u: str(u) if u <= 0 else f'+{u}', usage_list))
        string_usage_list.insert(0, '')
        filtered_df['usage'] = string_usage_list
        return filtered_df

    ''' ################# Stats methods ################# '''

    def plot(self):
        df_to_plot = self._get_grouped_datebalance()

        #plt.figure('ExpenseManager')
        dummy = df_to_plot['date'][0]
        plt.title(f'{dummy.strftime("%B")} {dummy.year}')
        plt.xlabel('Day of month')
        plt.ylabel('Balance')

        df_to_plot['date'] = df_to_plot['date'].map(lambda d: d.day)
        plt.plot(df_to_plot['date'], df_to_plot['balance'])

        plt.show()


''' ################# Global methods ################# '''


def get_confirmation():
    confirmation = input("Are you sure? y/n\n!>> ")
    return confirmation.lower() == 'y'


def parse_date(date_string):
    if date_string == 'yesterday':
        return dt.date.today() - timedelta(days=1)
    return dt.datetime.strptime(date_string, "%Y-%m-%d").date()

def get_today():
    return dt.date.today()

def is_currency(string):
    try:
        float(string)
        return True
    except Exception:
        return False

def handle_new_user(filename):
    input_message = "? What is your balance now\n$>> "
    error_message = "! Balance must be numeric!"

    balance = input(input_message)
    while not is_currency(balance):
        print(error_message)
        balance = input(input_message)
    balance = round(float(balance), 2)

    with open(filename, 'w') as file:
        file.write('date,category,credit,debit,remark,balance\n')
        file.write(f'{get_today()},,0.0,0.0,,{balance}\n')

    print(f'New csv file has been created: {filename}')


if __name__ == '__main__':
    default_filename = 'data.csv'
    if default_filename not in os.listdir():
        handle_new_user(default_filename)

    m = ExpenseManager(default_filename)
