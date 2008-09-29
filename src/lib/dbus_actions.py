# -*- coding: utf-8 -*-

__all__ = ['Actions']

import dbus
import dbus.service
import os
from subprocess import Popen

import dal
import bill
from lib import common, scheduler
from lib.utils import force_string
from lib.utils import Message
from db.billstable import BillsTable

class Actions(object):

    def __init__(self, databaselayer=None):
        try:
            session_bus = dbus.SessionBus()
            obj = session_bus.get_object(common.DBUS_INTERFACE,
                                         common.DBUS_PATH)
            self.dbus_interface = dbus.Interface(obj, common.DBUS_INTERFACE)
            pid = os.getpid()
            print self.dbus_interface.register(pid)
        except dbus.DBusException:
            if Message().ShowErrorQuestion( \
              _("An error occurred while connecting to BillReminder Notifier!\n"\
                "Do you want to launch it and restart BillReminder?")):
                Popen('python billreminderd --open-gui', shell=True)
                raise SystemExit
            return False

    def _correct_type(self, record):
        if not isinstance(record, dict):
            return record

        if 'Id' in record.keys():
            record['Id'] = int(record['Id'])
        if 'dueDate' in record.keys():
            record['dueDate'] = int(record['dueDate'])
        if 'amountDue' in record.keys():
            record['amountDue'] = float(record['amountDue'].replace(',', '.'))
        if 'paid' in record.keys():
            record['paid'] = int(record['paid'])
        if 'alarm' in record.keys():
            record['alarm'] = int(record['alarm'])
        if 'catId' in record.keys():
            record['catId'] = int(record['catId'])
        return record

    def get_monthly_totals(self, status, month, year):
        # Return a list of categories and totals for the given month
        #try:
        ret = []
        records = self.dbus_interface.get_monthly_totals(status, month, year)
        for record in records:
            record = self._correct_type(record)
            ret.append(record)
        return ret
        #except dbus.DBusException:
        #    if self.__init__():
        #        return self.get_monthly_totals(status, month, year)


    def get_monthly_bills(self, status, month, year):
        #try:
        ret = []
        records = self.dbus_interface.get_monthly_bills(status, month, year)
        for record in records:
            record = self._correct_type(record)
            ret.append(record)
        return ret
        #except dbus.DBusException:
        #    if self.__init__():
        #        return self.get_monthly_bills(status, month, year)

    def get_interval_totals(self, status, start, end):
        # Return a list of categories and totals for the given month
        #try:
        ret = []
        records = self.dbus_interface.get_interval_totals(status, start, end)
        for record in records:
            record = self._correct_type(record)
            ret.append(record)
        return ret
        #except dbus.DBusException:
        #    if self.__init__():
        #        return self.get_interval_totals(status, start, end)


    def get_interval_bills(self, status, start, end):
        #try:
        ret = []
        records = self.dbus_interface.get_interval_bills(status, start, end)
        for record in records:
            record = self._correct_type(record)
            ret.append(record)
        return ret
        #except dbus.DBusException:
        #    if self.__init__():
        #        return self.get_monthly_bills(status, start, end)

        
    def get_bills(self, kwargs):
        """ Returns one or more records that meet the criteria passed """
        try:
            ret = []
            if isinstance(kwargs, basestring):
                records = self.dbus_interface.get_bills_(kwargs)
            else:
                records = self.dbus_interface.get_bills(force_string(kwargs))
            for record in records:
                record = self._correct_type(record)
                ret.append(record)
            return ret
        except dbus.DBusException:
            if self.__init__():
                return self.get_bills(kwargs)

    def add_bill(self, kwargs):
        """ Adds a bill to the database """
        try:
            record = self.dbus_interface.add_bill(force_string(kwargs))
            return self._correct_type(record)
        except dbus.DBusException:
            if self.__init__():
                return self.add_bill(kwargs)

    def edit_bill(self, kwargs):
        """ Edit a record in the database """
        try:
            record = self.dbus_interface.edit_bill(force_string(kwargs))
            return self._correct_type(record)
        except dbus.DBusException:
            if self.__init__():
                return self.edit_bill(kwargs)

    def delete_bill(self, key):
        """ Delete a record in the database """
        try:
            return self.dbus_interface.delete_bill(key)
        except dbus.DBusException:
            if self.__init__():
                return self.delete_bill(kwargs)

    def get_categories(self, kwargs):
        """ Returns one or more records that meet the criteria passed """
        try:
            ret = []
            if isinstance(kwargs, basestring):
                records = self.dbus_interface.get_categories_(kwargs)
            else:
                records = self.dbus_interface.get_categories(force_string(kwargs))
            for record in records:
                record = self._correct_type(record)
                ret.append(record)
            return ret
        except dbus.DBusException:
            if self.__init__():
                return self.get_categories(kwargs)

    def add_category(self, kwargs):
        """ Adds a category to the database """
        try:
            record = self.dbus_interface.add_category(force_string(kwargs))
            return self._correct_type(record)
        except dbus.DBusException:
            if self.__init__():
                return self.add_category(kwargs)

    def edit_category(self, kwargs):
        """ Edit a record in the database """
        try:
            record = self.dbus_interface.edit_category(force_string(kwargs))
            return self._correct_type(record)
        except dbus.DBusException:
            if self.__init__():
                return self.edit_category(kwargs)

    def delete_category(self, key):
        """ Delete a record in the database """
        try:
            return self.dbus_interface.delete_category(key)
        except dbus.DBusException:
            if self.__init__():
                return self.delete_category(kwargs)
