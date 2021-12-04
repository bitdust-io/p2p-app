package org.bitdust_io.bitdust1;

import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.net.URL;
import java.net.URLEncoder;
import java.net.HttpURLConnection;

import android.os.Process;
import android.os.AsyncTask;
import android.util.Log;

import org.kivy.android.PythonService;
import org.kivy.android.PythonUtil;

import org.renpy.android.Hardware;


public class BitDustService extends PythonService {

    private static final String TAG = "BitDustService";

    private boolean serviceStartAsForeground;

    @Override
    public void onDestroy() {
        Log.v(TAG, "onDestroy()");
        String process_stop_result = "";
        process_stop_result = requestGetURL("http://localhost:8180/process/stop/v1");
        Log.v(TAG, "onDestroy() process_stop_result first call from the Service : " + process_stop_result);
        int attempts = 0;
        while ((process_stop_result.indexOf("Failed to connect") < 0) && (process_stop_result.indexOf("Connection refused") < 0)) {
            process_stop_result = requestGetURL("http://localhost:8180/process/stop/v1");
            Log.v(TAG, "onDestroy() process_stop_result retry from the Service: " + process_stop_result);
            attempts++;
            if (attempts > 50) break;
        }
        Log.v(TAG, "onDestroy()   about to call super onDestroy");
        super.onDestroy();
        Log.v(TAG, "onDestroy()   is finishing");
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

}
