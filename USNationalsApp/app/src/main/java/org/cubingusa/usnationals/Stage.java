package org.cubingusa.usnationals;

import android.graphics.Color;
import android.util.JsonReader;

import java.io.IOException;

public class Stage {
    public String id = "";
    public String name = "";
    public int color = 0;

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
                case "color_hex":
                    color = Color.parseColor(reader.nextString());
                    break;
                default:
                    reader.skipValue();
            }
        }
        reader.endObject();
    }
}
