package org.cubingusa.usnationals;

import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.support.annotation.UiThread;
import android.support.design.widget.TextInputEditText;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.JsonReader;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.widget.ImageView;
import android.widget.LinearLayout;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import cz.msebera.android.httpclient.Header;

public class CompetitorListActivity extends AppCompatActivity {
    private static final String TAG = "CompetitorListActivity";
    private static final int MAX_COMPETITORS_TO_SHOW = 20;

    private static final Map<String, ImageView> mCompetitorIdToSaveIcon = new HashMap<>();
    private SharedPreferences mSharedPreferences;
    private ArrayList<Competitor> mCompetitors = new ArrayList<Competitor>();

    @Override
    protected void onCreate(final Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_competitor_list);
        setTitle(R.string.title_activity_competitor_list);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        Uri uri = new Uri.Builder()
                .scheme("http")
                .authority(Constants.HOSTNAME)
                .appendPath("get_competitors")
                .build();
        AsyncHttpClient client = new AsyncHttpClient();
        mSharedPreferences = getSharedPreferences(Constants.PREFRENCES, MODE_PRIVATE);
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
            public void onFailure(
                    int statusCode, Header[] headers, byte[] responseBody, Throwable error) {
                Log.e(TAG, error.toString());
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
        Set<String> savedCompetitors = mSharedPreferences.getStringSet(
                Constants.SAVED_COMPETITOR_PREFERENCE_KEY, new HashSet<String>());
        JsonReader reader = new JsonReader(new InputStreamReader(new ByteArrayInputStream(responseBody)));
        try {
            reader.beginArray();
            while (reader.hasNext()) {
                Competitor competitor = new Competitor(savedCompetitors);
                competitor.parseFromJson(reader);
                mCompetitors.add(competitor);
            }
        } finally {
            reader.close();
        }
        Collections.sort(mCompetitors);
        displayMatchingCompetitors();
        TextInputEditText textInput = (TextInputEditText) findViewById(R.id.competitor_input);
        if (textInput == null) {
            return;
        }
        textInput.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                displayMatchingCompetitors();
            }

            @Override
            public void afterTextChanged(Editable s) {}
        });
    }

    @UiThread
    private void displayMatchingCompetitors() {
        mCompetitorIdToSaveIcon.clear();
        TextInputEditText textInput = (TextInputEditText) findViewById(R.id.competitor_input);
        if (textInput == null) {
            return;
        }
        String[] searchQueryTerms = textInput.getText().toString().toLowerCase().split(" ");
        LinearLayout container = (LinearLayout) findViewById(R.id.search_result_container);
        if (container == null) {
            return;
        }
        container.removeAllViewsInLayout();
        if (searchQueryTerms.length == 0) {
            return;
        }
        int numCompetitorsAdded = 0;
        for (final Competitor competitor : mCompetitors) {
            if (numCompetitorsAdded >= MAX_COMPETITORS_TO_SHOW) {
                break;
            }
            boolean matchesSearch = true;
            for (String searchTerm : searchQueryTerms) {
                if (!competitor.lowercaseName.contains(searchTerm) &&
                        !competitor.lowercaseWcaId.contains(searchTerm)) {
                    matchesSearch = false;
                    break;
                }
            }
            if (matchesSearch) {
                competitor.addChipToLayout(this, getLayoutInflater(), container);
                mCompetitorIdToSaveIcon.put(competitor.id, competitor.saveIcon);
                numCompetitorsAdded++;
            }
        }
        updateSaveIcons();
    }
}
