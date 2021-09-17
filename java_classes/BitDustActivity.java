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

    public static BitDustActivity mActivity = null;
    public static BitDustActivity mCustomActivity = null;

    public static int status_bar_height = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        this.mActivity = this;
        this.mCustomActivity = this;
        Log.v(TAG, "onCreate() overwrote mActivity " + this.mActivity);
    }

    @Override
    protected void onDestroy() {
        Log.v(TAG, "onDestroy()");
        String process_stop_result = "";
        process_stop_result = requestGetURL("http://localhost:8180/process/stop/v1");
        Log.v(TAG, "onDestroy() process_stop_result first call from the Activity : " + process_stop_result);
        while (process_stop_result.indexOf("Failed to connect") < 0) {
            process_stop_result = requestGetURL("http://localhost:8180/process/stop/v1");
            Log.v(TAG, "onDestroy() process_stop_result retry from the Activity : " + process_stop_result);
        }
        Log.v(TAG, "onDestroy()   about to call super onDestroy");
        super.onDestroy();
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
            HttpURLConnection urlConnection;
            try {
                URL url = new URL(urls[0]);
                urlConnection = (HttpURLConnection) url.openConnection();
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
                try {
                    urlConnection.disconnect();
                } catch (Exception e) {
                    Log.e(TAG, "HttpRequestGET.doInBackground().disconnect : " + e);
                }
            } catch (Exception exc) {
                Log.e(TAG, "HttpRequestGET.doInBackground() FAILED connecting: " + exc);
                result = exc.getMessage();
                try {
                    urlConnection.disconnect();
                } catch (Exception e) {
                    Log.e(TAG, "HttpRequestGET.doInBackground().disconnect : " + e);
                }
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
