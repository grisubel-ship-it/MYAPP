package com.caregiversync.app;

import com.android.installreferrer.api.InstallReferrerClient;
import com.android.installreferrer.api.InstallReferrerStateListener;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

// Legge il parametro "referrer" del link Google Play (es. conv_code=CODICE)
@CapacitorPlugin(name = "InstallReferrer")
public class InstallReferrerPlugin extends Plugin {

    @PluginMethod
    public void getReferrer(PluginCall call) {
        try {
            InstallReferrerClient client = InstallReferrerClient.newBuilder(getContext()).build();
            client.startConnection(new InstallReferrerStateListener() {
                @Override
                public void onInstallReferrerSetupFinished(int code) {
                    JSObject ret = new JSObject();
                    try {
                        if (code == InstallReferrerClient.InstallReferrerResponse.OK) {
                            ret.put("referrer", client.getInstallReferrer().getInstallReferrer());
                        } else {
                            ret.put("referrer", "");
                        }
                    } catch (Exception e) {
                        ret.put("referrer", "");
                    } finally {
                        client.endConnection();
                    }
                    call.resolve(ret);
                }

                @Override
                public void onInstallReferrerServiceDisconnected() {}
            });
        } catch (Exception e) {
            JSObject ret = new JSObject();
            ret.put("referrer", "");
            call.resolve(ret);
        }
    }
}
