package org.cubingusa.usnationals;

import android.util.JsonReader;

import java.io.IOException;

public class Round {
    public Event event = new Event();
    public int number = 0;
    public boolean isFinal = false;

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
                default:
                    reader.skipValue();
            }
        }
        reader.endObject();
    }
}
