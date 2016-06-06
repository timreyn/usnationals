package org.cubingusa.usnationals;

import android.support.annotation.NonNull;
import android.util.JsonReader;

import java.io.IOException;
import java.util.Set;

public class Competitor implements Comparable<Competitor> {
    private final Set<String> mSavedCompetitors;
    public String name;
    public String wcaId;
    public String id;
    public String lowercaseName;
    public String lowercaseWcaId;

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
}
