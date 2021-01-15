from io import open

import os
import sys
import json

from twisted.internet import reactor
from twisted.internet import endpoints
from twisted.web.server import Site
from twisted.web.static import File

import logging
# logging.basicConfig(level=logging.DEBUG)

# from twisted.internet.defer import setDebugging
# setDebugging(True)

# from twisted.python.log import startLogging
# startLogging(sys.stdout)

from jnius import autoclass  # @UnresolvedImport

import encodings.idna

PACKAGE_NAME = 'org.bitdust_io.bitdust1'

PythonActivity = autoclass('org.bitdust_io.bitdust1.BitDustActivity')


def set_foreground():
    print('set_foreground')
    channel_id = f'{PACKAGE_NAME}.Bitdustnode'
    Context = autoclass(u'android.content.Context')
    Intent = autoclass(u'android.content.Intent')
    PendingIntent = autoclass(u'android.app.PendingIntent')
    AndroidString = autoclass(u'java.lang.String')
    NotificationBuilder = autoclass(u'android.app.Notification$Builder')
    NotificationManager = autoclass(u'android.app.NotificationManager')
    NotificationChannel = autoclass(u'android.app.NotificationChannel')
    notification_channel = NotificationChannel(channel_id, AndroidString('BitDust Channel'.encode('utf-8')), NotificationManager.IMPORTANCE_HIGH)
    Notification = autoclass(u'android.app.Notification')
    # service = autoclass('org.kivy.android.PythonService').mService
    service = autoclass('org.bitdust_io.bitdust1.BitDustService').mService
    notification_service = service.getSystemService(Context.NOTIFICATION_SERVICE)
    notification_service.createNotificationChannel(notification_channel)
    app_context = service.getApplication().getApplicationContext()
    notification_builder = NotificationBuilder(app_context, channel_id)
    title = AndroidString("BitDust".encode('utf-8'))
    message = AndroidString("Application is running in background".encode('utf-8'))
    notification_intent = Intent(app_context, PythonActivity)
    notification_intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_NO_HISTORY)
    notification_intent.setAction(Intent.ACTION_MAIN)
    notification_intent.addCategory(Intent.CATEGORY_LAUNCHER)
    intent = PendingIntent.getActivity(service, 0, notification_intent, 0)
    notification_builder.setContentTitle(title)
    notification_builder.setContentText(message)
    notification_builder.setContentIntent(intent)
    notification_builder.setOngoing(True)
    notification_builder.setPriority(NotificationManager.IMPORTANCE_MIN)
    Drawable = autoclass(u"{}.R$drawable".format(service.getPackageName()))
    icon = getattr(Drawable, 'icon')
    notification_builder.setSmallIcon(icon)
    notification_builder.setAutoCancel(True)
    notification_builder.setCategory(Notification.CATEGORY_SERVICE)
    new_notification = notification_builder.getNotification()
    service.startForeground(1, new_notification)
    print('set_foreground DONE : %r' % service)


def start_bitdust():
    executable_path = os.getcwd()
    print('start_bitdust executable_path=%r' % executable_path)
    try:
        os.chdir('bitdust')
    except:
        pass
    print('executable_path after : %r' % os.getcwd())
    from main.bpmain import main
    # reactor.callLater(0, main, executable_path, start_reactor=False)  # @UndefinedVariable
    main(executable_path, start_reactor=False)
    return True


def stop_bitdust():
    executable_path = os.getcwd()
    print('stop_bitdust executable_path=%r' % executable_path)
    try:
        os.chdir('bitdust')
    except:
        pass
    print('executable_path after : %r' % os.getcwd())
    from main import shutdowner
    # reactor.callLater(0, shutdowner.A, 'stop', 'exit')  # @UndefinedVariable
    shutdowner.A('stop', 'exit')
    return True


def start_web_server(web_port_number=8888):
    """
    Not in use.
    """
    resource = File(f'/data/user/0/{PACKAGE_NAME}/files/app/www/')
    factory = Site(resource)
    endpoint = endpoints.TCP4ServerEndpoint(reactor, web_port_number)
    endpoint.listen(factory)
    # fout = open(SERVICE_STARTED_MARKER_FILENAME, 'w')
    # fout.write('localhost %d' % web_port_number)
    # fout.flush()
    # os.fsync(fout.fileno())
    # fout.close()
    # print('start_web_server file written', SERVICE_STARTED_MARKER_FILENAME)
    return endpoint


def run_service():
    print('run_service()')
    argument = os.environ.get('PYTHON_SERVICE_ARGUMENT', 'null')
    argument = json.loads(argument) if argument else None
    argument = {} if argument is None else argument
    print('run_service() argument : %r' % argument)

    if argument.get('stop_service'):
        print('run_service() service to be stopped now')
        stop_bitdust()
        return

    try:
        set_foreground()

        # reactor.callWhenRunning(start_web_server)  # @UndefinedVariable
        reactor.callWhenRunning(start_bitdust)  # @UndefinedVariable
        reactor.run(installSignalHandlers=False)  # @UndefinedVariable

        print('run_service() Twisted reactor stopped')

        # if os.path.isfile(SERVICE_STARTED_MARKER_FILENAME):
        #     os.remove(SERVICE_STARTED_MARKER_FILENAME)
        #     print('run_service() file erased:', SERVICE_STARTED_MARKER_FILENAME)

    except Exception as exc:
        print('Exception in run_service() : %r' % exc)


if __name__ == '__main__':
    run_service()
    print('EXIT')
