package org.cubingusa.usnationals;

import android.content.Context;
import android.content.Intent;
import android.view.MenuItem;

public class MenuHandler {
    public static Intent menuOptionIntent(Context context, MenuItem item) {
        Intent intent = new Intent();
        switch (item.getItemId()) {
            case R.id.action_competitor_list:
                intent.setClass(context, CompetitorListActivity.class);
                return intent;
            case R.id.action_admin:
                intent.setClass(context, AdminActivity.class);
                return intent;
            case R.id.action_stage_schedule:
                intent.setClass(context, StageScheduleActivity.class);
                return intent;
            default:
                return null;
        }
    }
}
