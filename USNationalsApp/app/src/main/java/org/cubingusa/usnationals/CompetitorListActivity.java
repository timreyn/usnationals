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
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

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

    private SharedPreferences.Editor editor;
    private static final Map<String, ImageView> competitorIdToSaveIcon = new HashMap<>();
    private SharedPreferences sharedPreferences;

    private class Competitor implements Comparable<Competitor> {
        private final Set<String> savedCompetitors;
        public String name;
        public String wcaId;
        public String id;
        public String lowercaseName;
        public String lowercaseWcaId;

        public Competitor(Set<String> savedCompetitors) {
            this.savedCompetitors = savedCompetitors;
        }

        @Override
        public int compareTo(Competitor other) {
            boolean isSaved = savedCompetitors.contains(id);
            boolean otherIsSaved = savedCompetitors.contains(other.id);
            if (isSaved && !otherIsSaved) {
                return -1;
            }
            if (!isSaved && otherIsSaved) {
                return 1;
            }
            return name.compareTo(other.name);
        }
    }

    private ArrayList<Competitor> competitors = new ArrayList<Competitor>();

    @Override
    protected void onCreate(final Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_competitor_list);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        Uri uri = new Uri.Builder()
                .scheme("http")
                .authority(Constants.HOSTNAME)
                .appendPath("get_competitors")
                .build();
        AsyncHttpClient client = new AsyncHttpClient();
        sharedPreferences = getSharedPreferences(Constants.PREFRENCES, MODE_PRIVATE);

        editor = sharedPreferences.edit();
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

    void updateSaveIcons() {
        Set<String> savedCompetitors = sharedPreferences.getStringSet(
                Constants.SAVED_COMPETITOR_PREFERENCE_KEY, new HashSet<String>());
        for (String competitor : competitorIdToSaveIcon.keySet()) {
            if (savedCompetitors.contains(competitor)) {
                competitorIdToSaveIcon.get(competitor)
                        .setImageResource(R.drawable.star);
            } else {
                competitorIdToSaveIcon.get(competitor)
                        .setImageResource(R.drawable.star_outline);
            }
        }
    }

    @UiThread
    private void parseJson(byte[] responseBody) throws IOException {
        Set<String> savedCompetitors = sharedPreferences.getStringSet(
                Constants.SAVED_COMPETITOR_PREFERENCE_KEY, new HashSet<String>());
        JsonReader reader = new JsonReader(new InputStreamReader(new ByteArrayInputStream(responseBody)));
        try {
            reader.beginArray();
            while (reader.hasNext()) {
                reader.beginObject();
                Competitor competitor = new Competitor(savedCompetitors);
                while (reader.hasNext()) {
                    String name = reader.nextName();
                    if (name.equals("wca_id")) {
                        competitor.wcaId = reader.nextString();
                        competitor.lowercaseWcaId = competitor.wcaId.toLowerCase();
                    } else if (name.equals("id")) {
                        competitor.id = reader.nextString();
                    } else if (name.equals("name")) {
                        competitor.name = reader.nextString();
                        competitor.lowercaseName = competitor.name.toLowerCase();
                    } else {
                        reader.skipValue();
                    }
                }
                competitors.add(competitor);
                reader.endObject();
            }
        } finally {
            reader.close();
        }
        Collections.sort(competitors);
        displayMatchingCompetitors();
        TextInputEditText textInput = (TextInputEditText) findViewById(R.id.competitor_input);
        textInput.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
                return;
            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                displayMatchingCompetitors();
            }

            @Override
            public void afterTextChanged(Editable s) {
                return;
            }
        });
    }

    @UiThread
    private void displayMatchingCompetitors() {
        competitorIdToSaveIcon.clear();
        final Set<String> savedCompetitors = sharedPreferences.getStringSet(
                Constants.SAVED_COMPETITOR_PREFERENCE_KEY, new HashSet<String>());
        TextInputEditText textInput = (TextInputEditText) findViewById(R.id.competitor_input);
        String[] searchQueryTerms = textInput.getText().toString().toLowerCase().split(" ");
        LinearLayout container = (LinearLayout) findViewById(R.id.search_result_container);
        container.removeAllViewsInLayout();
        if (searchQueryTerms.length == 0) {
            return;
        }
        int numCompetitorsAdded = 0;
        for (final Competitor competitor : competitors) {
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
                getLayoutInflater().inflate(
                        R.layout.content_competitor_search_result, container);
                LinearLayout result = (LinearLayout) container.getChildAt(numCompetitorsAdded);
                result.getChildAt(0).setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        Intent intent = new Intent();
                        intent.setClass(CompetitorListActivity.this, ScheduleActivity.class);
                        intent.putExtra(ScheduleActivity.COMPETITOR_EXTRA, competitor.id);
                        startActivity(intent);
                    }
                });
                TextView competitorName = (TextView) result.getChildAt(0);
                competitorName.setText(competitor.name);
                final ImageView saveIcon = (ImageView) result.getChildAt(1);
                competitorIdToSaveIcon.put(competitor.id, saveIcon);
                saveIcon.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        if (!savedCompetitors.contains(competitor.id)) {
                            savedCompetitors.add(competitor.id);
                            saveIcon.setImageResource(R.drawable.star);
                        } else {
                            savedCompetitors.remove(competitor.id);
                            saveIcon.setImageResource(R.drawable.star_outline);
                        }
                        editor.putStringSet(
                                Constants.SAVED_COMPETITOR_PREFERENCE_KEY, savedCompetitors);
                        editor.apply();
                    }
                });
                numCompetitorsAdded++;
            }
        }
        updateSaveIcons();
    }
}
