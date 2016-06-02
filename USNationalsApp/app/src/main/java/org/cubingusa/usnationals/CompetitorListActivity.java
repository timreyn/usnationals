package org.cubingusa.usnationals;

import android.content.Intent;
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
import android.widget.LinearLayout;
import android.widget.TextView;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;

import cz.msebera.android.httpclient.Header;

public class CompetitorListActivity extends AppCompatActivity {

    // TODO: move this to shared preferences
    private static final String HOSTNAME = "usnationals2016.appspot.com";
    private static final String TAG = "CompetitorListActivity";
    private static final int MAX_COMPETITORS_TO_SHOW = 20;

    private class Competitor {
        public String name;
        public String wcaId;
        public String id;
    }

    private ArrayList<Competitor> competitors = new ArrayList<Competitor>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_competitor_list);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        Uri uri = new Uri.Builder()
                .scheme("http")
                .authority(HOSTNAME)
                .appendPath("get_competitors")
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

    private void parseJson(byte[] responseBody) throws IOException {
        JsonReader reader = new JsonReader(new InputStreamReader(new ByteArrayInputStream(responseBody)));
        try {
            reader.beginArray();
            while (reader.hasNext()) {
                reader.beginObject();
                Competitor competitor = new Competitor();
                while (reader.hasNext()) {
                    String name = reader.nextName();
                    if (name.equals("wca_id")) {
                        competitor.wcaId = reader.nextString();
                    } else if (name.equals("id")) {
                        competitor.id = reader.nextString();
                    } else if (name.equals("name")) {
                        competitor.name = reader.nextString();
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
        TextInputEditText textInput = (TextInputEditText) findViewById(R.id.competitor_input);
        String[] searchQueryTerms = textInput.getText().toString().split(" ");
        LinearLayout container = (LinearLayout) findViewById(R.id.search_result_container);
        container.removeAllViewsInLayout();
        if (searchQueryTerms.length == 0) {
            return;
        }
        int numCompetitorsAdded = 0;
        for (final Competitor competitor : competitors) {
            boolean matchesSearch = true;
            for (String searchTerm : searchQueryTerms) {
                if (!competitor.name.contains(searchTerm) &&
                        !competitor.wcaId.contains(searchTerm)) {
                    matchesSearch = false;
                    break;
                }
            }
            if (matchesSearch) {
                getLayoutInflater().inflate(
                        R.layout.content_competitor_search_result, container);
                LinearLayout result = (LinearLayout) container.getChildAt(numCompetitorsAdded);
                result.setOnClickListener(new View.OnClickListener() {
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
                numCompetitorsAdded++;
                if (numCompetitorsAdded >= MAX_COMPETITORS_TO_SHOW) {
                    return;
                }
            }
        }
    }
}
