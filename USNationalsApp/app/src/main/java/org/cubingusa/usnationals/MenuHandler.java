package org.cubingusa.usnationals;

import android.content.Context;
import android.content.Intent;
import android.net.Uri;
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
            case R.id.action_cubecomps_link:
                Uri cubecomps_uri = new Uri.Builder()
                        .scheme("https")
                        .authority("m.cubecomps.com")
                        .build();
                intent.setAction(Intent.ACTION_VIEW);
                intent.setData(cubecomps_uri);
                return intent;
            case R.id.action_cubingusa_link:
                Uri cubingusa_uri = new Uri.Builder()
                        .scheme("https")
                        .authority("www.cubingusa.org")
                        .appendPath("nationals")
                        .appendPath("2018")
                        .build();
                intent.setAction(Intent.ACTION_VIEW);
                intent.setData(cubingusa_uri);
                return intent;
            default:
                return null;
        }
    }
}
