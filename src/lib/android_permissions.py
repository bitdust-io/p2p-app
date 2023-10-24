from kivy.utils import platform

if platform == 'android':
    from kivy.clock import Clock
    from android.permissions import request_permissions, check_permission, Permission  # @UnresolvedImport

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class AndroidPermissions:

    def __init__(self, callback=None, permissions=None):
        self.permission_dialog_count = 0
        self.callback = callback
        if platform == 'android':
            #################################################
            # Customize run time permissions for the app here
            #################################################
            self.permissions = permissions or [
                Permission.POST_NOTIFICATIONS,
                Permission.READ_MEDIA_AUDIO,
                Permission.READ_MEDIA_IMAGES,
                Permission.READ_MEDIA_VIDEO,
            ]
            self.permission_status([],[])
        elif self.callback:
            self.callback(True)

    def permission_status(self, permissions, grants):
        if _Debug:
            print('AndroidPermissions.permission_status', permissions, grants)
        granted = True
        for p in self.permissions:
            one_perm = check_permission(p)
            granted = granted and one_perm
            if not one_perm:
                if _Debug:
                    print('AndroidPermissions.permission_status permission was not granted', one_perm)
        if granted:
            if self.callback:
                if _Debug:
                    print('AndroidPermissions.permission_status SUCCESS', self.callback)
                self.callback(granted)
        elif self.permission_dialog_count < 2:
            Clock.schedule_once(self.permission_dialog)  
        else:
            if self.callback:
                if _Debug:
                    print('AndroidPermissions.permission_status NOT GRANTED', self.callback)
                self.callback(granted)
        
    def permission_dialog(self, dt):
        self.permission_dialog_count += 1
        request_permissions(self.permissions, self.permission_status)