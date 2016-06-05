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
import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.Locale;

import cz.msebera.android.httpclient.ParseException;

public class ScheduleParser {
    private static final String TAG = "ScheduleParser";

    private final LinearLayout mContainer;
    private final Context mContext;
    private final LayoutInflater mInflater;
    private EventIcons mEventIcons;
    private int mItemsAdded = 0;
    private GregorianCalendar mLastHeatDate = null;

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
        public String stageColorHex = "#000000";
    }

    public Heat parseHeat(JsonReader reader) throws IOException {
        Heat heat = new Heat();

        GregorianCalendar currentDate = null;

        String timeString = "";
        String eventId = "";

        while (reader.hasNext()) {
            switch (reader.nextName()) {
                case "start_time":
                    currentDate = parseTime(reader);
                    DateFormat format = DateFormat.getTimeInstance(DateFormat.SHORT);
                    try {
                        timeString = format.format(currentDate.getTime());
                    } catch (ParseException e) {
                        Log.e(TAG, e.toString());
                    }
                    break;
                case "stage":
                    parseStage(reader, heat);
                    break;
                case "round":
                    reader.beginObject();
                    Pair<String, String> eventIdAndName = parseRound(reader);
                    reader.endObject();
                    eventId = eventIdAndName.first;
                    heat.eventName = eventIdAndName.second;
                    break;
                case "number":
                    heat.heatNumber = reader.nextInt();
                    break;
                default:
                    reader.skipValue();
            }
        }
        if (currentDate != null) {
            if (mLastHeatDate == null ||
                    currentDate.get(Calendar.DAY_OF_YEAR) != mLastHeatDate.get(Calendar.DAY_OF_YEAR)) {
                mInflater.inflate(R.layout.content_divider, mContainer);
                LinearLayout divider = (LinearLayout) mContainer.getChildAt(mItemsAdded);
                ((TextView) divider.getChildAt(0)).setText(currentDate.getDisplayName(
                        Calendar.DAY_OF_WEEK, Calendar.LONG, Locale.getDefault()));
                mItemsAdded++;
            }
            mLastHeatDate = currentDate;
        }

        mInflater.inflate(R.layout.content_schedule_item, mContainer);
        LinearLayout scheduleItem = (LinearLayout) mContainer.getChildAt(mItemsAdded);
        TextView scheduleItemTime = (TextView) scheduleItem.getChildAt(0);
        ImageView scheduleItemIcon = (ImageView) scheduleItem.getChildAt(1);
        TextView scheduleItemName = (TextView) scheduleItem.getChildAt(2);

        scheduleItemTime.setText(timeString);
        scheduleItem.setBackgroundColor(Color.parseColor(heat.stageColorHex));
        scheduleItemIcon.setImageDrawable(mEventIcons.getDrawable(eventId));

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

    private void parseStage(JsonReader reader, Heat heat) throws IOException {
        reader.beginObject();
        while (reader.hasNext()) {
            switch(reader.nextName()) {
                case "color_hex":
                    heat.stageColorHex = reader.nextString();
                    break;
                case "name":
                    heat.stageName = reader.nextString();
                    break;
                default:
                    reader.skipValue();
            }
        }
        reader.endObject();
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
