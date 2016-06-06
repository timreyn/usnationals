package org.cubingusa.usnationals;

import android.util.JsonReader;

import java.io.IOException;

public class Event {
    public String name = "";
    public String id = "";
    public boolean isReal = true;

    public void parseFromJson(JsonReader reader) throws IOException {
        reader.beginObject();
        while (reader.hasNext()) {
            switch (reader.nextName()) {
                case "id":
                    id = reader.nextString();
                    break;
                case "name":
                    name = reader.nextString();
                    break;
                case "is_real":
                    isReal = reader.nextBoolean();
                    break;
                default:
                    reader.skipValue();
            }
        }
        reader.endObject();
    }
}
