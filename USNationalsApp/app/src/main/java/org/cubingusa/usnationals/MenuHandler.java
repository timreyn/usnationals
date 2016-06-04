package org.cubingusa.usnationals;

import android.content.Context;
import android.content.Intent;
import android.view.MenuItem;

public class MenuHandler {
    public static Intent menuOptionIntent(Context context, MenuItem item) {
        switch (item.getItemId()) {
            case R.id.action_competitor_list:
                Intent intent = new Intent();
                intent.setClass(context, CompetitorListActivity.class);
                return intent;
            default:
                return null;
        }
    }
}
