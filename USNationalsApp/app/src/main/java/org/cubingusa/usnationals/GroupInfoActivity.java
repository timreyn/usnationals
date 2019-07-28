package org.cubingusa.usnationals;

import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import androidx.annotation.UiThread;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import android.util.JsonReader;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;
import com.loopj.android.http.RequestParams;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

import cz.msebera.android.httpclient.Header;

public class GroupInfoActivity extends AppCompatActivity {
    private static final String TAG = "GroupInfoActivity";

    public static final String EVENT_ID_EXTRA =
            "org.cubingusa.usnationals.EVENT_ID";
    public static final String ROUND_ID_EXTRA =
            "org.cubingusa.usnationals.ROUND_ID";
    public static final String STAGE_ID_EXTRA =
            "org.cubingusa.usnationals.STAGE_ID";
    public static final String GROUP_ID_EXTRA =
            "org.cubingusa.usnationals.GROUP_ID";

    private static final Map<String, ImageView> mCompetitorIdToSaveIcon = new HashMap<>();
    private SharedPreferences mSharedPreferences;
    private List<Competitor> mCompetitors = new ArrayList<>();
    private List<Competitor> mJudges = new ArrayList<>();
    private List<Competitor> mScramblers = new ArrayList<>();
    private List<Competitor> mRunners = new ArrayList<>();
    private Group mGroup;
    private LinearLayout mContainer;
    private TextView mStartTime;
    private AsyncHttpClient mClient;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_group_info);
        mContainer = (LinearLayout) findViewById(R.id.group_info_content);
        mStartTime = (TextView) findViewById(R.id.group_info_start_time);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        mCompetitors = new ArrayList<>();

        final Intent intent = getIntent();

        Uri uri = new Uri.Builder()
                .scheme("https")
                .authority(Constants.HOSTNAME)
                .appendPath("get_group_info")
                .appendPath(intent.getStringExtra(EVENT_ID_EXTRA))
                .appendPath(Integer.toString(intent.getIntExtra(ROUND_ID_EXTRA, 1)))
                .appendPath(intent.getStringExtra(STAGE_ID_EXTRA))
                .appendPath(intent.getStringExtra(GROUP_ID_EXTRA))
                .build();
        mClient = new AsyncHttpClient();
        mSharedPreferences = getSharedPreferences(Constants.PREFRENCES, MODE_PRIVATE);

        mClient.get(uri.toString(), new AsyncHttpResponseHandler() {
            @Override
            public void onSuccess(int statusCode, Header[] headers, byte[] responseBody) {
                try {
                    parseJson(responseBody);
                } catch (IOException e) {
                    Log.e(TAG, e.toString());
                }
            }

            @Override
            public void onFailure(
                    int statusCode, Header[] headers, byte[] responseBody, Throwable error) {
                Log.e(TAG, error.toString());
            }
        });

        if (mSharedPreferences.getInt(Constants.ADMIN_STATUS_PREFERENCE_KEY,
                Constants.ADMIN_STATUS_NOT_REQUESTED) == Constants.ADMIN_STATUS_GRANTED) {
            View notificationButton = findViewById(R.id.notification_button);
            if (notificationButton != null) {
                notificationButton.setVisibility(View.VISIBLE);
                notificationButton.setOnClickListener(
                        new View.OnClickListener() {
                            @Override
                            public void onClick(View v) {
                                new AlertDialog.Builder(GroupInfoActivity.this)
                                        .setTitle("Confirm")
                                        .setMessage("Are you sure that you want to call this group?")
                                        .setPositiveButton("Yes", new DialogInterface.OnClickListener() {
                                            @Override
                                            public void onClick(DialogInterface dialog, int which) {
                                                callGroup();
                                            }
                                        })
                                        .setNegativeButton("No", null)
                                        .show();
                            }
                        });
            }
        }
    }

    private void callGroup() {
        Intent intent = getIntent();
        Uri uri = new Uri.Builder()
                .scheme("https")
                .authority(Constants.HOSTNAME)
                .appendPath("send_notification")
                .appendPath(intent.getStringExtra(EVENT_ID_EXTRA))
                .appendPath(Integer.toString(intent.getIntExtra(ROUND_ID_EXTRA, 1)))
                .appendPath(intent.getStringExtra(STAGE_ID_EXTRA))
                .appendPath(intent.getStringExtra(GROUP_ID_EXTRA))
                .build();
        RequestParams params = new RequestParams();
        params.add("device_id", DeviceId.getDeviceId(mSharedPreferences));
        mClient.post(uri.toString(), params, new AsyncHttpResponseHandler() {
            @Override
            public void onSuccess(
                    int statusCode, Header[] headers, byte[] responseBody) {
                Toast.makeText(GroupInfoActivity.this,
                        R.string.successfully_notified,
                        Toast.LENGTH_SHORT).show();
            }

            @Override
            public void onFailure(
                    int statusCode, Header[] headers, byte[] responseBody,
                    Throwable error) {
                String response = "null";
                if (responseBody != null) {
                    response = new String(responseBody);
                }
                Toast.makeText(GroupInfoActivity.this,
                        getString(R.string.unsuccessful_notification, response),
                        Toast.LENGTH_SHORT).show();
            }
        });
    }


    @Override
    protected void onResume() {
        super.onResume();
        updateSaveIcons();
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        Intent intent = MenuHandler.menuOptionIntent(this, item);
        if (intent == null) {
            return super.onOptionsItemSelected(item);
        }
        startActivity(intent);
        return true;
    }

    void updateSaveIcons() {
        Set<String> savedCompetitors = mSharedPreferences.getStringSet(
                Constants.SAVED_COMPETITOR_PREFERENCE_KEY, new HashSet<String>());
        for (String competitor : mCompetitorIdToSaveIcon.keySet()) {
            if (savedCompetitors.contains(competitor)) {
                mCompetitorIdToSaveIcon.get(competitor)
                        .setImageResource(R.drawable.star);
            } else {
                mCompetitorIdToSaveIcon.get(competitor)
                        .setImageResource(R.drawable.star_outline);
            }
        }
    }

    @UiThread
    private void parseJson(byte[] responseBody) throws IOException {
        JsonReader reader = new JsonReader(
                new InputStreamReader(new ByteArrayInputStream(responseBody)));
        try {
            reader.beginObject();
            while (reader.hasNext()) {
                switch (reader.nextName()) {
                    case "group":
                        mGroup = new Group();
                        mGroup.parseFromJson(reader);
                        break;
                    case "competitors":
                        parseCompetitors(reader);
                        break;
                    case "staff":
                        parseStaff(reader);
                        break;
                    default:
                        reader.skipValue();
                }
            }
            reader.endObject();
        } finally {
            reader.close();
        }
        Collections.sort(mCompetitors);

        View spinner = findViewById(R.id.group_info_spinner);
        if (spinner != null) {
            spinner.setVisibility(View.GONE);
        }
        if (mGroup.round.isFinal) {
            setTitle(getString(R.string.group_info_header_final,
                    mGroup.event.name, mGroup.stage.name, mGroup.number));
        } else {
            setTitle(getString(R.string.group_info_header_nonfinal,
                    mGroup.event.name, mGroup.round.number, mGroup.stage.name, mGroup.number));
        }
        DateFormat format = DateFormat.getTimeInstance(DateFormat.SHORT);
        mStartTime.setText(getString(R.string.group_info_start_time,
                mGroup.startTime.getDisplayName(
                        Calendar.DAY_OF_WEEK, Calendar.LONG, Locale.getDefault()),
                format.format(mGroup.startTime.getTime())));

        mContainer.removeAllViewsInLayout();

        showCompetitors(mCompetitors, getString(R.string.competitors_divider));
        showJudges(mJudges, getString(R.string.judges_divider));
        showCompetitors(mScramblers, getString(R.string.scramblers_divider));
        showCompetitors(mRunners, getString(R.string.runners_divider));
        //showOtherStaff();
        updateSaveIcons();
    }

    @UiThread
    private void parseCompetitors(JsonReader reader) throws IOException {
        final Set<String> savedCompetitors = mSharedPreferences.getStringSet(
                Constants.SAVED_COMPETITOR_PREFERENCE_KEY, new HashSet<String>());
        reader.beginArray();
        while (reader.hasNext()) {
            Competitor competitor = new Competitor(savedCompetitors);
            competitor.parseFromJson(reader);
            mCompetitors.add(competitor);
        }
        reader.endArray();
        Collections.sort(mCompetitors);
    }

    @UiThread
    private void parseStaff(JsonReader reader) throws IOException {
        final Set<String> savedCompetitors = mSharedPreferences.getStringSet(
                Constants.SAVED_COMPETITOR_PREFERENCE_KEY, new HashSet<String>());
        reader.beginArray();
        while (reader.hasNext()) {
            StaffAssignment staffAssignment = new StaffAssignment(savedCompetitors);
            staffAssignment.parseFromJson(reader);
            switch (staffAssignment.job) {
                case "J":
                    if (staffAssignment.station < 0) break;
                    while (mJudges.size() < staffAssignment.station) {
                        mJudges.add(new Competitor(savedCompetitors));
                    }
                    mJudges.set(staffAssignment.station - 1, staffAssignment.staffMember);
                    break;
                case "S":
                    mScramblers.add(staffAssignment.staffMember);
                    break;
                case "R":
                    mRunners.add(staffAssignment.staffMember);
                    break;
            }
        }
        reader.endArray();
    }

    @UiThread
    private void showCompetitors(List<Competitor> competitors, String title) {
        if (competitors.isEmpty()) {
            return;
        }
        Util.addDivider(title, getLayoutInflater(), mContainer);

        for (Competitor competitor : competitors) {
            competitor.addChipToLayout(this, getLayoutInflater(), mContainer);
            mCompetitorIdToSaveIcon.put(competitor.id, competitor.saveIcon);
        }
    }

    @UiThread
    private void showJudges(List<Competitor> judges, String title) {
        if (judges.isEmpty()) {
            return;
        }
        Util.addDivider(title, getLayoutInflater(), mContainer);

        for (int i = 0; i < judges.size(); ++i) {
            Competitor judge = judges.get(i);
            judge.addChipToLayout(this, getLayoutInflater(), mContainer, i + 1);
            mCompetitorIdToSaveIcon.put(judge.id, judge.saveIcon);
        }
    }
}
