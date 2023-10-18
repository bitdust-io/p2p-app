package org.kivy.player;

import java.lang.String;
import android.net.Uri;
import android.provider.MediaStore;
import android.provider.BaseColumns;

public class MediaStoreConstants {
    public static final Uri GENRE_TABLE = MediaStore.Audio.Genres.EXTERNAL_CONTENT_URI;
    public static final Uri MEDIA_TABLE = MediaStore.Audio.Media.EXTERNAL_CONTENT_URI;
    public static final String ID = BaseColumns._ID;
    public static final String GENRE_NAME = MediaStore.Audio.GenresColumns.NAME;
    public static final String GENRE = MediaStore.Audio.AudioColumns.GENRE;
    public static final String GENRE_ID = MediaStore.Audio.AudioColumns.GENRE_ID;
    public static final String ALBUM = MediaStore.Audio.AlbumColumns.ALBUM;
    public static final String ALBUM_ID = MediaStore.Audio.AlbumColumns.ALBUM_ID;
    public static final String ALBUM_ARTIST = MediaStore.MediaColumns.ALBUM_ARTIST;
    public static final String TITLE = MediaStore.MediaColumns.TITLE;
    public static final String DISPLAY_NAME = MediaStore.MediaColumns.DISPLAY_NAME;
}
