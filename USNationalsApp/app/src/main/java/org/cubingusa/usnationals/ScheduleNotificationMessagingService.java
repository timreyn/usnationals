package org.cubingusa.usnationals;

import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.IBinder;
import android.support.v4.app.NotificationCompat;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

import java.util.HashMap;
import java.util.Map;

public class ScheduleNotificationMessagingService extends FirebaseMessagingService {
    private final EventIcons icons;
    private int nextNotificationId = 0;
    private Map<String, Integer> heatAssignmentToNotificationId = new HashMap<>();

    private NotificationManager notificationManager;

    public ScheduleNotificationMessagingService() {
        notificationManager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        icons = new EventIcons(this);
    }

    @Override
    public void onMessageReceived(RemoteMessage message) {
        if (message.getMessageType().equals("heatNotification")) {
            Map<String, String> data = message.getData();
            String heatAssignmentId = data.get("heatAssignmentId");
            String eventId = data.get("eventId");
            String eventName = data.get("eventName");
            String competitorName = data.get("competitorName");
            String competitorId = data.get("competitorId");
            int heatNumber = Integer.parseInt(data.get("heatNumber"));
            String stageName = data.get("stageName");

            StringBuffer titleBuffer = new StringBuffer()
                    .append(eventName)
                    .append(" on the ")
                    .append(stageName)
                    .append(" stage");

            StringBuffer contentBuffer = new StringBuffer()
                    .append("It's time for ")
                    .append(competitorName)
                    .append(" to compete in ")
                    .append(eventName)
                    .append(" heat ")
                    .append(heatNumber)
                    .append(" on the ")
                    .append(stageName)
                    .append(" stage!");

            Intent notificationClickIntent = new Intent();
            notificationClickIntent.setClass(this, ScheduleActivity.class);
            notificationClickIntent.putExtra(ScheduleActivity.COMPETITOR_EXTRA, competitorId);
            PendingIntent notificationClickPendingIntent =
                    PendingIntent.getActivity(
                            this,
                            0,
                            notificationClickIntent,
                            PendingIntent.FLAG_UPDATE_CURRENT);

            Uri ringtoneUri= RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
            NotificationCompat.Builder builder = new NotificationCompat.Builder(this)
                    .setContentTitle(titleBuffer.toString())
                    .setContentText(titleBuffer.toString())
                    .setSmallIcon(icons.getDrawableId(eventId))
                    .setAutoCancel(true)
                    .setContentIntent(notificationClickPendingIntent)
                    .setSound(ringtoneUri);

            heatAssignmentToNotificationId.put(heatAssignmentId, nextNotificationId);
            notificationManager.notify(nextNotificationId, builder.build());
            nextNotificationId++;
        } else if (message.getMessageType().equals("cancelHeatNotification")) {
            Map<String, String> data = message.getData();
            String heatAssignmentId = data.get("heatAssignmentId");
            if (!heatAssignmentToNotificationId.containsKey(heatAssignmentId)) {
                return;
            }
            notificationManager.cancel(heatAssignmentToNotificationId.get(heatAssignmentId));
        }
    }

}
