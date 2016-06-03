package org.cubingusa.usnationals;

import android.content.Context;
import android.graphics.drawable.Drawable;
import android.support.v4.content.ContextCompat;

import java.util.HashMap;
import java.util.Map;

public class EventIcons {
    private Map<String, Drawable> drawableMap;

    public EventIcons(Context context) {
        drawableMap = new HashMap<String, Drawable>();
        drawableMap.put("222", ContextCompat.getDrawable(context, R.drawable.e_222));
        drawableMap.put("333", ContextCompat.getDrawable(context, R.drawable.e_333));
        drawableMap.put("333bf", ContextCompat.getDrawable(context, R.drawable.e_333bf));
        drawableMap.put("333fm", ContextCompat.getDrawable(context, R.drawable.e_333fm));
        drawableMap.put("333ft", ContextCompat.getDrawable(context, R.drawable.e_333ft));
        drawableMap.put("333mbf", ContextCompat.getDrawable(context, R.drawable.e_333mbf));
        drawableMap.put("333oh", ContextCompat.getDrawable(context, R.drawable.e_333oh));
        drawableMap.put("444", ContextCompat.getDrawable(context, R.drawable.e_444));
        drawableMap.put("444bf", ContextCompat.getDrawable(context, R.drawable.e_444bf));
        drawableMap.put("555", ContextCompat.getDrawable(context, R.drawable.e_555));
        drawableMap.put("555bf", ContextCompat.getDrawable(context, R.drawable.e_555bf));
        drawableMap.put("666", ContextCompat.getDrawable(context, R.drawable.e_666));
        drawableMap.put("777", ContextCompat.getDrawable(context, R.drawable.e_777));
        drawableMap.put("clock", ContextCompat.getDrawable(context, R.drawable.e_clock));
        drawableMap.put("minx", ContextCompat.getDrawable(context, R.drawable.e_minx));
        drawableMap.put("pyram", ContextCompat.getDrawable(context, R.drawable.e_pyram));
        drawableMap.put("skewb", ContextCompat.getDrawable(context, R.drawable.e_skewb));
        drawableMap.put("sq1", ContextCompat.getDrawable(context, R.drawable.e_sq1));
    }

    public Drawable getDrawable(String eventId) {
        if (drawableMap.containsKey(eventId)) {
            return drawableMap.get(eventId);
        }
        return null;
    }
}
