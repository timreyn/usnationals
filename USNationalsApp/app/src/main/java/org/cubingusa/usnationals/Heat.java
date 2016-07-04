package org.cubingusa.usnationals;

import android.util.JsonReader;

import java.io.IOException;
import java.util.GregorianCalendar;

public class Heat {
    public Round round;
    // For convenience.  This is always round.event.
    public Event event;
    public Stage stage;
    public int number;
    public GregorianCalendar startTime;
    public GregorianCalendar endTime;

    public void parseFromJson(JsonReader reader) throws IOException{
        reader.beginObject();
        while (reader.hasNext()) {
            switch (reader.nextName()) {
                case "start_time":
                    startTime = parseTime(reader);
                    break;
                case "end_time":
                    endTime = parseTime(reader);
                    break;
                case "stage":
                    stage = new Stage();
                    stage.parseFromJson(reader);
                    break;
                case "round":
                    round = new Round();
                    round.parseFromJson(reader);
                    event = round.event;
                    break;
                case "number":
                    number = reader.nextInt();
                    break;
                default:
                    reader.skipValue();
            }
        }
        reader.endObject();
    }

    private GregorianCalendar parseTime(JsonReader reader) throws IOException {
        reader.beginObject();
        GregorianCalendar time = new GregorianCalendar();
        while (reader.hasNext()) {
            switch (reader.nextName()) {
                case "year":
                    time.set(GregorianCalendar.YEAR, reader.nextInt());
                    break;
                case "month":
                    time.set(GregorianCalendar.MONTH, reader.nextInt() - 1);
                    break;
                case "day":
                    time.set(GregorianCalendar.DAY_OF_MONTH, reader.nextInt());
                    break;
                case "hour":
                    time.set(GregorianCalendar.HOUR_OF_DAY, reader.nextInt());
                    break;
                case "minute":
                    time.set(GregorianCalendar.MINUTE, reader.nextInt());
                    break;
                default:
                    reader.skipValue();
            }
        }
        reader.endObject();
        return time;
    }
}
