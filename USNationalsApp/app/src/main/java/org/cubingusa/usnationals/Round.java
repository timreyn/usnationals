package org.cubingusa.usnationals;

import android.util.JsonReader;

import java.io.IOException;

public class Round {
    public Event event = new Event();
    public int number = 0;
    public boolean isFinal = false;
    public String id = "";

    public void parseFromJson(JsonReader reader) throws IOException {
        reader.beginObject();
        while (reader.hasNext()) {
            switch (reader.nextName()) {
                case "event":
                    event.parseFromJson(reader);
                    break;
                case "number":
                    number = reader.nextInt();
                    break;
                case "is_final":
                    isFinal = reader.nextBoolean();
                    break;
                case "id":
                    id = reader.nextString();
                    break;
                default:
                    reader.skipValue();
            }
        }
        reader.endObject();
    }
}
