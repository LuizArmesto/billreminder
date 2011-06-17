import unittest
import sys
import os

from decimal import Decimal

sys.path += [os.path.abspath('..')]

from lib import dal, actions

class ActionsTest(unittest.TestCase):
    def setUp(self):
        import datetime

        self.dal = dal.DAL(fake=True)
        self.actions = actions.Actions(databaselayer=self.dal)

        self.today = datetime.date.today()
        self.tomorrow = self.today + datetime.timedelta(1)
        self.yesterday = self.today - datetime.timedelta(1)

        bills_orig = dict()

        # Create simple bills

        # Not paid, due date is today
        bills_orig['A'] = dal.Bill('A', Decimal('12.34'), self.today)
        # Not paid, due date is tomorrow
        bills_orig['B'] = dal.Bill('B', Decimal('123.45'), self.tomorrow)
        # Not paid, due date was yesterday
        bills_orig['C'] = dal.Bill('C', Decimal('1234.56'), self.yesterday)

        # Paid, due date is today
        bills_orig['D'] = dal.Bill('D', Decimal('12.34'), self.today,
                                   paid=True)
        # Paid, due date is tomorrow
        bills_orig['E'] = dal.Bill('E', Decimal('123.45'), self.tomorrow,
                                   paid=True)
        # Paid, due date was yesterday
        bills_orig['F'] = dal.Bill('F', Decimal('1234.56'), self.yesterday,
                                   paid=True)

        self.dal.add(bills_orig['A'])
        self.dal.add(bills_orig['B'])
        self.dal.add(bills_orig['C'])
        self.dal.add(bills_orig['D'])
        self.dal.add(bills_orig['E'])
        self.dal.add(bills_orig['F'])

    def test_count_not_paid(self):
        count = self.actions.count_not_paid()
        self.assertEqual(count, 3)

    def test_count_not_paid_start(self):
        count = self.actions.count_not_paid(start=self.today)
        self.assertEqual(count, 2)

        count = self.actions.count_not_paid(start=self.tomorrow)
        self.assertEqual(count, 1)

        count = self.actions.count_not_paid(start=self.yesterday)
        self.assertEqual(count, 3)

    def test_count_not_paid_end(self):
        count = self.actions.count_not_paid(end=self.yesterday)
        self.assertEqual(count, 1)

        count = self.actions.count_not_paid(end=self.today)
        self.assertEqual(count, 2)

        count = self.actions.count_not_paid(end=self.tomorrow)
        self.assertEqual(count, 3)

    def test_count_not_paid_start_and_end(self):
        count = self.actions.count_not_paid(start=self.yesterday, end=self.tomorrow)
        self.assertEqual(count, 3)

        count = self.actions.count_not_paid(start=self.today, end=self.tomorrow)
        self.assertEqual(count, 2)

        count = self.actions.count_not_paid(start=self.yesterday, end=self.today)
        self.assertEqual(count, 2)

        count = self.actions.count_not_paid(start=self.tomorrow, end=self.yesterday)
        self.assertEqual(count, 0)

    def test_get_bills(self):
        bill = self.actions.get_bills(payee='A')[0]
        self.assertEqual(bill.payee, 'A')
        self.assertEqual(bill.amount, Decimal('12.34'))


        bill = self.actions.get_bills(payee='B')[0]
        self.assertEqual(bill.payee, 'B')
        self.assertEqual(bill.amount, Decimal('123.45'))

    def test_add_category(self):
        category_orig = dal.Category('Groceries', 'c0c0c0')

        # Add category using DAL
        category_orig_id = self.dal.add(category_orig)

        session = self.dal.Session()
        category = session.query(dal.Category).filter(dal.Category.name=='Groceries').first()

        self.assertEqual(category.name, 'Groceries')
        self.assertEqual(category.color, 'c0c0c0')
        self.assertEqual(category.id, category_orig_id)

        session.close()

    def test_add_category_twice(self):
        category_orig_A = dal.Category('Groceries', 'c0c0c0')
        category_orig_A_id = self.dal.add(category_orig_A)

        category_orig_B = dal.Category('Groceries', 'c0c0c0')
        category_orig_B_id = self.dal.add(category_orig_A)

        self.assertEqual(category_orig_A_id, category_orig_B_id)

        session = self.dal.Session()
        self.assertEqual(session.query(dal.Category).filter(dal.Category.name=='Groceries').count(), 1)
        session.close()

    def test_add_simple_bill(self):
        bills_orig = dict()
        bills = dict()

        # Create a simple bill
        bills_orig['Food Market'] = dal.Bill('Food Market', Decimal('123.94'), self.today)

        # Add bill using Actions
        self.actions.add(bills_orig['Food Market'])

        session = self.dal.Session()
        bills['Food Market'] = session.query(dal.Bill).filter(dal.Bill.payee=='Food Market').first()

        self.assertEqual(bills['Food Market'].payee, 'Food Market')
        self.assertEqual(bills['Food Market'].amount, Decimal('123.94'))
        self.assertEqual(bills['Food Market'].dueDate, self.today)
        self.assertEqual(bills['Food Market'].alarmDate, None)
        self.assertEqual(bills['Food Market'].notes, None)
        self.assertFalse(bills['Food Market'].paid)
        self.assertEqual(bills['Food Market'].repeats, None)
        self.assertEqual(bills['Food Market'].category, None)

        session.close()

    def test_add_bill_with_category(self):
        bills_orig = dict()
        bills = dict()

        category_orig = dal.Category('Groceries', 'c0c0c0')

        # Add category using Actions
        category_orig_id = self.actions.add(category_orig)

        session = self.dal.Session()
        category = session.query(dal.Category).filter(dal.Category.name=='Groceries').first()

        # Create a simple bill
        bills_orig['Food Market'] = dal.Bill('Food Market', Decimal('123.94'), self.today, category=dal.Category('Groceries', 'c0c0c0'))

        session.close()

        # Add bill using Actions
        self.assertEqual(self.actions.add(bills_orig['Food Market']), 7)

        session = self.dal.Session()
        category = session.query(dal.Category).filter(dal.Category.name=='Groceries').first()
        bills['Food Market'] = session.query(dal.Bill).filter(dal.Bill.payee=='Food Market').first()

        self.assertEqual(bills['Food Market'].payee, 'Food Market')
        self.assertEqual(bills['Food Market'].amount, Decimal('123.94'))
        self.assertEqual(bills['Food Market'].dueDate, self.today)
        self.assertEqual(bills['Food Market'].alarmDate, None)
        self.assertEqual(bills['Food Market'].notes, None)
        self.assertFalse(bills['Food Market'].paid)
        self.assertEqual(bills['Food Market'].repeats, None)
        self.assertEqual(bills['Food Market'].category.id, category_orig_id)

        session.close()

    def test_add_bill_with_new_category(self):
        bills_orig = dict()
        bills = dict()
        category_orig = dal.Category('Nothing', 'c0c0c0')

        # Create a simple bill
        bills_orig['Food Market'] = dal.Bill('Food Market', Decimal('123.94'), self.today, category=category_orig)

        # Add bill using Actions
        self.actions.add(bills_orig['Food Market'])

        session = self.dal.Session()
        bills['Food Market'] = session.query(dal.Bill).filter(dal.Bill.payee=='Food Market').first()

        self.assertEqual(bills['Food Market'].payee, 'Food Market')
        self.assertEqual(bills['Food Market'].amount, Decimal('123.94'))
        self.assertEqual(bills['Food Market'].dueDate, self.today)
        self.assertEqual(bills['Food Market'].alarmDate, None)
        self.assertEqual(bills['Food Market'].notes, None)
        self.assertFalse(bills['Food Market'].paid)
        self.assertEqual(bills['Food Market'].repeats, None)
        self.assertEqual(bills['Food Market'].category.id, 1)

        session.close()
