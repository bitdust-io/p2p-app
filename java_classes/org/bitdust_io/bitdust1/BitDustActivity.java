package org.bitdust_io.bitdust1;

import java.io.BufferedReader;
import java.io.BufferedInputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.File;
import java.io.OutputStream;
import java.io.IOException;
import java.io.UnsupportedEncodingException;

import java.lang.reflect.InvocationTargetException;
import java.lang.UnsatisfiedLinkError;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;
import java.net.URL;
import java.net.URLEncoder;
import java.net.HttpURLConnection;
import java.net.SocketException;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.content.pm.PackageManager;
import android.content.pm.ApplicationInfo;
import android.provider.MediaStore;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.Manifest;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Build;
import android.os.PowerManager;
import android.os.Process;
import android.util.Log;
import android.util.DisplayMetrics;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.view.ViewGroup;
import android.view.ViewGroup.LayoutParams;
import android.view.Window;
import android.view.WindowManager;
import android.widget.ImageView;
import android.widget.Toast;

import android.webkit.ConsoleMessage;
import android.webkit.ValueCallback;

import org.libsdl.app.SDL;
import org.libsdl.app.SDLActivity;

import org.kivy.android.PythonActivity;
import org.kivy.android.PythonUtil;
import org.kivy.android.launcher.Project;

import org.renpy.android.ResourceManager;
import org.renpy.android.AssetExtract;


public class BitDustActivity extends PythonActivity {

    private static final String TAG = "BitDustActivity";

    public static BitDustActivity mBitDustActivity = null;

    public static int status_bar_height = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        this.mBitDustActivity = this;
        Log.v(TAG, "onCreate()");
    }

    @Override
    protected void onStop() {
        Log.v(TAG, "onStop()   about to call super onStop");
        super.onStop();
        Log.v(TAG, "onStop()  super onStop finished");
    }

    @Override
    protected void onDestroy() {
        Log.v(TAG, "onDestroy() going to call /process/stop/v1 API");
        String process_stop_result = "";
        process_stop_result = requestGetURL("http://localhost:8180/process/stop/v1");
        Log.v(TAG, "onDestroy() process_stop_result first call from the Activity : " + process_stop_result);
        int attempts = 0;
        while ((process_stop_result.indexOf("Failed to connect") < 0) && (process_stop_result.indexOf("Connection refused") < 0)) {
            process_stop_result = requestGetURL("http://localhost:8180/process/stop/v1");
            Log.v(TAG, "onDestroy() process_stop_result retry from the Activity : " + process_stop_result);
            attempts++;
            if (attempts > 5) break;
        }
        Log.v(TAG, "onDestroy() going to kill the process: " + Process.myPid());
        Process.killProcess(Process.myPid());
        Log.v(TAG, "onDestroy()   about to call super onDestroy");
        super.onDestroy();
        Log.v(TAG, "onDestroy()  is finishing");
    }

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
                urlConnection.setConnectTimeout(50);
                urlConnection.setReadTimeout(50);
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
                } catch (java.net.SocketException exc) {
                    Log.e(TAG, "HttpRequestGET.doInBackground() FAILED SocketException: " + exc.getMessage());
                    result = exc.getMessage();
                    try {
                        urlConnection.disconnect();
                    } catch (Exception e) {
                        Log.e(TAG, "HttpRequestGET.doInBackground().disconnect : " + e);
                    }
                } catch (Exception exc) {
                    Log.e(TAG, "HttpRequestGET.doInBackground() FAILED reading: " + exc);
                    result = exc.getMessage();
                    try {
                        urlConnection.disconnect();
                    } catch (Exception e) {
                        Log.e(TAG, "HttpRequestGET.doInBackground().disconnect : " + e);
                    }
                }
                try {
                    urlConnection.disconnect();
                } catch (Exception e) {
                    Log.e(TAG, "HttpRequestGET.doInBackground().disconnect : " + e);
                }
            } catch (java.net.SocketException exc) {
                Log.e(TAG, "HttpRequestGET.doInBackground() FAILED SocketException: " + exc.getMessage());
                result = exc.getMessage();
            } catch (Exception exc) {
                Log.e(TAG, "HttpRequestGET.doInBackground() FAILED connecting: " + exc);
                result = exc.getMessage();
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


    public interface CustomPermissionsCallback {
        void onRequestCustomPermissionsResult(int requestCode, String[] permissions, int[] grantResults);
    }

    private CustomPermissionsCallback permissionCallbackCustom;
    private boolean haveCustomPermissionsCallback = false;

    public void addCustomPermissionsCallback(CustomPermissionsCallback callback) {
        permissionCallbackCustom = callback;
        haveCustomPermissionsCallback = true;
        Log.v(TAG, "addCustomPermissionsCallback(): Added callback for onRequestPermissionsResult");
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        Log.v(TAG, "onRequestPermissionsResult()");
        if (haveCustomPermissionsCallback) {
            Log.v(TAG, "onRequestPermissionsResult passed to callback");
            permissionCallbackCustom.onRequestCustomPermissionsResult(requestCode, permissions, grantResults);
        }
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
    }

    public boolean checkCurrentCustomPermission(String permission) {
        if (android.os.Build.VERSION.SDK_INT < 23)
            return true;

        try {
            java.lang.reflect.Method methodCheckPermission = Activity.class.getMethod("checkSelfPermission", String.class);
            Object resultObj = methodCheckPermission.invoke(this, permission);
            int result = Integer.parseInt(resultObj.toString());
            if (result == PackageManager.PERMISSION_GRANTED)
                return true;
        } catch (IllegalAccessException | NoSuchMethodException | InvocationTargetException e) {
        }
        return false;
    }

    public void requestCustomPermissionsWithRequestCode(String[] permissions, int requestCode) {
        if (android.os.Build.VERSION.SDK_INT < 23)
            return;
        try {
            java.lang.reflect.Method methodRequestPermission = Activity.class.getMethod("requestPermissions", String[].class, int.class);
            methodRequestPermission.invoke(this, permissions, requestCode);
        } catch (IllegalAccessException | NoSuchMethodException | InvocationTargetException e) {
        }
    }

    public void requestCustomPermissions(String[] permissions) {
        requestCustomPermissionsWithRequestCode(permissions, 1);
    }

}
