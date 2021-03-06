# -*- coding: utf-8 -*-

__all__ = ['Daemon', 'Program', 'lock', 'unlock']

import os
import sys
from subprocess import Popen

try:
    import gobject
except ImportError:
    print 'Required package: pygobject'
    raise SystemExit
try:
    import dbus
except ImportError:
    print 'Required package: dbus-python'
    raise SystemExit

from lib import common
from lib import i18n
from lib.utils import verify_pid
from lib.actions import Actions
from alarm import Alarm
from dbus_manager import Server
from dbus_manager import verify_service
from device import *

stdout_orig = sys.stdout
stderr_orig = sys.stderr

LOCKFD = None

def lock():
    """ Verify/Create Lock File """
    global LOCKFD

    try:
        LOCKFD = os.open(common.DAEMON_LOCK_FILE,
                         os.O_CREAT | os.O_EXCL | os.O_RDWR)
        os.write(LOCKFD, '%d' % os.getpid())
        return True
    except OSError:
        # Already locked
        return False

def unlock():
    """ Remove Lock File """
    global LOCKFD

    if not LOCKFD:
        return False
    try:
        os.close(LOCKFD)
        os.remove(common.DAEMON_LOCK_FILE)
        return True
    except OSError:
        return False


class Daemon(object):
    """ Make the program run like a daemon """
    def __init__(self, options):
        """ Detach process and run it as a daemon """
        if options.app_verbose:
            sys.stdout.write('\n')
            sys.stdout = VerboseDevice(type_='stdout')
            sys.stderr = VerboseDevice(type_='stderr')
        else:
            sys.stdout = LogDevice(type_='stdout')
            sys.stderr = LogDevice(type_='stderr')


class Program(Daemon):
    """ BillReminder Daemon Main class """

    def __init__(self, options):

        # Verify if Lock File exist and if there is another instance running
        if not lock():
            lockfd = open(common.DAEMON_LOCK_FILE, 'r')
            lockpid = int(lockfd.readline())
            lockfd.close()
            if verify_pid(lockpid):
                print _('Lock File found:' \
                        ' You have another instance running. (pid=%d)') % \
                        lockpid
                raise SystemExit
            else:
                print _('Lock File found: ' \
                        'Possibly the program was exited unexpectedly.')
                try:
                    print _('Removing Lock File...')
                    os.remove(common.DAEMON_LOCK_FILE)
                    print _('Successfully.')
                except OSError:
                    print _('Failed.')

        # Verify if there is another Billreminder-Daemon DBus Service
        if verify_service(common.DBUS_INTERFACE):
            print _('BillReminder Notifier is already running.')
            raise SystemExit

        Daemon.__init__(self, options)

        self.client_pid = None

        self.actions = Actions()
        self.dbus_server = Server(self)
        if options.app_opengui:
            gui = Popen('billreminder', shell=True)
            self.client_pid = gui.pid
        self.alarm = Alarm(self)


        # Create the mainloop
        self.mainloop = gobject.MainLoop()
        self.mainloop.run()

    def __del__(self):
        try:
            unlock()
        except:
            pass

    def quit(self):
        """ Close program """
        self.mainloop.quit()
        unlock()

def main(options):
    gobject.threads_init()

    try:
        Program(options)
    except KeyboardInterrupt:
        unlock()
        print >> stdout_orig, 'Keyboard Interrupt (Ctrl+C)'
    except:
        unlock()
        raise SystemExit
