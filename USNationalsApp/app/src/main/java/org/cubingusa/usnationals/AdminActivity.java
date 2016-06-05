package org.cubingusa.usnationals;

import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;
import com.loopj.android.http.RequestParams;

import cz.msebera.android.httpclient.Header;

public class AdminActivity extends AppCompatActivity {

    private static final String TAG = "AdminActivity";

    private SharedPreferences mPreferences;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_admin);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        mPreferences = getSharedPreferences(Constants.PREFRENCES, MODE_PRIVATE);
        switch (mPreferences.getInt(
                Constants.ADMIN_STATUS_PREFERENCE_KEY, Constants.ADMIN_STATUS_NOT_REQUESTED)) {
            case Constants.ADMIN_STATUS_NOT_REQUESTED:
                showRequestAdminStatus();
                break;
            case Constants.ADMIN_STATUS_REQUESTED:
                showAwaitingAdminStatus();
                break;
            case Constants.ADMIN_STATUS_GRANTED:
                showHasAdminStatus();
                break;
            default:
                break;
        }

        Button requestAccessButton = (Button) findViewById(R.id.request_access);
        if (requestAccessButton != null) {
            requestAccessButton.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    Uri uri = new Uri.Builder()
                            .scheme("https")
                            .authority(Constants.HOSTNAME)
                            .appendPath("register_device")
                            .build();
                    AsyncHttpClient client = new AsyncHttpClient();
                    RequestParams params = new RequestParams();
                    params.put("id", DeviceId.getDeviceId(mPreferences));
                    params.put("password", DeviceId.getDevicePassword(mPreferences));
                    client.post(uri.toString(), params, new AsyncHttpResponseHandler() {
                                @Override
                                public void onSuccess(
                                        int statusCode, Header[] headers, byte[] responseBody) {
                                    showAwaitingAdminStatus();
                                    mPreferences.edit().putInt(
                                            Constants.ADMIN_STATUS_PREFERENCE_KEY,
                                            Constants.ADMIN_STATUS_REQUESTED).apply();
                                }

                                @Override
                                public void onFailure(
                                        int statusCode, Header[] headers, byte[] responseBody,
                                        Throwable error) {
                                    Log.e(TAG, error.toString());
                                }
                            });
                    showSpinner();
                }
            });
        }

        Button revokeAccessButton = (Button) findViewById(R.id.revoke_access);
        if (revokeAccessButton != null) {
            revokeAccessButton.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    Uri uri = new Uri.Builder()
                            .scheme("https")
                            .authority(Constants.HOSTNAME)
                            .appendPath("register_device")
                            .build();
                    AsyncHttpClient client = new AsyncHttpClient();
                    RequestParams params = new RequestParams();
                    params.put("id", DeviceId.getDeviceId(mPreferences));
                    params.put("password", DeviceId.getDevicePassword(mPreferences));
                    params.put("unregister", "1");
                    client.post(uri.toString(), params, new AsyncHttpResponseHandler() {
                        @Override
                        public void onSuccess(
                                int statusCode, Header[] headers, byte[] responseBody) {
                            showRequestAdminStatus();
                            mPreferences.edit().putInt(
                                    Constants.ADMIN_STATUS_PREFERENCE_KEY,
                                    Constants.ADMIN_STATUS_NOT_REQUESTED).apply();
                        }

                        @Override
                        public void onFailure(
                                int statusCode, Header[] headers, byte[] responseBody,
                                Throwable error) {
                            Log.e(TAG, error.toString());
                        }
                    });
                    showSpinner();
                }
            });
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        Intent intent = MenuHandler.menuOptionIntent(this, item);
        if (intent == null) {
            return super.onOptionsItemSelected(item);
        }
        startActivity(intent);
        return true;
    }

    private void showRequestAdminStatus() {
        TextView textView = (TextView) findViewById(R.id.admin_info);
        if (textView == null) {
            return;
        }
        textView.setText(R.string.request_access_info);
        textView.setVisibility(View.VISIBLE);

        setVisibility(findViewById(R.id.admin_password), View.GONE);
        setVisibility(findViewById(R.id.revoke_access), View.GONE);
        setVisibility(findViewById(R.id.request_access), View.VISIBLE);
        setVisibility(findViewById(R.id.admin_spinner), View.GONE);
    }

    private void showAwaitingAdminStatus() {
        TextView textView = (TextView) findViewById(R.id.admin_info);
        if (textView == null) {
            return;
        }
        textView.setText(R.string.awaiting_access_info);
        textView.setVisibility(View.VISIBLE);

        TextView adminPassword = (TextView) findViewById(R.id.admin_password);
        if (adminPassword == null) {
            return;
        }
        adminPassword.setText(DeviceId.getDevicePassword(mPreferences));

        setVisibility(findViewById(R.id.admin_password), View.VISIBLE);
        setVisibility(findViewById(R.id.revoke_access), View.GONE);
        setVisibility(findViewById(R.id.request_access), View.GONE);
        setVisibility(findViewById(R.id.admin_spinner), View.GONE);
    }

    private void showHasAdminStatus() {
        TextView textView = (TextView) findViewById(R.id.admin_info);
        if (textView == null) {
            return;
        }
        textView.setText(getString(R.string.has_access_info,
                mPreferences.getString(Constants.ADMIN_NAME_PREFERENCE_KEY, "")));
        textView.setVisibility(View.VISIBLE);

        setVisibility(findViewById(R.id.admin_password), View.GONE);
        setVisibility(findViewById(R.id.revoke_access), View.VISIBLE);
        setVisibility(findViewById(R.id.request_access), View.GONE);
        setVisibility(findViewById(R.id.admin_spinner), View.GONE);
    }

    private void showSpinner() {
        setVisibility(findViewById(R.id.admin_info), View.GONE);
        setVisibility(findViewById(R.id.admin_password), View.GONE);
        setVisibility(findViewById(R.id.revoke_access), View.GONE);
        setVisibility(findViewById(R.id.request_access), View.GONE);
        setVisibility(findViewById(R.id.admin_spinner), View.VISIBLE);
    }

    void setVisibility(View view, int visibility) {
        if (view != null) {
            view.setVisibility(visibility);
        }
    }
}
