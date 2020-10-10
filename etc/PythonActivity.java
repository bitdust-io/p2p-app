package org.kivy.android;

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
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import org.libsdl.app.SDL;
import org.libsdl.app.SDLActivity;

import org.kivy.android.PythonUtil;
import org.kivy.android.launcher.Project;

import org.renpy.android.ResourceManager;
import org.renpy.android.AssetExtract;


public class PythonActivity extends SDLActivity {
    private static final String TAG = "PythonActivity";

    public static PythonActivity mActivity = null;

    private ResourceManager resourceManager = null;
    private Bundle mMetaData = null;
    private PowerManager.WakeLock mWakeLock = null;
    private static boolean appliedWindowedModeHack = false;
    private static final int INPUT_FILE_REQUEST_CODE = 10001;
    public WebView webView = null;
    private WebSettings webSettings = null;
    private ValueCallback<Uri[]> mUploadMessage = null;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        Log.v(TAG, "onCreate()");
        Log.v(TAG, "About to do super onCreate");
        super.onCreate(savedInstanceState);
        Log.v(TAG, "Did super onCreate");

        resourceManager = new ResourceManager(this);

        this.mActivity = this;
        this.showLoadingScreen();

        new UnpackFilesTask().execute(getAppRoot());
    }


    public void createWebView() {
        Log.v(TAG, "createWebView()");
        try {
            this.webView = new WebView(this);
            webSettings = this.webView.getSettings();
            webSettings.setJavaScriptEnabled(true);
            webSettings.setUseWideViewPort(true);
            webSettings.setLoadWithOverviewMode(true);
            webSettings.setAllowFileAccess(true);
            webSettings.setAllowContentAccess(true);
            webSettings.setAllowFileAccessFromFileURLs(true);
            webSettings.setAllowUniversalAccessFromFileURLs(true);
            webSettings.setSupportZoom(false);
            webSettings.setBuiltInZoomControls(false);
            webSettings.setAppCacheEnabled(false);
            this.webView.setWebContentsDebuggingEnabled(true);
            this.webView.setWebViewClient(new WebViewClient());
            this.webView.setWebChromeClient(new MyWebChromeClient());
            // this.webView.requestFocus(View.FOCUS_DOWN);
            //if SDK version is greater of 19 then activate hardware acceleration otherwise activate software acceleration
            if (Build.VERSION.SDK_INT >= 19) {
                this.webView.setLayerType(View.LAYER_TYPE_HARDWARE, null);
            } else if (Build.VERSION.SDK_INT >= 11 && Build.VERSION.SDK_INT < 19) {
                this.webView.setLayerType(View.LAYER_TYPE_SOFTWARE, null);
            }
            this.addContentView(this.webView, new LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT));
            Log.v(TAG, "createWebView() ok");
        } catch (Exception exc) {
            Log.e(TAG, "Failed creating WebView: " + exc);
        }
    }

    public String getAppRoot() {
        String app_root =  getFilesDir().getAbsolutePath() + "/app";
        return app_root;
    }

    public String getImagePath(Uri uri) {
        Log.v(TAG, "getImagePath()");
        Cursor cursor = getContentResolver().query(uri, null, null, null, null);
        cursor.moveToFirst();
        String document_id = cursor.getString(0);
        document_id = document_id.substring(document_id.lastIndexOf(":")+1);
        cursor.close();
        cursor = getContentResolver().query(
            android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
            null,
            MediaStore.Images.Media._ID + " = ? ",
            new String[]{document_id},
            null
        );
        cursor.moveToFirst();
        String path = cursor.getString(cursor.getColumnIndex(MediaStore.Images.Media.DATA));
        cursor.close();
        return path;
    }

    protected void parseSelectedFilePath(int resultCode, Intent intent) {
        Log.v(TAG, "parseSelectedFilePath()");
        Uri[] results = null;
        if (resultCode == RESULT_OK && intent != null) {
            Log.v(TAG, "PythonActivity is running parseSelectedFilePath for " + intent.getData());
            results  = new Uri[1];
            try {
                String full_path = getImagePath(intent.getData());
                String encoded_path = URLEncoder.encode(full_path, "UTF-8");
                File fake_file = new File("file:///" + encoded_path);
                results[0] = Uri.fromFile(fake_file);
                Log.v(TAG, "PythonActivity parseSelectedFilePath : " + results[0].toString());
            } catch (UnsupportedEncodingException exc) {
                Log.e(TAG, "PythonActivity parseSelectedFilePath error encoding file path");
            }
        }
        else {
            Log.v(TAG, "PythonActivity is running parseSelectedFilePath return EMPTY LIST: resultCode=" + resultCode + " intent=" + intent);
        }
        mUploadMessage.onReceiveValue(results);
        mUploadMessage = null;
    }

    public class MyWebChromeClient extends WebChromeClient {

        public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> filePath, WebChromeClient.FileChooserParams fileChooserParams) {
            Log.v(TAG, "onShowFileChooser()");
            if (mUploadMessage != null) {
                Log.v(TAG, "PythonActivity mUploadMessage is not empty");
                mUploadMessage.onReceiveValue(null);
            }
            mUploadMessage = filePath;
            Intent contentSelectionIntent = new Intent(Intent.ACTION_GET_CONTENT);
            contentSelectionIntent.addCategory(Intent.CATEGORY_OPENABLE);
            contentSelectionIntent.setType("*/*");
            contentSelectionIntent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, false);
            Intent[] intentArray;
            intentArray = new Intent[0];
            Intent chooserIntent = new Intent(Intent.ACTION_CHOOSER);
            chooserIntent.putExtra(Intent.EXTRA_INTENT, contentSelectionIntent);
            chooserIntent.putExtra(Intent.EXTRA_TITLE, "Select file to upload");
            chooserIntent.putExtra(Intent.EXTRA_INITIAL_INTENTS, intentArray);
            //startActivityForResult(Intent.createChooser(chooserIntent, "Select file"), INPUT_FILE_REQUEST_CODE);
            startActivityForResult(chooserIntent, INPUT_FILE_REQUEST_CODE);
            return true;
        }

        @Override
        public boolean onConsoleMessage(ConsoleMessage consoleMessage) {
            Log.v("WebViewConsole", consoleMessage.message());
            return true;
        }
    }

    public class MyWebViewClient extends WebViewClient {

    }

    public void loadLibraries() {
        Log.v(TAG, "loadLibraries()");
        String app_root = new String(getAppRoot());
        File app_root_file = new File(app_root);
        PythonUtil.loadLibraries(app_root_file,
            new File(getApplicationInfo().nativeLibraryDir));
    }

    public void recursiveDelete(File f) {
        if (f.isDirectory()) {
            for (File r : f.listFiles()) {
                recursiveDelete(r);
            }
        }
        f.delete();
    }

    /**
     * Show an error using a toast. (Only makes sense from non-UI
     * threads.)
     */
    public void toastError(final String msg) {
        Log.v(TAG, "toastError(): " + msg);
        final Activity thisActivity = this;

        runOnUiThread(new Runnable () {
            public void run() {
                Toast.makeText(thisActivity, msg, Toast.LENGTH_LONG).show();
            }
        });

        // Wait to show the error.
        synchronized (this) {
            try {
                this.wait(1000);
            } catch (InterruptedException e) {
            }
        }
    }

    private class UnpackFilesTask extends AsyncTask<String, Void, String> {
        @Override
        protected String doInBackground(String... params) {
            File app_root_file = new File(params[0]);
            Log.v(TAG, "doInBackground(): Ready to unpack");
            unpackData("private", app_root_file);
            return null;
        }

        @Override
        protected void onPostExecute(String result) {
            Log.v(TAG, "onPostExecute() " + result);
            // Figure out the directory where the game is. If the game was
            // given to us via an intent, then we use the scheme-specific
            // part of that intent to determine the file to launch. We
            // also use the android.txt file to determine the orientation.
            //
            // Otherwise, we use the public data, if we have it, or the
            // private data if we do not.
            mActivity.finishLoad();

            // finishLoad called setContentView with the SDL view, which
            // removed the loading screen. However, we still need it to
            // show until the app is ready to render, so pop it back up
            // on top of the SDL view.
            mActivity.showLoadingScreen();

            String app_root_dir = getAppRoot();
            if (getIntent() != null && getIntent().getAction() != null &&
                    getIntent().getAction().equals("org.kivy.LAUNCH")) {
                Log.v(TAG, "onPostExecute() is going to LAUNCH a file " + getIntent().getData().getSchemeSpecificPart());
                File path = new File(getIntent().getData().getSchemeSpecificPart());

                Project p = Project.scanDirectory(path);
                String entry_point = getEntryPoint(p.dir);
                SDLActivity.nativeSetenv("ANDROID_ENTRYPOINT", p.dir + "/" + entry_point);
                SDLActivity.nativeSetenv("ANDROID_ARGUMENT", p.dir);
                SDLActivity.nativeSetenv("ANDROID_APP_PATH", p.dir);
                Log.v(TAG, "onPostExecute() ANDROID_ENTRYPOINT is " + p.dir + "/" + entry_point);
                Log.v(TAG, "onPostExecute() ANDROID_APP_PATH is " + p.dir);

                if (p != null) {
                    if (p.landscape) {
                        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);
                    } else {
                        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
                    }
                }

                // Let old apps know they started.
                try {
                    FileWriter f = new FileWriter(new File(path, ".launch"));
                    f.write("started");
                    f.close();
                } catch (IOException e) {
                    // pass
                }
            } else {
                String entry_point = getEntryPoint(app_root_dir);
                SDLActivity.nativeSetenv("ANDROID_ENTRYPOINT", entry_point);
                SDLActivity.nativeSetenv("ANDROID_ARGUMENT", app_root_dir);
                SDLActivity.nativeSetenv("ANDROID_APP_PATH", app_root_dir);
                Log.v(TAG, "onPostExecute() ANDROID_ENTRYPOINT is " + entry_point);
                Log.v(TAG, "onPostExecute() ANDROID_APP_PATH is " + app_root_dir);
            }

            String mFilesDirectory = mActivity.getFilesDir().getAbsolutePath();
            Log.v(TAG, "Setting env vars for start.c and Python to use");
            SDLActivity.nativeSetenv("ANDROID_PRIVATE", mFilesDirectory);
            SDLActivity.nativeSetenv("ANDROID_UNPACK", app_root_dir);
            SDLActivity.nativeSetenv("PYTHONHOME", app_root_dir);
            SDLActivity.nativeSetenv("PYTHONPATH", app_root_dir + ":" + app_root_dir + "/lib");
            SDLActivity.nativeSetenv("PYTHONOPTIMIZE", "2");

            try {
                Log.v(TAG, "Access to our meta-data...");
                mActivity.mMetaData = mActivity.getPackageManager().getApplicationInfo(
                        mActivity.getPackageName(), PackageManager.GET_META_DATA).metaData;

                PowerManager pm = (PowerManager) mActivity.getSystemService(Context.POWER_SERVICE);
                if ( mActivity.mMetaData.getInt("wakelock") == 1 ) {
                    mActivity.mWakeLock = pm.newWakeLock(PowerManager.SCREEN_BRIGHT_WAKE_LOCK, "Screen On");
                    mActivity.mWakeLock.acquire();
                }
                if ( mActivity.mMetaData.getInt("surface.transparent") != 0 ) {
                    Log.v(TAG, "Surface will be transparent.");
                    getSurface().setZOrderOnTop(true);
                    getSurface().getHolder().setFormat(PixelFormat.TRANSPARENT);
                } else {
                    Log.i(TAG, "Surface will NOT be transparent");
                }
            } catch (PackageManager.NameNotFoundException e) {
            }

            // Launch app if that hasn't been done yet:
            if (mActivity.mHasFocus && (
                    // never went into proper resume state:
                    mActivity.mCurrentNativeState == NativeState.INIT ||
                    (
                    // resumed earlier but wasn't ready yet
                    mActivity.mCurrentNativeState == NativeState.RESUMED &&
                    mActivity.mSDLThread == null
                    ))) {
                // Because sometimes the app will get stuck here and never
                // actually run, ensure that it gets launched if we're active:
                Log.v(TAG, "onPostExecute() going to resume activity");
                mActivity.onResume();
            }
        }

        @Override
        protected void onPreExecute() {
            Log.v(TAG, "onPreExecute()");
        }

        @Override
        protected void onProgressUpdate(Void... values) {
            Log.v(TAG, "onProgressUpdate()");
        }
    }

    public void unpackData(final String resource, File target) {

        Log.v(TAG, "unpackData!!! " + resource + " " + target.getName());

        // The version of data in memory and on disk.
        String data_version = resourceManager.getString(resource + "_version");
        String disk_version = null;

        Log.v(TAG, "Data version is " + data_version);

        // If no version, no unpacking is necessary.
        if (data_version == null) {
            return;
        }

        // Check the current disk version, if any.
        String filesDir = target.getAbsolutePath();
        String disk_version_fn = filesDir + "/" + resource + ".version";

        try {
            byte buf[] = new byte[64];
            InputStream is = new FileInputStream(disk_version_fn);
            int len = is.read(buf);
            disk_version = new String(buf, 0, len);
            is.close();
        } catch (Exception e) {
            disk_version = "";
        }

        // If the disk data is out of date, extract it and write the
        // version file.
        // if (! data_version.equals(disk_version)) {
        if (! data_version.equals(disk_version)) {
            Log.v(TAG, "Extracting " + resource + " assets.");

            recursiveDelete(target);
            target.mkdirs();

            AssetExtract ae = new AssetExtract(this);
            if (!ae.extractTar(resource + ".mp3", target.getAbsolutePath())) {
                toastError("Could not extract " + resource + " data.");
            }

            try {
                // Write .nomedia.
                new File(target, ".nomedia").createNewFile();

                // Write version file.
                FileOutputStream os = new FileOutputStream(disk_version_fn);
                os.write(data_version.getBytes());
                os.close();
            } catch (Exception e) {
                Log.w("python", e);
            }
        }
    }

    public static ViewGroup getLayout() {
        return   mLayout;
    }

    public static SurfaceView getSurface() {
        return   mSurface;
    }

    //----------------------------------------------------------------------------
    // Listener interface for onNewIntent
    //

    public interface NewIntentListener {
        void onNewIntent(Intent intent);
    }

    private List<NewIntentListener> newIntentListeners = null;

    public void registerNewIntentListener(NewIntentListener listener) {
        Log.v(TAG, "registerNewIntentListener()");
        if ( this.newIntentListeners == null )
            this.newIntentListeners = Collections.synchronizedList(new ArrayList<NewIntentListener>());
        this.newIntentListeners.add(listener);
    }

    public void unregisterNewIntentListener(NewIntentListener listener) {
        Log.v(TAG, "unregisterNewIntentListener()");
        if ( this.newIntentListeners == null )
            return;
        this.newIntentListeners.remove(listener);
    }

    @Override
    protected void onNewIntent(Intent intent) {
        if (intent != null) {
            String action = intent.getAction();
            Log.v(TAG, "onNewIntent() action is : " + action);
        } else {
            Log.v(TAG, "onNewIntent() intent is NULL!!!");
        }
        if ( this.newIntentListeners == null )
            return;
        this.onResume();
        synchronized ( this.newIntentListeners ) {
            Iterator<NewIntentListener> iterator = this.newIntentListeners.iterator();
            while ( iterator.hasNext() ) {
                (iterator.next()).onNewIntent(intent);
            }
        }
    }

    //----------------------------------------------------------------------------
    // Listener interface for onActivityResult
    //

    public interface ActivityResultListener {
        void onActivityResult(int requestCode, int resultCode, Intent data);
    }

    private List<ActivityResultListener> activityResultListeners = null;

    public void registerActivityResultListener(ActivityResultListener listener) {
        Log.v(TAG, "registerActivityResultListener()");
        if ( this.activityResultListeners == null )
            this.activityResultListeners = Collections.synchronizedList(new ArrayList<ActivityResultListener>());
        this.activityResultListeners.add(listener);
    }

    public void unregisterActivityResultListener(ActivityResultListener listener) {
        Log.v(TAG, "unregisterActivityResultListener()");
        if ( this.activityResultListeners == null )
            return;
        this.activityResultListeners.remove(listener);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent intent) {
        Log.v(TAG, "onActivityResult()");
        if (requestCode == INPUT_FILE_REQUEST_CODE && mUploadMessage != null) {
            parseSelectedFilePath(resultCode, intent);
            return;
        }
        if ( this.activityResultListeners == null )
            return;
        this.onResume();
        synchronized ( this.activityResultListeners ) {
            Iterator<ActivityResultListener> iterator = this.activityResultListeners.iterator();
            while ( iterator.hasNext() )
                (iterator.next()).onActivityResult(requestCode, resultCode, intent);
        }
    }

    public static void start_service(
            String serviceTitle,
            String serviceDescription,
            String pythonServiceArgument
            ) {
        _do_start_service(
            serviceTitle, serviceDescription, pythonServiceArgument, true
        );
    }

    public static void start_service_not_as_foreground(
            String serviceTitle,
            String serviceDescription,
            String pythonServiceArgument
            ) {
        _do_start_service(
            serviceTitle, serviceDescription, pythonServiceArgument, false
        );
    }

    public static void _do_start_service(
            String serviceTitle,
            String serviceDescription,
            String pythonServiceArgument,
            boolean showForegroundNotification
            ) {
        Log.v(TAG, "_do_start_service()");
        Intent serviceIntent = new Intent(PythonActivity.mActivity, PythonService.class);
        String argument = PythonActivity.mActivity.getFilesDir().getAbsolutePath();
        String filesDirectory = argument;
        String app_root_dir = PythonActivity.mActivity.getAppRoot();
        String entry_point = PythonActivity.mActivity.getEntryPoint(app_root_dir + "/service");
        serviceIntent.putExtra("androidPrivate", argument);
        serviceIntent.putExtra("androidArgument", app_root_dir);
        serviceIntent.putExtra("serviceEntrypoint", "service/" + entry_point);
        serviceIntent.putExtra("pythonName", "python");
        serviceIntent.putExtra("pythonHome", app_root_dir);
        serviceIntent.putExtra("pythonPath", app_root_dir + ":" + app_root_dir + "/lib");
        serviceIntent.putExtra("serviceStartAsForeground",
            (showForegroundNotification ? "true" : "false")
        );
        serviceIntent.putExtra("serviceTitle", serviceTitle);
        serviceIntent.putExtra("serviceDescription", serviceDescription);
        serviceIntent.putExtra("pythonServiceArgument", pythonServiceArgument);
        PythonActivity.mActivity.startService(serviceIntent);
    }

    public static void stop_service() {
        Log.v(TAG, "stop_service()");
        Intent serviceIntent = new Intent(PythonActivity.mActivity, PythonService.class);
        PythonActivity.mActivity.stopService(serviceIntent);
    }

    /** Loading screen view **/
    public static ImageView mImageView = null;
    /** Whether main routine/actual app has started yet **/
    protected boolean mAppConfirmedActive = false;
    /** Timer for delayed loading screen removal. **/
    protected Timer loadingScreenRemovalTimer = null; 

    // Overridden since it's called often, to check whether to remove the
    // loading screen:
    @Override
    protected boolean sendCommand(int command, Object data) {
        boolean result = super.sendCommand(command, data);
        considerLoadingScreenRemoval();
        return result;
    }
   
    /** Confirm that the app's main routine has been launched.
     **/
    @Override
    public void appConfirmedActive() {
        Log.v(TAG, "appConfirmedActive()");
        if (!mAppConfirmedActive) {
            Log.v(TAG, "appConfirmedActive() -> preparing loading screen removal");
            mAppConfirmedActive = true;
            considerLoadingScreenRemoval();
        }
    }

    /** This is called from various places to check whether the app's main
     *  routine has been launched already, and if it has, then the loading
     *  screen will be removed.
     **/
    public void considerLoadingScreenRemoval() {
        Log.v(TAG, "considerLoadingScreenRemoval()");
        //requestGetURL("http://localhost:8180/process/health/v1");
        if (loadingScreenRemovalTimer != null)
            return;
        runOnUiThread(new Runnable() {
            public void run() {
                if (((PythonActivity)PythonActivity.mSingleton).mAppConfirmedActive &&
                        loadingScreenRemovalTimer == null) {
                    // Remove loading screen but with a delay.
                    // (app can use p4a's android.loadingscreen module to
                    // do it quicker if it wants to)
                    // get a handler (call from main thread)
                    // this will run when timer elapses
                    TimerTask removalTask = new TimerTask() {
                        @Override
                        public void run() {
                            // post a runnable to the handler
                            runOnUiThread(new Runnable() {
                                @Override
                                public void run() {
                                    PythonActivity activity =
                                        ((PythonActivity)PythonActivity.mSingleton);
                                    if (activity != null)
                                        activity.removeLoadingScreen();
                                }
                            });
                        }
                    };
                    loadingScreenRemovalTimer = new Timer();
                    loadingScreenRemovalTimer.schedule(removalTask, 5000);
                }
            }
        });
    }

    public void removeLoadingScreen() {
        Log.v(TAG, "removeLoadingScreen()");
        runOnUiThread(new Runnable() {
            public void run() {
                if (PythonActivity.mImageView != null && 
                        PythonActivity.mImageView.getParent() != null) {
                    ((ViewGroup)PythonActivity.mImageView.getParent()).removeView(
                        PythonActivity.mImageView);
                    PythonActivity.mImageView = null;
                }
            }
        });
    }

    public String getEntryPoint(String search_dir) {
        /* Get the main file (.pyc|.pyo|.py) depending on if we
         * have a compiled version or not.
        */
        List<String> entryPoints = new ArrayList<String>();
        entryPoints.add("main.pyo");  // python 2 compiled files
        entryPoints.add("main.pyc");  // python 3 compiled files
		for (String value : entryPoints) {
            File mainFile = new File(search_dir + "/" + value);
            if (mainFile.exists()) {
                return value;
            }
        }
        return "main.py";
    }

    protected void showLoadingScreen() {
        // load the bitmap
        // 1. if the image is valid and we don't have layout yet, assign this bitmap
        // as main view.
        // 2. if we have a layout, just set it in the layout.
        // 3. If we have an mImageView already, then do nothing because it will have
        // already been made the content view or added to the layout.
        Log.v(TAG, "showLoadingScreen()");
        if (mImageView == null) {
            int presplashId = this.resourceManager.getIdentifier("presplash", "drawable");
            InputStream is = this.getResources().openRawResource(presplashId);
            Bitmap bitmap = null;
            try {
                bitmap = BitmapFactory.decodeStream(is);
            } finally {
                try {
                    is.close();
                } catch (IOException e) {};
            }

            mImageView = new ImageView(this);
            mImageView.setImageBitmap(bitmap);

            /*
             * Set the presplash loading screen background color
             * https://developer.android.com/reference/android/graphics/Color.html
             * Parse the color string, and return the corresponding color-int.
             * If the string cannot be parsed, throws an IllegalArgumentException exception.
             * Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
             * 'red', 'blue', 'green', 'black', 'white', 'gray', 'cyan', 'magenta', 'yellow',
             * 'lightgray', 'darkgray', 'grey', 'lightgrey', 'darkgrey', 'aqua', 'fuchsia',
             * 'lime', 'maroon', 'navy', 'olive', 'purple', 'silver', 'teal'.
             */
            String backgroundColor = resourceManager.getString("presplash_color");
            if (backgroundColor != null) {
                try {
                    mImageView.setBackgroundColor(Color.parseColor(backgroundColor));
                } catch (IllegalArgumentException e) {}
            }   
            mImageView.setLayoutParams(new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.FILL_PARENT,
                ViewGroup.LayoutParams.FILL_PARENT));
            mImageView.setScaleType(ImageView.ScaleType.FIT_CENTER);
        }

        try {
            if (mLayout == null) {
                setContentView(mImageView);
            } else if (PythonActivity.mImageView.getParent() == null) {
                mLayout.addView(mImageView);
            }
        } catch (IllegalStateException e) {
            // The loading screen can be attempted to be applied twice if app
            // is tabbed in/out, quickly.
            // (Gives error "The specified child already has a parent.
            // You must call removeView() on the child's parent first.")
        }
    }

    @Override
    protected void onStart() {
        Log.v(TAG, "onStart()");
        try {
            super.onStart();
        } catch (Exception e) {
            Log.v(TAG, "onStart() failed : " + e);
        }
    }

    @Override
    protected void onStop() {
        Log.v(TAG, "onStop() isFinishing: " + this.isFinishing());
        //requestGetURL("http://localhost:8180/process/stop/v1");
        try {
            super.onStop();
        } catch (Exception e) {
            Log.v(TAG, "onStop() failed : " + e);
        }
    }

    @Override
    protected void onDestroy() {
        Log.v(TAG, "onDestroy()");
        String process_stop_result = requestGetURL("http://localhost:8180/process/stop/v1");
        Log.v(TAG, "onDestroy() process_stop_result : " + process_stop_result);
        String process_health_result = "ok";
        while (process_health_result != "") {
            process_health_result = requestGetURL("http://localhost:8180/process/health/v1");
            Log.v(TAG, "onDestroy() process_health_result : " + process_health_result);
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.HONEYCOMB) {
            if (this.webView != null) {
                Log.v(TAG, "onDestroy()   about to call webView.destroy()");
                this.webView.destroy();
                this.webView = null;
            }
        }
        Log.v(TAG, "onDestroy()   about to call super onDestroy");
        try {
            super.onDestroy();
        } catch (Exception e) {
            Log.v(TAG, "onDestroy() super onDestroy failed : " + e);
        }
        Log.v(TAG, "onDestroy() success");
        Log.v(TAG, "onDestroy() going to kill process " + Process.myPid());
        Process.killProcess(Process.myPid());
        Log.v(TAG, "onDestroy() process suppose tobe killed");
    }

    @Override
    protected void onPause() {
        Log.v(TAG, "onPause() isFinishing: " + this.isFinishing());
        if (this.mWakeLock != null && mWakeLock.isHeld()) {
            Log.v(TAG, "onPause() will call mWakeLock.release()");
            this.mWakeLock.release();
        }
        try {
            super.onPause();
        } catch (Exception e) {
            Log.v(TAG, "onPause() failed : " + e);
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.HONEYCOMB) {
            if (this.webView != null) {
                Log.v(TAG, "onPause()   about to call webView.onPause()");
                this.webView.onPause();
                this.webView.pauseTimers();
            }
        }
    }

    @Override
    protected void onResume() {
        Log.v(TAG, "onResume()");
        if (this.mWakeLock != null) {
            Log.v(TAG, "onResume() mWakeLock.acquire()");
            this.mWakeLock.acquire();
        }
        try {
            super.onResume();
        } catch (Exception e) {
            Log.v(TAG, "onResume() failed : " + e);
        }
        considerLoadingScreenRemoval();
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.HONEYCOMB) {
            if (this.webView != null) {
                Log.v(TAG, "onResume()   about to call webView.resumeTimers()");
                this.webView.resumeTimers();
                this.webView.onResume();
            }
        }
    }

    @Override
    protected void onRestart() {
        Log.v(TAG, "onRestart()");
        super.onRestart();
    }

    @Override
    public void onDetachedFromWindow() {
        Log.v(TAG, "onDetachedFromWindow()");
        super.onDetachedFromWindow();
    }

    @Override
    public void onAttachedToWindow() {
        Log.v(TAG, "onAttachedToWindow()");
        super.onAttachedToWindow();
    }

    @Override
    public void onActivityReenter(int resultCode, Intent data) {
        Log.v(TAG, "onActivityReenter() " + resultCode);
        super.onActivityReenter(resultCode, data);
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        Log.v(TAG, "onWindowFocusChanged()");
        try {
            super.onWindowFocusChanged(hasFocus);
        } catch (UnsatisfiedLinkError e) {
            // Catch window focus while still in loading screen failing to
            // call native function (since it's not yet loaded)
        }
        considerLoadingScreenRemoval();
    }

    /**
     * Used by android.permissions p4a module to register a call back after
     * requesting runtime permissions
     **/
    public interface PermissionsCallback {
        void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults);
    }

    private PermissionsCallback permissionCallback;
    private boolean havePermissionsCallback = false;

    public void addPermissionsCallback(PermissionsCallback callback) {
        permissionCallback = callback;
        havePermissionsCallback = true;
        Log.v(TAG, "addPermissionsCallback(): Added callback for onRequestPermissionsResult");
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        Log.v(TAG, "onRequestPermissionsResult()");
        if (havePermissionsCallback) {
            Log.v(TAG, "onRequestPermissionsResult passed to callback");
            permissionCallback.onRequestPermissionsResult(requestCode, permissions, grantResults);
        }
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
    }

    /**
     * Used by android.permissions p4a module to check a permission
     **/
    public boolean checkCurrentPermission(String permission) {
        Log.v(TAG, "checkCurrentPermission()");
        if (Build.VERSION.SDK_INT < 23)
            return true;

        try {
            java.lang.reflect.Method methodCheckPermission =
                Activity.class.getMethod("checkSelfPermission", java.lang.String.class);
            Object resultObj = methodCheckPermission.invoke(this, permission);
            int result = Integer.parseInt(resultObj.toString());
            if (result == PackageManager.PERMISSION_GRANTED) 
                return true;
        } catch (IllegalAccessException | NoSuchMethodException |
                 InvocationTargetException e) {
        }
        return false;
    }

    /**
     * Used by android.permissions p4a module to request runtime permissions
     **/
    public void requestPermissionsWithRequestCode(String[] permissions, int requestCode) {
        Log.v(TAG, "requestPermissionsWithRequestCode()");
        if (Build.VERSION.SDK_INT < 23)
            return;
        try {
            java.lang.reflect.Method methodRequestPermission =
                Activity.class.getMethod("requestPermissions",
                java.lang.String[].class, int.class);
            methodRequestPermission.invoke(this, permissions, requestCode);
        } catch (IllegalAccessException | NoSuchMethodException |
                 InvocationTargetException e) {
        }
    }

    public void requestPermissions(String[] permissions) {
        Log.v(TAG, "requestPermissions()");
        requestPermissionsWithRequestCode(permissions, 1);
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
