package org.cubingusa.usnationals;

import android.content.Context;
import android.content.Intent;
import android.util.JsonReader;
import android.util.Pair;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.io.IOException;
import java.text.DateFormat;
import java.util.Calendar;
import java.util.GregorianCalendar;
import java.util.Locale;

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

    public Pair<Heat, LinearLayout> parseHeat(JsonReader reader) throws IOException {
        final Heat heat = new Heat();
        heat.parseFromJson(reader);

        DateFormat format = DateFormat.getTimeInstance(DateFormat.SHORT);

        if (heat.startTime != null) {
            if (mLastHeatDate == null ||
                    heat.startTime.get(Calendar.DAY_OF_YEAR) != mLastHeatDate.get(Calendar.DAY_OF_YEAR)) {
                Util.addDivider(heat.startTime.getDisplayName(
                        Calendar.DAY_OF_WEEK, Calendar.LONG, Locale.getDefault()),
                        mInflater, mContainer);
                mItemsAdded++;
            }
            mLastHeatDate = heat.startTime;
        }

        mInflater.inflate(R.layout.content_schedule_item, mContainer);
        LinearLayout scheduleItem = (LinearLayout) mContainer.getChildAt(mItemsAdded);
        TextView scheduleItemTime = (TextView) scheduleItem.getChildAt(0);
        ImageView scheduleItemIcon = (ImageView) scheduleItem.getChildAt(1);
        TextView scheduleItemName = (TextView) scheduleItem.getChildAt(2);

        scheduleItemTime.setText(format.format(heat.startTime.getTime()));
        scheduleItem.setBackgroundColor(heat.stage.color);
        scheduleItemIcon.setImageDrawable(mEventIcons.getDrawable(heat.event.id));

        scheduleItem.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent();
                intent.setClass(mContext, HeatInfoActivity.class);
                intent.putExtra(HeatInfoActivity.HEAT_ID_EXTRA, heat.number);
                intent.putExtra(HeatInfoActivity.STAGE_ID_EXTRA, heat.stage.id);
                intent.putExtra(HeatInfoActivity.ROUND_ID_EXTRA, heat.round.number);
                intent.putExtra(HeatInfoActivity.EVENT_ID_EXTRA, heat.event.id);
                mContext.startActivity(intent);
            }
        });

        StringBuilder builder = new StringBuilder();
        builder.append(heat.event.name);
        builder.append(" ");
        if (!heat.stage.name.equals("")) {
            builder.append(heat.stage.name);
            builder.append(" ");
        }
        builder.append(heat.number);
        scheduleItemName.setText(builder.toString());
        mItemsAdded++;

        return new Pair<Heat, LinearLayout>(heat, scheduleItem);
    }
}
