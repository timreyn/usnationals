package org.cubingusa.usnationals;

import android.util.JsonReader;

import java.io.IOException;
import java.util.Set;

public class StaffAssignment {
    private final Set<String> mSavedCompetitors;
    public Heat heat = null;
    public Round longEvent = null;
    public Competitor staffMember = null;
    public String job = "";
    public int station = -1;

    public StaffAssignment(Set<String> savedCompetitors) {
        mSavedCompetitors = savedCompetitors;
    }
    
    public void parseFromJson(JsonReader reader) throws IOException {
        reader.beginObject();
        while (reader.hasNext()) {
            switch (reader.nextName()) {
                case "heat":
                    heat = new Heat();
                    heat.parseFromJson(reader);
                    break;
                case "staff_member":
                    staffMember = new Competitor(mSavedCompetitors);
                    staffMember.parseFromJson(reader);
                    break;
                case "job":
                    job = reader.nextString();
                    break;
                case "station":
                    station = reader.nextInt();
                    break;
                case "long_event":
                    longEvent = new Round();
                    longEvent.parseFromJson(reader);
                    break;
                default:
                    reader.skipValue();
            }
        }
        reader.endObject();
    }
}
