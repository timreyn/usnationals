package org.cubingusa.usnationals;

import android.content.SharedPreferences;
import android.util.Log;

import com.google.firebase.messaging.FirebaseMessaging;

import java.util.Random;

public class DeviceId {
    private static final String TAG = "DeviceId";

    public static final String DEVICE_ID_PREFERENCE_KEY = "DEVICE_ID";
    public static final String DEVICE_PASSWORD_PREFERENCE_KEY = "DEVICE_PASSWORD";
    public static final int DEVICE_PASSWORD_NUM_DIGITS = 8;

    public static String getDeviceTopic(String deviceId) {
        return "/topics/device_" + deviceId;
    }

    public static String getDeviceId(SharedPreferences preferences) {
        String deviceId = preferences.getString(DEVICE_ID_PREFERENCE_KEY, "");
        if (deviceId.isEmpty()) {
            Random random = new Random(System.currentTimeMillis());
            deviceId = Integer.toHexString(random.nextInt());
            preferences.edit().putString(DEVICE_ID_PREFERENCE_KEY, deviceId).apply();
        }
        FirebaseMessaging.getInstance().subscribeToTopic(getDeviceTopic(deviceId));
        return deviceId;
    }

    public static String getDevicePassword(SharedPreferences preferences) {
        String devicePassword = preferences.getString(DEVICE_PASSWORD_PREFERENCE_KEY, "");
        if (devicePassword.isEmpty()) {
            Random random = new Random(System.currentTimeMillis());
            final int passwordMinValue = (int) Math.pow(10, DEVICE_PASSWORD_NUM_DIGITS - 1);
            devicePassword = Integer.toString(
                    random.nextInt(9 * passwordMinValue) + passwordMinValue);
            preferences.edit().putString(DEVICE_PASSWORD_PREFERENCE_KEY, devicePassword).apply();
        }
        return devicePassword;
    }

    public static void revokeDeviceId(SharedPreferences preferences) {
        String deviceId = preferences.getString(DEVICE_ID_PREFERENCE_KEY, "");
        if (!deviceId.isEmpty()) {
            FirebaseMessaging.getInstance().unsubscribeFromTopic(getDeviceTopic(deviceId));
        }
        preferences.edit().remove(DEVICE_ID_PREFERENCE_KEY).apply();
    }
}
