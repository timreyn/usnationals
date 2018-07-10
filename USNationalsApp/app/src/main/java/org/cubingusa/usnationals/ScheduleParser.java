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
    private GregorianCalendar mLastGroupDate = null;

    public ScheduleParser(Context context, LayoutInflater inflater, LinearLayout container) {
        this.mContext = context;
        this.mContainer = container;
        this.mInflater = inflater;
        this.mEventIcons = new EventIcons(mContext);
    }

    public Pair<Group, LinearLayout> parseGroup(JsonReader reader) throws IOException {
        final Group group = new Group();
        group.parseFromJson(reader);

        StringBuilder builder = new StringBuilder();
        builder.append(group.event.name);
        builder.append(" ");
        if (!group.stage.name.equals("")) {
            builder.append(group.stage.name);
            builder.append(" ");
        }
        builder.append(group.number);

        LinearLayout scheduleItem =
                addScheduleItem(group, builder.toString(), group.event, group.stage.color);
        return new Pair<Group, LinearLayout>(group, scheduleItem);
    }

    public void parseStaffAssignment(JsonReader reader) throws IOException {
        StaffAssignment staffAssignment = new StaffAssignment(new HashSet<String>());
        staffAssignment.parseFromJson(reader);

        Event event = staffAssignment.group.event;
        int color = staffAssignment.group.stage.color;

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
                color = Color.parseColor("#FFFF00");
                break;
            case "U":
                builder.append("Scramble ");
                builder.append(staffAssignment.longEvent.event.name);
                event = staffAssignment.longEvent.event;
                color = Color.parseColor("#FFFF00");
                break;
            case "D":
                builder.append("Data entry");
                event = null;
                color = Color.parseColor("#FFFFFF");
                break;
            case "H":
                builder.append("Help desk");
                event = null;
                color = Color.parseColor("#FFFFFF");
                break;
            case "Y":
                builder.append(staffAssignment.misc);
                event = null;
                color = Color.parseColor("#FFFFFF");
                break;
        }
        if (!staffAssignment.job.equals("Y")) {
            builder.append(" - ");
            builder.append(staffAssignment.group.event.id);
            if (staffAssignment.group.event.isReal) {
                builder.append(" group ");
                builder.append(staffAssignment.group.number);
            }
        }

        addScheduleItem(staffAssignment.group, builder.toString(), event, color);
    }

    public LinearLayout addScheduleItem(
            final Group group, String text, final Event event, final int color) {
        DateFormat format = DateFormat.getTimeInstance(DateFormat.SHORT);

        if (group.startTime != null) {
            if (mLastGroupDate == null ||
                    group.startTime.get(Calendar.DAY_OF_YEAR) !=
                            mLastGroupDate.get(Calendar.DAY_OF_YEAR)) {
                Util.addDivider(group.startTime.getDisplayName(
                        Calendar.DAY_OF_WEEK, Calendar.LONG, Locale.getDefault()),
                        mInflater, mContainer);
                mItemsAdded++;
            }
            mLastGroupDate = group.startTime;
        }

        mInflater.inflate(R.layout.content_schedule_item, mContainer);
        LinearLayout scheduleItem = (LinearLayout) mContainer.getChildAt(mItemsAdded);
        TextView scheduleItemTime = (TextView) scheduleItem.getChildAt(0);
        ImageView scheduleItemIcon = (ImageView) scheduleItem.getChildAt(1);
        TextView scheduleItemName = (TextView) scheduleItem.getChildAt(2);

        scheduleItemTime.setText(format.format(group.startTime.getTime()));
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
                intent.setClass(mContext, GroupInfoActivity.class);
                intent.putExtra(GroupInfoActivity.HEAT_ID_EXTRA, group.number);
                intent.putExtra(GroupInfoActivity.STAGE_ID_EXTRA, group.stage.id);
                intent.putExtra(GroupInfoActivity.ROUND_ID_EXTRA, group.round.number);
                intent.putExtra(GroupInfoActivity.EVENT_ID_EXTRA, group.event.id);
                mContext.startActivity(intent);
            }
        });


        scheduleItemName.setText(text);
        mItemsAdded++;

        return scheduleItem;
    }
}
