package org.cubingusa.usnationals;

import android.view.LayoutInflater;
import android.widget.LinearLayout;
import android.widget.TextView;

public class Util {
    public static void addDivider(String text, LayoutInflater inflater, LinearLayout container) {
        inflater.inflate(R.layout.content_divider, container);
        LinearLayout divider = (LinearLayout) container.getChildAt(
                container.getChildCount() - 1);
        ((TextView) divider.getChildAt(0)).setText(text);
    }
}
