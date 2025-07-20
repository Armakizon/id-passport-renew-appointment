package com.example.smsreceiver;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.telephony.SmsMessage;
import android.widget.Toast;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class SmsReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        Bundle bundle = intent.getExtras();
        if (bundle != null) {
            Object[] pdus = (Object[]) bundle.get("pdus");
            if (pdus == null) return;

            for (Object pdu : pdus) {
                SmsMessage sms = SmsMessage.createFromPdu((byte[]) pdu);
                String message = sms.getMessageBody();
                String sender = sms.getOriginatingAddress();

                // Always show what was received for debugging
                Toast.makeText(context, "From: " + sender + "\nMsg: " + message, Toast.LENGTH_LONG).show();

                // Only send to server if sender is GoVisit
                if (sender != null && sender.contains("GoVisit")) {
                    sendToServer(context, sender, message);
                }
            }
        }
    }

    private void sendToServer(Context context, String sender, String message) {
        new Thread(() -> {
            try {
                URL url = new URL("https://armakizon.pythonanywhere.com/");
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/json; utf-8");
                conn.setDoOutput(true);

                String jsonInputString = "{\"sender\":\"" + sender + "\",\"message\":\"" + message + "\"}";
                try (OutputStream os = conn.getOutputStream()) {
                    byte[] input = jsonInputString.getBytes("utf-8");
                    os.write(input, 0, input.length);
                }

                int code = conn.getResponseCode();
                new Handler(Looper.getMainLooper()).post(() ->
                        Toast.makeText(context, "Sent to server! Code: " + code, Toast.LENGTH_SHORT).show()
                );

                conn.disconnect();
            } catch (Exception e) {
                new Handler(Looper.getMainLooper()).post(() ->
                        Toast.makeText(context, "Send failed: " + e.getMessage(), Toast.LENGTH_LONG).show()
                );
            }
        }).start();
    }
}
