package org.cubingusa.usnationals;

import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.JsonReader;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.webkit.WebView;
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
import java.util.HashSet;
import java.util.Set;

import cz.msebera.android.httpclient.Header;

public class CompetitorScheduleActivity extends AppCompatActivity {
    private static final String TAG = "CompetitorSchedule";

    public static final String COMPETITOR_EXTRA =
            "org.cubingusa.usnationals.COMPETITOR";

    private Competitor mCompetitor;
    private String mCompetitorId;
    private String mNotificationPreferenceKey;
    private ImageView mSaveIcon;
    private ImageView mNotificationIcon;
    private SharedPreferences mSharedPreferences;
    private TextView mScheduleOption;
    private TextView mResultsOption;
    private View mScroll;
    private WebView mResultsWebView;
    private boolean mResultsLoaded;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_schedule);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        Intent intent = getIntent();
        mSharedPreferences = getSharedPreferences(Constants.PREFRENCES, MODE_PRIVATE);
        final SharedPreferences.Editor editor = mSharedPreferences.edit();
        mCompetitorId = intent.getStringExtra(COMPETITOR_EXTRA);
        mNotificationPreferenceKey = "subscription_" + mCompetitorId;
        mNotificationIcon = (ImageView) findViewById(R.id.notification_button);
        mSaveIcon = (ImageView) findViewById(R.id.save_button);
        mScheduleOption = (TextView) findViewById(R.id.schedule_option);
        mResultsOption = (TextView) findViewById(R.id.results_option);
        mScroll = findViewById(R.id.schedule_scrollview);
        mResultsWebView = (WebView) findViewById(R.id.schedule_results_webview);
        mResultsWebView.getSettings().setJavaScriptEnabled(true);
        mResultsLoaded = false;

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

        mResultsOption.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!mResultsLoaded) {
                    Uri cubecompsUri = new Uri.Builder()
                            .scheme("https")
                            .authority(Constants.HOSTNAME)
                            .appendPath("cubecomps")
                            .appendPath(mCompetitorId)
                            .build();
                    Log.d(TAG, "Loading " + cubecompsUri.toString());
                    mResultsWebView.loadUrl(cubecompsUri.toString());
                    mResultsLoaded = true;
                }
                mResultsWebView.setVisibility(View.VISIBLE);
                mScroll.setVisibility(View.GONE);
                setActive(mResultsOption);
                setInactive(mScheduleOption);
            }
        });

        mScheduleOption.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mScroll.setVisibility(View.VISIBLE);
                mResultsWebView.setVisibility(View.GONE);
                setActive(mScheduleOption);
                setInactive(mResultsOption);
            }
        });

        Uri uri = new Uri.Builder()
                .scheme("http")
                .authority(Constants.HOSTNAME)
                .appendPath("get_schedule")
                .appendPath(mCompetitorId)
                .appendQueryParameter("hide_old", "1")
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

    private void setActive(TextView view) {
        view.setTypeface(null, Typeface.BOLD);
        view.setBackgroundResource(R.drawable.border_on_gray);
    }

    private void setInactive(TextView view) {
        view.setTypeface(null, Typeface.NORMAL);
        view.setBackgroundResource(R.drawable.border);
    }

    private String getTopic(String competitorId) {
        return "/topics/competitor_" + competitorId;
    }

    private void parseJson(byte[] responseBody) throws IOException {
        JsonReader reader = new JsonReader(new InputStreamReader(new ByteArrayInputStream(responseBody)));
        try {
            reader.beginObject();
            while (reader.hasNext()) {
                switch (reader.nextName()) {
                    case "competitor":
                        parseCompetitor(reader);
                        break;
                    case "groups":
                        parseGroups(reader);
                        break;
                    default:
                        reader.skipValue();
                }
            }
        } finally {
            reader.close();
        }
    }

    private void parseCompetitor(JsonReader reader) throws IOException {
        mCompetitor = new Competitor(mSharedPreferences.getStringSet(
                Constants.SAVED_COMPETITOR_PREFERENCE_KEY, new HashSet<String>()));
        mCompetitor.parseFromJson(reader);
        setTitle(mCompetitor.name);
    }

    private void parseGroups(JsonReader reader) throws IOException {
        reader.beginArray();
        LinearLayout scheduleContainer = (LinearLayout) findViewById(R.id.schedule_container);
        if (scheduleContainer == null) {
            reader.endArray();
            return;
        }
        ScheduleParser scheduleParser =
                new ScheduleParser(this, getLayoutInflater(), scheduleContainer);
        while (reader.hasNext()) {
            reader.beginObject();
            while (reader.hasNext()) {
                switch (reader.nextName()) {
                    case "competing":
                        scheduleParser.parseGroup(reader);
                        break;
                    case "staff":
                        scheduleParser.parseStaffAssignment(reader);
                        break;
                    default:
                        reader.skipValue();
                }
            }
            reader.endObject();
        }
        reader.endArray();
    }
}