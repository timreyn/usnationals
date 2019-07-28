package org.cubingusa.usnationals;

import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.media.RingtoneManager;
import android.net.Uri;
import androidx.core.app.NotificationCompat;
import android.util.Log;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

import java.util.HashMap;
import java.util.Map;

public class ScheduleNotificationMessagingService extends FirebaseMessagingService {
    private static final String TAG = "NotificationService";
    private final EventIcons mIcons;
    private int mNextNotificationId = 0;
    private Map<String, Integer> mGroupAssignmentToNotificationId = new HashMap<>();

    private NotificationManager mNotificationManager;

    public ScheduleNotificationMessagingService() {
        mIcons = new EventIcons(this);
    }

    @Override
    public void onMessageReceived(RemoteMessage message) {
        mNotificationManager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);

        Map<String, String> data = message.getData();
        Log.i(TAG, "Message received of type " + data.get("type"));

        SharedPreferences preferences =
                getSharedPreferences(Constants.PREFRENCES, MODE_PRIVATE);
        boolean enableNotifications = true;

        switch (data.get("type")) {
            case "groupNotification":
                String groupAssignmentId = data.get("groupAssignmentId");
                String eventId = data.get("eventId");
                String eventName = data.get("eventName");
                String competitorName = data.get("competitorName");
                String competitorId = data.get("competitorId");
                String groupNumber = data.get("groupNumber");
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
                        .append(" group ")
                        .append(groupNumber)
                        .append(" on the ")
                        .append(stageName)
                        .append(" stage!");

                Intent notificationClickIntent = new Intent();
                notificationClickIntent.setClass(this, CompetitorScheduleActivity.class);
                notificationClickIntent.putExtra(CompetitorScheduleActivity.COMPETITOR_EXTRA, competitorId);
                PendingIntent notificationClickPendingIntent =
                        PendingIntent.getActivity(
                                this,
                                0,
                                notificationClickIntent,
                                PendingIntent.FLAG_UPDATE_CURRENT);

                Uri ringtoneUri= RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
                Bitmap largeIcon = BitmapFactory.decodeResource(
                        getResources(), mIcons.getDrawableId(eventId));
                NotificationCompat.Builder builder = new NotificationCompat.Builder(this, NotificationUtils.CHANNEL_ID)
                        .setContentTitle(titleBuffer.toString())
                        .setContentText(contentBuffer.toString())
                        .setSmallIcon(mIcons.getTransparentDrawableId(eventId))
                        .setLargeIcon(largeIcon)
                        .setAutoCancel(true)
                        .setContentIntent(notificationClickPendingIntent)
                        .setSound(ringtoneUri);

                mGroupAssignmentToNotificationId.put(groupAssignmentId, mNextNotificationId);
                if (enableNotifications) {
                    mNotificationManager.notify(mNextNotificationId, builder.build());
                }
                mNextNotificationId++;
                break;

            case "cancelGroupNotification":
                String groupAssignment = data.get("groupAssignmentId");
                if (!mGroupAssignmentToNotificationId.containsKey(groupAssignment)) {
                    return;
                }
                if (enableNotifications) {
                    mNotificationManager.cancel(
                            mGroupAssignmentToNotificationId.get(groupAssignment));
                }
                break;

            case "adminStatus":
                boolean isAdmin = data.get("isAdmin").equals("1");
                if (!DeviceId.getDeviceId(preferences).equals(data.get("deviceId"))) {
                    return;
                }
                if (isAdmin) {
                    preferences.edit()
                            .putInt(Constants.ADMIN_STATUS_PREFERENCE_KEY,
                                    Constants.ADMIN_STATUS_GRANTED)
                            .putString(Constants.ADMIN_NAME_PREFERENCE_KEY,
                                    data.get("competitorName"))
                            .apply();
                } else {
                    preferences.edit()
                            .putInt(Constants.ADMIN_STATUS_PREFERENCE_KEY,
                                    Constants.ADMIN_STATUS_NOT_REQUESTED)
                            .apply();
                    DeviceId.revokeDeviceId(preferences);
                }
                break;

            case "staffNotification":
                String staffAssignmentId = data.get("staffAssignmentId");
                if (data.containsKey("eventId")) {
                    eventId = data.get("eventId");
                } else {
                    eventId = "333";
                }
                competitorName = data.get("competitorName");
                competitorId = data.get("competitorId");
                stageName = data.get("stageName");
                String jobName = data.get("jobName");
                String jobId = data.get("jobId");


                String location = "";
                switch (jobId) {
                    case "J":
                    case "S":
                    case "R":
                        location = new StringBuffer().append(" on the ")
                                .append(stageName)
                                .append(" stage")
                                .toString();
                        break;
                    case "L":
                    case "U":
                        location = " in the long room";
                        break;
                }
                titleBuffer = new StringBuffer()
                        .append(jobName)
                        .append(location)
                        .append("!");

                contentBuffer = new StringBuffer()
                        .append("It's time for ")
                        .append(competitorName)
                        .append(" to ")
                        .append(jobName);
                if (data.containsKey("station")) {
                    contentBuffer.append(" station ")
                            .append(data.get("station"));
                }
                contentBuffer.append(location)
                        .append("!");

                notificationClickIntent = new Intent();
                notificationClickIntent.setClass(this, CompetitorScheduleActivity.class);
                notificationClickIntent.putExtra(CompetitorScheduleActivity.COMPETITOR_EXTRA, competitorId);
                notificationClickPendingIntent =
                        PendingIntent.getActivity(
                                this,
                                0,
                                notificationClickIntent,
                                PendingIntent.FLAG_UPDATE_CURRENT);

                ringtoneUri= RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
                largeIcon = BitmapFactory.decodeResource(
                        getResources(), mIcons.getDrawableId(eventId));
                builder = new NotificationCompat.Builder(this, NotificationUtils.CHANNEL_ID)
                        .setContentTitle(titleBuffer.toString())
                        .setContentText(contentBuffer.toString())
                        .setSmallIcon(mIcons.getTransparentDrawableId(eventId))
                        .setLargeIcon(largeIcon)
                        .setAutoCancel(true)
                        .setContentIntent(notificationClickPendingIntent)
                        .setSound(ringtoneUri);

                mGroupAssignmentToNotificationId.put(staffAssignmentId, mNextNotificationId);
                if (enableNotifications) {
                    mNotificationManager.notify(mNextNotificationId, builder.build());
                }
                mNextNotificationId++;
                break;
        }
    }

}
