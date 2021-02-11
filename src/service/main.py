import os
import sys
import json

from twisted.internet import reactor

from jnius import autoclass  # @UnresolvedImport

import encodings.idna

#------------------------------------------------------------------------------

PACKAGE_NAME = 'org.bitdust_io.bitdust1'
SERVICE_NAME = 'org.bitdust_io.bitdust1.BitDustService'

PythonActivity = autoclass('org.bitdust_io.bitdust1.BitDustActivity')

#------------------------------------------------------------------------------ 

_Debug = True

#------------------------------------------------------------------------------

if _Debug:
    # logging.basicConfig(level=logging.DEBUG)
    from twisted.internet.defer import setDebugging
    setDebugging(True)
    from twisted.python.log import startLogging
    startLogging(sys.stdout)

#------------------------------------------------------------------------------

if _Debug:
    print('BitDustService __file__', os.path.dirname(os.path.abspath(__file__)))
    print('BitDustService os.getcwd', os.path.abspath(os.getcwd()))
    print('BitDustService sys.path', sys.path)
    print('BitDustService os.listdir', os.listdir(os.getcwd()))

#------------------------------------------------------------------------------

def set_foreground():
    channel_id = f'{PACKAGE_NAME}.Bitdustnode'
    Context = autoclass(u'android.content.Context')
    Intent = autoclass(u'android.content.Intent')
    PendingIntent = autoclass(u'android.app.PendingIntent')
    AndroidString = autoclass(u'java.lang.String')
    NotificationBuilder = autoclass(u'android.app.Notification$Builder')
    NotificationManager = autoclass(u'android.app.NotificationManager')
    NotificationChannel = autoclass(u'android.app.NotificationChannel')

    notification_channel = NotificationChannel(channel_id, AndroidString('BitDust Channel'.encode('utf-8')), NotificationManager.IMPORTANCE_LOW)

    Notification = autoclass(u'android.app.Notification')
    service = autoclass(SERVICE_NAME).mService
    notification_service = service.getSystemService(Context.NOTIFICATION_SERVICE)

    notification_service.createNotificationChannel(notification_channel)

    app_context = service.getApplication().getApplicationContext()
    notification_builder = NotificationBuilder(app_context, channel_id)

    title = AndroidString("BitDust".encode('utf-8'))
    message = AndroidString("Application is running in background".encode('utf-8'))

    notification_intent = Intent(app_context, PythonActivity)
    notification_intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_NEW_TASK)
    notification_intent.setAction(Intent.ACTION_MAIN)
    notification_intent.addCategory(Intent.CATEGORY_LAUNCHER)

    intent = PendingIntent.getActivity(service, 0, notification_intent, 0)
    notification_builder.setContentTitle(title)
    notification_builder.setContentText(message)
    notification_builder.setContentIntent(intent)
    notification_builder.setOngoing(True)
    notification_builder.setPriority(NotificationManager.IMPORTANCE_MIN)

    Drawable = autoclass(u"{}.R$drawable".format(service.getPackageName()))
    notification_builder.setSmallIcon(getattr(Drawable, 'icon'))
    notification_builder.setAutoCancel(True)
    notification_builder.setCategory(Notification.CATEGORY_SERVICE)

    new_notification = notification_builder.getNotification()
    service.startForeground(1, new_notification)
    if _Debug:
        print('BitDustService.set_foreground() : %r' % service)


def set_foreground_api_lower_26():
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    AndroidString = autoclass('java.lang.String')
    NotificationBuilder = autoclass('android.app.Notification$Builder')

    Notification = autoclass('android.app.Notification')
    service = autoclass(SERVICE_NAME).mService

    app_context = service.getApplication().getApplicationContext()
    notification_builder = NotificationBuilder(app_context)

    title = AndroidString("BitDust".encode('utf-8'))
    message = AndroidString("Application is running in background".encode('utf-8'))

    notification_intent = Intent(app_context, PythonActivity)
    notification_intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_NEW_TASK)
    notification_intent.setAction(Intent.ACTION_MAIN)
    notification_intent.addCategory(Intent.CATEGORY_LAUNCHER)

    intent = PendingIntent.getActivity(service, 0, notification_intent, 0)
    notification_builder.setContentTitle(title)
    notification_builder.setContentText(message)
    notification_builder.setContentIntent(intent)
    notification_builder.setOngoing(True)

    Drawable = autoclass("{}.R$drawable".format(service.getPackageName()))
    notification_builder.setSmallIcon(getattr(Drawable, 'icon'))
    notification_builder.setAutoCancel(True)
    notification_builder.setCategory(Notification.CATEGORY_SERVICE)

    service.startForeground(1, notification_builder.getNotification())
    if _Debug:
        print('BitDustService.set_foreground_api_lower_26() : %r' % service)

#------------------------------------------------------------------------------

def start_bitdust():
    executable_path = os.getcwd()
    if _Debug:
        print('BitDustService.start_bitdust() executable_path=%r' % executable_path)
    try:
        os.chdir('bitdust')
    except Exception as exc:
        if _Debug:
            print('BitDustService.start_bitdust() error changing current path to "bitdust" sub-folder:', exc)
    if _Debug:
        print('BitDustService.start_bitdust() executing the entry point     os.getcwd() : %r' % os.getcwd())
    from main.bpmain import main
    main(executable_path, start_reactor=False)
    if _Debug:
        print('BitDustService.start_bitdust() OK!')
    return True


def stop_bitdust():
    executable_path = os.getcwd()
    if _Debug:
        print('BitDustService.stop_bitdust() executable_path=%r' % executable_path)
    try:
        os.chdir('bitdust')
    except:
        pass
    if _Debug:
        print('BitDustService.stop_bitdust() executable_path after : %r' % os.getcwd())
    from main import shutdowner
    shutdowner.A('stop', 'exit')
    return True

#------------------------------------------------------------------------------

def run_service():
    argument = os.environ.get('PYTHON_SERVICE_ARGUMENT', 'null')
    argument = json.loads(argument) if argument else None
    argument = {} if argument is None else argument
    if _Debug:
        print('BitDustService.run_service() argument : %r' % argument)

    if argument.get('stop_service'):
        if _Debug:
            print('BitDustService.run_service() service to be stopped now')
        stop_bitdust()
        return

    try:
        from lib.system import android_sdk_version

        if android_sdk_version() < 26:
            set_foreground_api_lower_26()
        else:
            set_foreground()

        reactor.callWhenRunning(start_bitdust)  # @UndefinedVariable
        reactor.run(installSignalHandlers=False)  # @UndefinedVariable

        if _Debug:
            print('BitDustService.run_service() Twisted reactor stopped')

    except Exception as exc:
        if _Debug:
            print('BitDustService.run_service()  Exception : %r' % exc)

#------------------------------------------------------------------------------

def main():
    if _Debug:
        print('BitDustService.main() process is starting')
    run_service()
    if _Debug:
        print('BitDustService.main() process is finishing')

#------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
