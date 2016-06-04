package org.cubingusa.usnationals;

import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.JsonReader;
import android.util.Log;
import android.util.Pair;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.google.firebase.messaging.FirebaseMessaging;
import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.text.DateFormat;
import java.util.GregorianCalendar;
import java.util.HashSet;
import java.util.Set;

import cz.msebera.android.httpclient.Header;
import cz.msebera.android.httpclient.ParseException;

public class CompetitorScheduleActivity extends AppCompatActivity {
    private static final String TAG = "CompetitorSchedule";

    public static final String COMPETITOR_EXTRA = "COMPETITOR";

    private EventIcons mEventIcons;
    private String mCompetitorId;
    private String mNotificationPreferenceKey;
    private ImageView mSaveIcon;
    private ImageView mNotificationIcon;
    private SharedPreferences mSharedPreferences;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_schedule);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        Intent intent = getIntent();
        mEventIcons = new EventIcons(this);
        mSharedPreferences = getSharedPreferences(Constants.PREFRENCES, MODE_PRIVATE);
        final SharedPreferences.Editor editor = mSharedPreferences.edit();
        mCompetitorId = intent.getStringExtra(COMPETITOR_EXTRA);
        mNotificationPreferenceKey = "subscription_" + mCompetitorId;
        mNotificationIcon = (ImageView) findViewById(R.id.notification_button);
        mSaveIcon = (ImageView) findViewById(R.id.save_button);

        mNotificationIcon.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                boolean isSubscribed =
                        mSharedPreferences.getBoolean(mNotificationPreferenceKey, false);
                if (!isSubscribed) {
                    FirebaseMessaging.getInstance().subscribeToTopic(getTopic(mCompetitorId));
                    mNotificationIcon.setImageResource(R.drawable.bell);
                    Toast.makeText(CompetitorScheduleActivity.this,
                            R.string.subscribed, Toast.LENGTH_SHORT).show();
                } else {
                    FirebaseMessaging.getInstance().unsubscribeFromTopic(getTopic(mCompetitorId));
                    mNotificationIcon.setImageResource(R.drawable.bell_outline);
                }
                editor.putBoolean(mNotificationPreferenceKey, !isSubscribed);
                editor.apply();
            }
        });

        mSaveIcon.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Set<String> savedCompetitors = mSharedPreferences.getStringSet(
                        Constants.SAVED_COMPETITOR_PREFERENCE_KEY, new HashSet<String>());
                if (!savedCompetitors.contains(mCompetitorId)) {
                    savedCompetitors.add(mCompetitorId);
                    mSaveIcon.setImageResource(R.drawable.star);
                    Toast.makeText(CompetitorScheduleActivity.this,
                            R.string.saved_competitor, Toast.LENGTH_SHORT).show();
                } else {
                    savedCompetitors.remove(mCompetitorId);
                    mSaveIcon.setImageResource(R.drawable.star_outline);
                }
                editor.putStringSet(Constants.SAVED_COMPETITOR_PREFERENCE_KEY, savedCompetitors);
                editor.apply();
            }
        });

        Uri uri = new Uri.Builder()
                .scheme("http")
                .authority(Constants.HOSTNAME)
                .appendPath("get_schedule")
                .appendPath(mCompetitorId)
                .build();
        AsyncHttpClient client = new AsyncHttpClient();
        client.get(uri.toString(), new AsyncHttpResponseHandler() {
            @Override
            public void onSuccess(int statusCode, Header[] headers, byte[] responseBody) {
                LinearLayout layout = (LinearLayout) findViewById(R.id.schedule_container);
                if (layout != null) {
                    layout.removeAllViewsInLayout();
                }
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
    }

    @Override
    protected void onResume() {
        super.onResume();
        Set<String> savedCompetitors = mSharedPreferences.getStringSet(
                Constants.SAVED_COMPETITOR_PREFERENCE_KEY, new HashSet<String>());
        if (savedCompetitors.contains(mCompetitorId)) {
            mSaveIcon.setImageResource(R.drawable.star);
        } else {
            mSaveIcon.setImageResource(R.drawable.star_outline);
        }
        if (mSharedPreferences.getBoolean(mNotificationPreferenceKey, false)) {
            mNotificationIcon.setImageResource(R.drawable.bell);
        } else {
            mNotificationIcon.setImageResource(R.drawable.bell_outline);
        }
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

    private String getTopic(String competitorId) {
        return "/topics/competitor_" + competitorId;
    }

    private void parseJson(byte[] responseBody) throws IOException {
        JsonReader reader = new JsonReader(new InputStreamReader(new ByteArrayInputStream(responseBody)));
        try {
            reader.beginObject();
            while (reader.hasNext()) {
                String name = reader.nextName();
                if (name.equals("competitor")) {
                    parseCompetitor(reader);
                } else if (name.equals("heats")) {
                    parseHeats(reader);
                }
            }
        } finally {
            reader.close();
        }
    }

    private void parseCompetitor(JsonReader reader) throws IOException {
        reader.beginObject();
        while (reader.hasNext()) {
            String name = reader.nextName();
            if (name.equals("name")) {
                setTitle(reader.nextString());
            } else {
                reader.skipValue();
            }
        }
        reader.endObject();
    }

    private void parseHeats(JsonReader reader) throws IOException {
        reader.beginArray();
        LinearLayout scheduleContainer = (LinearLayout) findViewById(R.id.schedule_container);
        if (scheduleContainer == null) {
            reader.endArray();
            return;
        }
        int numHeatsAdded = 0;
        while (reader.hasNext()) {
            reader.beginObject();
            getLayoutInflater().inflate(
                    R.layout.content_schedule_item, scheduleContainer);
            LinearLayout scheduleItem = (LinearLayout) scheduleContainer.getChildAt(numHeatsAdded);
            TextView scheduleItemTime = (TextView) scheduleItem.getChildAt(0);
            ImageView scheduleItemIcon = (ImageView) scheduleItem.getChildAt(1);
            TextView scheduleItemName = (TextView) scheduleItem.getChildAt(2);
            String stageName = "";
            int heatNumber = 0;
            String eventName = "";
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
                        stageName = parseStage(reader, scheduleItem);
                        break;
                    case "round":
                        reader.beginObject();
                        Pair<String, String> eventIdAndName = parseRound(reader);
                        reader.endObject();
                        scheduleItemIcon.setImageDrawable(
                                mEventIcons.getDrawable(eventIdAndName.first));
                        eventName = eventIdAndName.second;
                        break;
                    case "number":
                        heatNumber = reader.nextInt();
                        break;
                    default:
                        reader.skipValue();
                }
            }
            StringBuilder builder = new StringBuilder();
            builder.append(eventName);
            builder.append(" ");
            if (!stageName.equals("")) {
                builder.append(stageName);
                builder.append(" ");
            }
            builder.append(heatNumber);
            scheduleItemName.setText(builder.toString());
            reader.endObject();
            numHeatsAdded++;
        }
        reader.endArray();
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