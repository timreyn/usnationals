package org.cubingusa.usnationals;

import android.content.Context;
import android.graphics.drawable.Drawable;
import android.support.v4.content.ContextCompat;

import java.util.HashMap;
import java.util.Map;

public class EventIcons {
    private final Context context;
    private Map<String, Integer> drawableMap;

    public EventIcons(Context context) {
        this.context = context;
        drawableMap = new HashMap<String, Integer>();
        drawableMap.put("222", R.drawable.e_222);
        drawableMap.put("333", R.drawable.e_333);
        drawableMap.put("333bf", R.drawable.e_333bf);
        drawableMap.put("333fm", R.drawable.e_333fm);
        drawableMap.put("333ft", R.drawable.e_333ft);
        drawableMap.put("333mbf", R.drawable.e_333mbf);
        drawableMap.put("333oh", R.drawable.e_333oh);
        drawableMap.put("444", R.drawable.e_444);
        drawableMap.put("444bf", R.drawable.e_444bf);
        drawableMap.put("555", R.drawable.e_555);
        drawableMap.put("555bf", R.drawable.e_555bf);
        drawableMap.put("666", R.drawable.e_666);
        drawableMap.put("777", R.drawable.e_777);
        drawableMap.put("clock", R.drawable.e_clock);
        drawableMap.put("minx", R.drawable.e_minx);
        drawableMap.put("pyram", R.drawable.e_pyram);
        drawableMap.put("skewb", R.drawable.e_skewb);
        drawableMap.put("sq1", R.drawable.e_sq1);
    }

    public Drawable getDrawable(String eventId) {
        if (drawableMap.containsKey(eventId)) {
            return ContextCompat.getDrawable(context, drawableMap.get(eventId));
        }
        return null;
    }

    public int getDrawableId(String eventId) {
        if (drawableMap.containsKey(eventId)) {
            return drawableMap.get(eventId);
        }
        return -1;
    }
}
