package org.cubingusa.usnationals;

import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
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
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

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

        StringBuilder builder = new StringBuilder();
        builder.append(heat.event.name);
        builder.append(" ");
        if (!heat.stage.name.equals("")) {
            builder.append(heat.stage.name);
            builder.append(" ");
        }
        builder.append(heat.number);

        LinearLayout scheduleItem =
                addScheduleItem(heat, builder.toString(), heat.event, heat.stage.color);
        return new Pair<Heat, LinearLayout>(heat, scheduleItem);
    }

    public void parseStaffAssignment(JsonReader reader) throws IOException {
        StaffAssignment staffAssignment = new StaffAssignment(new HashSet<String>());
        staffAssignment.parseFromJson(reader);

        Event event = staffAssignment.heat.event;
        int color = staffAssignment.heat.stage.color;

        StringBuilder builder = new StringBuilder();
        switch (staffAssignment.job) {
            case "J":
                builder.append("Judge station ");
                builder.append(staffAssignment.station);
                break;
            case "S":
                builder.append("Scramble ");
                break;
            case "R":
                builder.append("Run ");
                break;
            case "L":
                builder.append("Judge ");
                builder.append(staffAssignment.longEvent.event.name);
                event = staffAssignment.longEvent.event;
                color = Color.parseColor("#FFFFFF");
                break;
            case "U":
                builder.append("Scramble ");
                builder.append(staffAssignment.longEvent.event.name);
                event = staffAssignment.longEvent.event;
                color = Color.parseColor("#FFFFFF");
                break;
            case "D":
                builder.append("Data entry");
                event = null;
                color = Color.parseColor("#FF0000");
                break;
            case "H":
                builder.append("Help desk");
                event = null;
                color = Color.parseColor("#FF0000");
                break;
            case "Y":
                builder.append(staffAssignment.misc);
                event = null;
                color = Color.parseColor("#FF0000");
                break;
        }
        builder.append(" - ");
        builder.append(staffAssignment.heat.event.id);
        if (staffAssignment.heat.event.isReal) {
            builder.append(" heat ");
            builder.append(staffAssignment.heat.number);
        }

        addScheduleItem(staffAssignment.heat, builder.toString(), event, color);
    }

    public LinearLayout addScheduleItem(
            final Heat heat, String text, final Event event, final int color) {
        DateFormat format = DateFormat.getTimeInstance(DateFormat.SHORT);

        if (heat.startTime != null) {
            if (mLastHeatDate == null ||
                    heat.startTime.get(Calendar.DAY_OF_YEAR) !=
                            mLastHeatDate.get(Calendar.DAY_OF_YEAR)) {
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
        scheduleItem.setBackgroundColor(color);
        if (event == null) {
            scheduleItemIcon.setVisibility(View.INVISIBLE);
        } else {
            scheduleItemIcon.setImageDrawable(mEventIcons.getDrawable(event.id));
        }

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

        scheduleItemName.setText(text);
        mItemsAdded++;

        return scheduleItem;
    }
}
