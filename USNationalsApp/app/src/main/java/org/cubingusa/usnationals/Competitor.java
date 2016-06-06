package org.cubingusa.usnationals;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.support.annotation.NonNull;
import android.util.JsonReader;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

public class Competitor implements Comparable<Competitor> {
    private Set<String> mSavedCompetitors;
    public String name;
    public String wcaId;
    public String id;
    public String lowercaseName;
    public String lowercaseWcaId;
    public ImageView saveIcon;

    public Competitor(Set<String> savedCompetitors) {
        this.mSavedCompetitors = savedCompetitors;
    }

    @Override
    public int compareTo(@NonNull Competitor other) {
        boolean isSaved = mSavedCompetitors.contains(id);
        boolean otherIsSaved = mSavedCompetitors.contains(other.id);
        if (isSaved && !otherIsSaved) {
            return -1;
        }
        if (!isSaved && otherIsSaved) {
            return 1;
        }
        return name.compareTo(other.name);
    }

    public void parseFromJson(JsonReader reader) throws IOException {
        reader.beginObject();
        while (reader.hasNext()) {
            switch (reader.nextName()) {
                case "wca_id":
                    wcaId = reader.nextString();
                    lowercaseWcaId = wcaId.toLowerCase();
                    break;
                case "id":
                    id = reader.nextString();
                    break;
                case "name":
                    name = reader.nextString();
                    lowercaseName = name.toLowerCase();
                    break;
                default:
                    reader.skipValue();
            }
        }
        reader.endObject();
    }
    public void addChipToLayout(
            final Context context, LayoutInflater inflater, LinearLayout container) {
        addChipToLayout(context, inflater, container, -1);
    }

    public void addChipToLayout(
            final Context context, LayoutInflater inflater, LinearLayout container, int number) {
        final SharedPreferences sharedPreferences =
                context.getSharedPreferences(Constants.PREFRENCES, Context.MODE_PRIVATE);

        inflater.inflate(
                R.layout.content_competitor_search_result, container);
        LinearLayout result = (LinearLayout) container.getChildAt(container.getChildCount() - 1);
        result.getChildAt(1).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent();
                intent.setClass(context, CompetitorScheduleActivity.class);
                intent.putExtra(CompetitorScheduleActivity.COMPETITOR_EXTRA, id);
                context.startActivity(intent);
            }
        });
        if (number != -1) {
            TextView competitorNumber = (TextView) result.getChildAt(0);
            competitorNumber.setText(number);
            competitorNumber.setVisibility(View.VISIBLE);
        }
        TextView competitorName = (TextView) result.getChildAt(1);
        competitorName.setText(name);
        final ImageView wcaIcon = (ImageView) result.getChildAt(2);
        if (wcaId.isEmpty()) {
            wcaIcon.setVisibility(View.GONE);
        } else {
            wcaIcon.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    Uri wcaUri = new Uri.Builder()
                            .scheme("https")
                            .authority(Constants.WCA_HOSTNAME)
                            .appendPath("results")
                            .appendPath("p.php")
                            .appendQueryParameter("i", wcaId)
                            .build();

                    Intent intent = new Intent(Intent.ACTION_VIEW, wcaUri);
                    context.startActivity(intent);
                }
            });
        }
        saveIcon = (ImageView) result.getChildAt(3);
        saveIcon.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mSavedCompetitors = sharedPreferences.getStringSet(
                        Constants.SAVED_COMPETITOR_PREFERENCE_KEY, new HashSet<String>());
                if (!mSavedCompetitors.contains(id)) {
                    mSavedCompetitors.add(id);
                    saveIcon.setImageResource(R.drawable.star);
                    Toast.makeText(context, R.string.saved_competitor, Toast.LENGTH_SHORT).show();
                } else {
                    mSavedCompetitors.remove(id);
                    saveIcon.setImageResource(R.drawable.star_outline);
                }
                sharedPreferences.edit()
                        .putStringSet(
                                Constants.SAVED_COMPETITOR_PREFERENCE_KEY, mSavedCompetitors)
                        .apply();
            }
        });
    }
}
