package org.cubingusa.usnationals;

import android.content.Context;
import android.graphics.Color;
import android.util.JsonReader;
import android.util.Log;
import android.util.Pair;
import android.view.LayoutInflater;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.io.IOException;
import java.text.DateFormat;
import java.util.GregorianCalendar;

import cz.msebera.android.httpclient.ParseException;

public class ScheduleParser {
    private static final String TAG = "ScheduleParser";

    private final LinearLayout mContainer;
    private final Context mContext;
    private final LayoutInflater mInflater;
    private EventIcons mEventIcons;
    private int mItemsAdded = 0;

    public ScheduleParser(Context context, LayoutInflater inflater, LinearLayout container) {
        this.mContext = context;
        this.mContainer = container;
        this.mInflater = inflater;
        this.mEventIcons = new EventIcons(mContext);
    }

    public class Heat {
        public LinearLayout layout;
        public String eventName = "";
        public int heatNumber = 0;
        public String stageName = "";
    }

    public Heat parseHeat(JsonReader reader) throws IOException {
        mInflater.inflate(R.layout.content_schedule_item, mContainer);
        Heat heat = new Heat();
        LinearLayout scheduleItem = (LinearLayout) mContainer.getChildAt(mItemsAdded);
        TextView scheduleItemTime = (TextView) scheduleItem.getChildAt(0);
        ImageView scheduleItemIcon = (ImageView) scheduleItem.getChildAt(1);
        TextView scheduleItemName = (TextView) scheduleItem.getChildAt(2);
        while (reader.hasNext()) {
            switch (reader.nextName()) {
                case "start_time":
                    GregorianCalendar time = parseTime(reader);
                    DateFormat format = DateFormat.getTimeInstance(DateFormat.SHORT);
                    try {
                        scheduleItemTime.setText(format.format(time.getTime()));
                    } catch (ParseException e) {
                        Log.e(TAG, e.toString());
                    }
                    break;
                case "stage":
                    heat.stageName = parseStage(reader, scheduleItem);
                    break;
                case "round":
                    reader.beginObject();
                    Pair<String, String> eventIdAndName = parseRound(reader);
                    reader.endObject();
                    scheduleItemIcon.setImageDrawable(
                            mEventIcons.getDrawable(eventIdAndName.first));
                    heat.eventName = eventIdAndName.second;
                    break;
                case "number":
                    heat.heatNumber = reader.nextInt();
                    break;
                default:
                    reader.skipValue();
            }
        }
        StringBuilder builder = new StringBuilder();
        builder.append(heat.eventName);
        builder.append(" ");
        if (!heat.stageName.equals("")) {
            builder.append(heat.stageName);
            builder.append(" ");
        }
        builder.append(heat.heatNumber);
        scheduleItemName.setText(builder.toString());
        heat.layout = scheduleItem;
        mItemsAdded++;

        return heat;
    }

    private GregorianCalendar parseTime(JsonReader reader) throws IOException {
        reader.beginObject();
        GregorianCalendar time = new GregorianCalendar();
        while (reader.hasNext()) {
            switch (reader.nextName()) {
                case "year":
                    time.set(GregorianCalendar.YEAR, reader.nextInt());
                    break;
                case "month":
                    time.set(GregorianCalendar.MONTH, reader.nextInt());
                    break;
                case "day":
                    time.set(GregorianCalendar.DAY_OF_MONTH, reader.nextInt());
                    break;
                case "hour":
                    time.set(GregorianCalendar.HOUR_OF_DAY, reader.nextInt());
                    break;
                case "minute":
                    time.set(GregorianCalendar.MINUTE, reader.nextInt());
                    break;
                default:
                    reader.skipValue();
            }
        }
        reader.endObject();
        return time;
    }

    private String parseStage(JsonReader reader, LinearLayout layout) throws IOException {
        reader.beginObject();
        String stageName = "";
        while (reader.hasNext()) {
            switch(reader.nextName()) {
                case "color_hex":
                    layout.setBackgroundColor(Color.parseColor(reader.nextString()));
                    break;
                case "name":
                    stageName = reader.nextString();
                    break;
                default:
                    reader.skipValue();
            }
        }
        reader.endObject();
        return stageName;
    }

    private Pair<String, String> parseRound(JsonReader reader) throws IOException {
        String eventId = "";
        String eventName = "";
        while (reader.hasNext()) {
            String name = reader.nextName();
            if (name.equals("event")) {
                reader.beginObject();
                while (reader.hasNext()) {
                    switch (reader.nextName()) {
                        case "id":
                            eventId = reader.nextString();
                            break;
                        case "name":
                            eventName = reader.nextString();
                            break;
                        default:
                            reader.skipValue();
                    }
                }
                reader.endObject();
            } else {
                reader.skipValue();
            }
        }
        return new Pair<String, String>(eventId, eventName);
    }
}
