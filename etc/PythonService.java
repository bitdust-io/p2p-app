package org.kivy.android;

import android.os.AsyncTask;
import android.os.Build;
import java.lang.reflect.Method;
import java.lang.reflect.InvocationTargetException;
import android.app.Service;
import android.os.IBinder;
import android.os.Bundle;
import android.content.Intent;
import android.content.Context;
import android.util.Log;
import android.app.Notification;
import android.app.PendingIntent;
import android.os.Process;
import java.io.File;
import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.net.URL;
import java.net.URLEncoder;
import java.net.HttpURLConnection;

import org.kivy.android.PythonUtil;

import org.renpy.android.Hardware;

//imports for channel definition
import android.app.NotificationManager;
import android.app.NotificationChannel;
import android.graphics.Color;

public class PythonService extends Service implements Runnable {

    private static final String TAG = "PythonService";

    // Thread for Python code
    private Thread pythonThread = null;

    // Python environment variables
    private String androidPrivate;
    private String androidArgument;
    private String pythonName;
    private String pythonHome;
    private String pythonPath;
    private String serviceEntrypoint;
    private boolean serviceStartAsForeground;
    // Argument to pass to Python code,
    private String pythonServiceArgument;


    public static PythonService mService = null;
    private Intent startIntent = null;

    private boolean autoRestartService = false;

    public void setAutoRestartService(boolean restart) {
        Log.v(TAG, "setAutoRestartService() " + restart);
        autoRestartService = restart;
    }

    public int startType() {
        return START_NOT_STICKY;
    }

    @Override
    public IBinder onBind(Intent arg0) {
        if (arg0 != null) {
            String action = arg0.getAction();
            Log.v(TAG, "onBind() action is : " + action);
        } else {
            Log.v(TAG, "onBind() intent is NULL!!!");
        }
        return null;
    }

    @Override
    public void onCreate() {
        Log.v(TAG, "onCreate()");
        super.onCreate();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.v(TAG, "onStartCommand()");
        if (intent != null) {
            String action = intent.getAction();
            Log.v(TAG, "onStartCommand() action is : " + action);
        } else {
            Log.v(TAG, "onStartCommand() intent is NULL!!!");
        }
        if (pythonThread != null) {
            Log.v(TAG, "service exists, do not start again");
            return START_NOT_STICKY;
        }
		startIntent = intent;
        Bundle extras = intent.getExtras();
        androidPrivate = extras.getString("androidPrivate");
        androidArgument = extras.getString("androidArgument");
        serviceEntrypoint = extras.getString("serviceEntrypoint");
        pythonName = extras.getString("pythonName");
        pythonHome = extras.getString("pythonHome");
        pythonPath = extras.getString("pythonPath");
        serviceStartAsForeground = (
            extras.getString("serviceStartAsForeground") == "true"
        );
        pythonServiceArgument = extras.getString("pythonServiceArgument");
        pythonThread = new Thread(this);
        pythonThread.start();

        if (serviceStartAsForeground) {
            doStartForeground(extras);
        }

        return startType();
    }

    protected int getServiceId() {
        return 1;
    }

    protected void doStartForeground(Bundle extras) {
        Log.v(TAG, "doStartForeground()");
        String serviceTitle = extras.getString("serviceTitle");
        String serviceDescription = extras.getString("serviceDescription");
        Notification notification;
        Context context = getApplicationContext();
        Intent contextIntent = new Intent(context, PythonActivity.class);
        PendingIntent pIntent = PendingIntent.getActivity(context, 0, contextIntent,
            PendingIntent.FLAG_UPDATE_CURRENT);

        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            notification = new Notification(
                context.getApplicationInfo().icon, serviceTitle, System.currentTimeMillis());
            try {
                // prevent using NotificationCompat, this saves 100kb on apk
                Method func = notification.getClass().getMethod(
                    "setLatestEventInfo", Context.class, CharSequence.class,
                    CharSequence.class, PendingIntent.class);
                func.invoke(notification, context, serviceTitle, serviceDescription, pIntent);
            } catch (NoSuchMethodException | IllegalAccessException |
                     IllegalArgumentException | InvocationTargetException e) {
            }
        } else {
            // for android 8+ we need to create our own channel
            // https://stackoverflow.com/questions/47531742/startforeground-fail-after-upgrade-to-android-8-1
            String NOTIFICATION_CHANNEL_ID = "org.kivy.p4a";    //TODO: make this configurable
            String channelName = "Background Service";                //TODO: make this configurable
            NotificationChannel chan = new NotificationChannel(NOTIFICATION_CHANNEL_ID, channelName, 
                NotificationManager.IMPORTANCE_NONE);
            
            chan.setLightColor(Color.BLUE);
            chan.setLockscreenVisibility(Notification.VISIBILITY_PRIVATE);
            NotificationManager manager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            manager.createNotificationChannel(chan);

            Notification.Builder builder = new Notification.Builder(context, NOTIFICATION_CHANNEL_ID);
            builder.setContentTitle(serviceTitle);
            builder.setContentText(serviceDescription);
            builder.setContentIntent(pIntent);
            builder.setSmallIcon(context.getApplicationInfo().icon);
            notification = builder.build();
        }
        startForeground(getServiceId(), notification);
    }

    @Override
    public void onDestroy() {
        Log.v(TAG, "onDestroy()");
        String process_stop_result = requestGetURL("http://localhost:8180/process/stop/v1");
        Log.v(TAG, "onDestroy() process_stop_result : " + process_stop_result);
        String process_health_result = "ok";
        while (process_health_result != "") {
            process_health_result = requestGetURL("http://localhost:8180/process/health/v1");
            Log.v(TAG, "onDestroy() process_health_result : " + process_health_result);
        }
        try {
            super.onDestroy();
            Log.v(TAG, "onDestroy() super onDestroy finished");
        } catch (Exception exc) {
            Log.e(TAG, "onDestroy() super onDestroy failed : " + exc);
        }
        pythonThread = null;
        if (autoRestartService && startIntent != null) {
            Log.v(TAG, "service restart requested");
            startService(startIntent);
        }
        Log.v(TAG, "onDestroy() going to kill process " + Process.myPid());
        Process.killProcess(Process.myPid());
        Log.v(TAG, "onDestroy() process finished correctly");
    }

    /**
     * Stops the task gracefully when killed.
     * Calling stopSelf() will trigger a onDestroy() call from the system.
     */
    @Override
    public void onTaskRemoved(Intent rootIntent) {
        Log.v(TAG, "onTaskRemoved()");
        super.onTaskRemoved(rootIntent);
        stopSelf();
    }

    @Override
    public void run(){
        Log.v(TAG, "run()");
        String app_root =  getFilesDir().getAbsolutePath() + "/app";
        File app_root_file = new File(app_root);
        PythonUtil.loadLibraries(app_root_file,
            new File(getApplicationInfo().nativeLibraryDir));
        this.mService = this;
        Log.v(TAG, "run() is about to call to nativeStart()");
        nativeStart(
            androidPrivate, androidArgument,
            serviceEntrypoint, pythonName,
            pythonHome, pythonPath,
            pythonServiceArgument);
        Log.v(TAG, "run() is finished");
        stopSelf();
    }

    // Native part
    public static native void nativeStart(
            String androidPrivate, String androidArgument,
            String serviceEntrypoint, String pythonName,
            String pythonHome, String pythonPath,
            String pythonServiceArgument);



    private class HttpRequestGET extends AsyncTask<String, Void, String> {
        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            Log.v(TAG, "HttpRequestGET.onPreExecute()");
        }

        @Override
        protected String doInBackground(String... urls) {
            Log.v(TAG, "HttpRequestGET.doInBackground() " + urls[0]);
            String result = "";
            try {
                URL url = new URL(urls[0]);
                HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
                urlConnection.setRequestMethod("GET");
                urlConnection.setUseCaches(false);
                urlConnection.setAllowUserInteraction(false);
                urlConnection.setConnectTimeout(300);
                urlConnection.setReadTimeout(300);
                urlConnection.setRequestProperty("Content-Type", "application/json; utf-8");
                urlConnection.setRequestProperty("Content-length", "0");
                urlConnection.setRequestProperty("Accept", "application/json");
                urlConnection.connect();
                try {
                    int responseCode = urlConnection.getResponseCode();
                    if (responseCode == HttpURLConnection.HTTP_OK) {
                        BufferedReader br = new BufferedReader(new InputStreamReader(urlConnection.getInputStream(), "utf-8"));
                        StringBuilder sb = new StringBuilder();
                        String line;
                        while ((line = br.readLine()) != null) {
                            sb.append(line + "\n");
                        }
                        br.close();
                        result = sb.toString();
                    }
                } catch (Exception exc) {
                    Log.e(TAG, "HttpRequestGET.doInBackground() FAILED reading: " + exc);
                }
                urlConnection.disconnect();
            }
            catch (Exception exc) {
                Log.e(TAG, "HttpRequestGET.doInBackground() FAILED connecting: " + exc);
            }
            return result;
        }

        @Override
        protected void onPostExecute(String result) {
            Log.v(TAG, "HttpRequestGET.onPostExecute() OK");
        }
    }

    public String requestGetURL(String url_str) {
        Log.v(TAG, "requestGetURL() " + url_str);
        String str_result = "";
        try {
            str_result = new HttpRequestGET().execute(url_str).get();
        } catch (Exception exc) {
            Log.e(TAG, "requestGetURL() FAILED : " + exc);
        }
        Log.v(TAG, "requestGetURL() result : " + str_result);
        return str_result;
    }

}
