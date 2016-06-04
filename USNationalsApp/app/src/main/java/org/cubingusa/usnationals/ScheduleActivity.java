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
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.google.firebase.messaging.FirebaseMessaging;
import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.text.SimpleDateFormat;
import java.util.GregorianCalendar;
import java.util.HashSet;
import java.util.Set;

import cz.msebera.android.httpclient.Header;
import cz.msebera.android.httpclient.ParseException;

public class ScheduleActivity extends AppCompatActivity {
    private static final String TAG = "ScheduleActivity";

    public static final String COMPETITOR_EXTRA = "COMPETITOR";

    private EventIcons eventIcons;
    private String competitorId;
    private String notificationPreferenceKey;
    private ImageView saveIcon;
    private ImageView notificationIcon;
    private SharedPreferences preferences;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_schedule);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        Intent intent = getIntent();
        eventIcons = new EventIcons(this);
        preferences = getSharedPreferences(Constants.PREFRENCES, MODE_PRIVATE);
        final SharedPreferences.Editor editor = preferences.edit();
        competitorId = intent.getStringExtra(COMPETITOR_EXTRA);
        notificationPreferenceKey = "subscription_" + competitorId;
        notificationIcon = (ImageView) findViewById(R.id.notification_button);
        saveIcon = (ImageView) findViewById(R.id.save_button);

        notificationIcon.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                boolean isSubscribed = preferences.getBoolean(notificationPreferenceKey, false);
                if (!isSubscribed) {
                    FirebaseMessaging.getInstance().subscribeToTopic(getTopic(competitorId));
                    notificationIcon.setImageResource(R.drawable.bell);
                } else {
                    FirebaseMessaging.getInstance().unsubscribeFromTopic(getTopic(competitorId));
                    notificationIcon.setImageResource(R.drawable.bell_outline);
                }
                editor.putBoolean(notificationPreferenceKey, isSubscribed);
                editor.apply();
            }
        });

        saveIcon.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Set<String> savedCompetitors = preferences.getStringSet(
                        Constants.SAVED_COMPETITOR_PREFERENCE_KEY, new HashSet<String>());
                if (!savedCompetitors.contains(competitorId)) {
                    savedCompetitors.add(competitorId);
                    saveIcon.setImageResource(R.drawable.star);
                } else {
                    savedCompetitors.remove(competitorId);
                    saveIcon.setImageResource(R.drawable.star_outline);
                }
                editor.putStringSet(Constants.SAVED_COMPETITOR_PREFERENCE_KEY, savedCompetitors);
                editor.apply();
            }
        });

        Uri uri = new Uri.Builder()
                .scheme("http")
                .authority(Constants.HOSTNAME)
                .appendPath("get_schedule")
                .appendPath(competitorId)
                .build();
        AsyncHttpClient client = new AsyncHttpClient();
        client.get(uri.toString(), new AsyncHttpResponseHandler() {
            @Override
            public void onSuccess(int statusCode, Header[] headers, byte[] responseBody) {
                try {
                    parseJson(responseBody);
                } catch (IOException e) {
                    Log.e(TAG, e.toString());
                }
            }

            @Override
            public void onFailure(int statusCode, Header[] headers, byte[] responseBody, Throwable error) {
                Log.e(TAG, error.toString());
            }
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        Set<String> savedCompetitors = preferences.getStringSet(
                Constants.SAVED_COMPETITOR_PREFERENCE_KEY, new HashSet<String>());
        if (savedCompetitors.contains(competitorId)) {
            saveIcon.setImageResource(R.drawable.star);
        } else {
            saveIcon.setImageResource(R.drawable.star_outline);
        }
        if (preferences.getBoolean(notificationPreferenceKey, false)) {
            notificationIcon.setImageResource(R.drawable.bell);
        } else {
            notificationIcon.setImageResource(R.drawable.bell_outline);
        }
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
        int numHeatsAdded = 0;
        while (reader.hasNext()) {
            reader.beginObject();
            getLayoutInflater().inflate(
                    R.layout.content_schedule_item, scheduleContainer);
            LinearLayout schedule_item = (LinearLayout) scheduleContainer.getChildAt(numHeatsAdded);
            TextView schedule_item_time = (TextView) schedule_item.getChildAt(0);
            ImageView schedule_item_icon = (ImageView) schedule_item.getChildAt(1);
            TextView schedule_item_name = (TextView) schedule_item.getChildAt(2);
            String stage_name = "";
            int heat_number = 0;
            String event_name = "";
            while (reader.hasNext()) {
                String name = reader.nextName();
                if (name.equals("start_time")) {
                    GregorianCalendar time = parseTime(reader);
                    SimpleDateFormat format = new SimpleDateFormat("h:mm a");
                    try {
                        schedule_item_time.setText(format.format(time.getTime()));
                    } catch (ParseException e) {
                        Log.e(TAG, e.toString());
                    }
                } else if (name.equals("stage")) {
                    stage_name = parseStage(reader, schedule_item);
                } else if (name.equals("round")) {
                    reader.beginObject();
                    while (reader.hasNext()) {
                        name = reader.nextName();
                        if (name.equals("event")) {
                            reader.beginObject();
                            while (reader.hasNext()) {
                                name = reader.nextName();
                                if (name.equals("id")) {
                                    String eventId = reader.nextString();
                                    schedule_item_icon.setImageDrawable(eventIcons.getDrawable(
                                            eventId));
                                } else if (name.equals("name")) {
                                    event_name = reader.nextString();
                                } else {
                                    reader.skipValue();
                                }
                            }
                            reader.endObject();
                        } else {
                            reader.skipValue();
                        }
                    }
                    reader.endObject();
                } else if (name.equals("number")) {
                    heat_number = reader.nextInt();
                } else {
                    reader.skipValue();
                }
            }
            StringBuffer buffer = new StringBuffer();
            buffer.append(event_name);
            buffer.append(" ");
            if (!stage_name.equals("")) {
                buffer.append(stage_name);
                buffer.append(" ");
            }
            buffer.append(heat_number);
            schedule_item_name.setText(buffer.toString());
            reader.endObject();
            numHeatsAdded++;
        }
        reader.endArray();
    }

    private GregorianCalendar parseTime(JsonReader reader) throws IOException {
        reader.beginObject();
        GregorianCalendar time = new GregorianCalendar();
        while (reader.hasNext()) {
            String name = reader.nextName();
            if (name.equals("year")) {
                time.set(GregorianCalendar.YEAR, reader.nextInt());
            } else if (name.equals("month")) {
                time.set(GregorianCalendar.MONTH, reader.nextInt());
            } else if (name.equals("day")) {
                time.set(GregorianCalendar.DAY_OF_MONTH, reader.nextInt());
            } else if (name.equals("hour")) {
                time.set(GregorianCalendar.HOUR_OF_DAY, reader.nextInt());
            } else if (name.equals("minute")) {
                time.set(GregorianCalendar.MINUTE, reader.nextInt());
            } else {
                reader.skipValue();
            }
        }
        reader.endObject();
        return time;
    }

    private String parseStage(JsonReader reader, LinearLayout layout) throws IOException {
        reader.beginObject();
        String stage_name = "";
        while (reader.hasNext()) {
            String name = reader.nextName();
            if (name.equals("color_hex")) {
                layout.setBackgroundColor(Color.parseColor(reader.nextString()));
            } else if (name.equals("name")) {
                stage_name = reader.nextString();
            } else {
                reader.skipValue();
            }
        }
        reader.endObject();
        return stage_name;
    }
}
