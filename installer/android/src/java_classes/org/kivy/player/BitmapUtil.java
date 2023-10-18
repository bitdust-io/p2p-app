package org.kivy.player;

import android.graphics.Bitmap;
import java.nio.ByteBuffer;
import java.nio.IntBuffer;

// This is probably only useful for small bitmaps

public class BitmapUtil {

    public byte[] toPixels(Bitmap bitmap) {	
	int width = bitmap.getWidth();
        int height= bitmap.getHeight();
	
	ByteBuffer buffer = ByteBuffer.allocateDirect(width * height * 4);
	// copyPixelsToBuffer uses Bitmap internal RGBA not BGRA or ARGB
	bitmap.copyPixelsToBuffer(buffer);
	bitmap.recycle();
	return buffer.array();
    }   
}
