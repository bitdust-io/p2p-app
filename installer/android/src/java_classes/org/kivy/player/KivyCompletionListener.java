package org.kivy.player;

import android.media.MediaPlayer;
import android.media.MediaPlayer.OnCompletionListener;
import org.kivy.player.CallbackWrapper;


public class KivyCompletionListener implements OnCompletionListener {

    private CallbackWrapper callback_wrapper;

    public KivyCompletionListener(CallbackWrapper callback_wrapper) {	
	this.callback_wrapper = callback_wrapper;
    }       

    @Override
    public void onCompletion (MediaPlayer mp) {
	this.callback_wrapper.on_completion();
    }
}
