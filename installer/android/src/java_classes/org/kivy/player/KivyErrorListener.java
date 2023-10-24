package org.kivy.player;

import android.media.MediaPlayer;
import android.media.MediaPlayer.OnErrorListener;
import org.kivy.player.CallbackWrapper;


public class KivyErrorListener implements OnErrorListener {

    private CallbackWrapper callback_wrapper;

    public KivyErrorListener(CallbackWrapper callback_wrapper) {	
	this.callback_wrapper = callback_wrapper;
    }       

    @Override
    public boolean onError (MediaPlayer mp, int what, int extra) {
	this.callback_wrapper.on_error();
	return true;
    }
}
