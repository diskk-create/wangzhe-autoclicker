package com.wangzhe.autoclicker;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.widget.Toast;
import android.content.Context;
import android.widget.Button;
import android.widget.LinearLayout;
import android.view.View;
import android.os.Environment;
import android.os.Handler;
import android.util.Log;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import android.content.res.AssetManager;

public class MainActivity extends Activity {
    private WebView webView;
    private Handler handler = new Handler();
    private static final String TAG = "AutoClickerApp";
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // 创建主布局
        LinearLayout mainLayout = new LinearLayout(this);
        mainLayout.setOrientation(LinearLayout.VERTICAL);
        
        // 创建WebView
        webView = new WebView(this);
        webView.setLayoutParams(new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT,
            1.0f
        ));
        
        // 创建控制按钮
        LinearLayout buttonLayout = new LinearLayout(this);
        buttonLayout.setOrientation(LinearLayout.HORIZONTAL);
        
        Button btnStart = new Button(this);
        btnStart.setText("开始运行");
        btnStart.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                webView.loadUrl("javascript:startScript()");
                Toast.makeText(MainActivity.this, "开始运行脚本", Toast.LENGTH_SHORT).show();
            }
        });
        
        Button btnStop = new Button(this);
        btnStop.setText("停止运行");
        btnStop.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                webView.loadUrl("javascript:stopScript()");
                Toast.makeText(MainActivity.this, "停止脚本", Toast.LENGTH_SHORT).show();
            }
        });
        
        Button btnSettings = new Button(this);
        btnSettings.setText("设置");
        btnSettings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                webView.loadUrl("javascript:openSettings()");
            }
        });
        
        Button btnHelp = new Button(this);
        btnHelp.setText("帮助");
        btnHelp.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                webView.loadUrl("javascript:showHelp()");
            }
        });
        
        buttonLayout.addView(btnStart);
        buttonLayout.addView(btnStop);
        buttonLayout.addView(btnSettings);
        buttonLayout.addView(btnHelp);
        
        // 添加控件到布局
        mainLayout.addView(webView);
        mainLayout.addView(buttonLayout);
        
        setContentView(mainLayout);
        
        // 配置WebView
        setupWebView();
        
        // 加载本地HTML界面
        webView.loadUrl("file:///android_asset/index.html");
        
        // 复制Python脚本到应用目录
        copyAssets();
    }
    
    private void setupWebView() {
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setDatabaseEnabled(true);
        webSettings.setAllowFileAccess(true);
        webSettings.setAllowContentAccess(true);
        
        // 支持JavaScript调用Android方法
        webView.addJavascriptInterface(new WebAppInterface(this), "Android");
        
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                view.loadUrl(url);
                return true;
            }
        });
        
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                if (newProgress == 100) {
                    // 页面加载完成
                }
            }
        });
    }
    
    private void copyAssets() {
        AssetManager assetManager = getAssets();
        String[] files = null;
        try {
            files = assetManager.list("");
        } catch (IOException e) {
            Log.e(TAG, "Failed to get asset file list.", e);
        }
        
        if (files != null) {
            for (String filename : files) {
                if (filename.endsWith(".py") || filename.endsWith(".txt") || filename.endsWith(".json")) {
                    InputStream in = null;
                    OutputStream out = null;
                    try {
                        in = assetManager.open(filename);
                        File outFile = new File(getFilesDir(), filename);
                        out = new FileOutputStream(outFile);
                        copyFile(in, out);
                        Log.d(TAG, "Copied asset: " + filename);
                    } catch (IOException e) {
                        Log.e(TAG, "Failed to copy asset: " + filename, e);
                    } finally {
                        if (in != null) {
                            try {
                                in.close();
                            } catch (IOException e) {
                                // ignore
                            }
                        }
                        if (out != null) {
                            try {
                                out.close();
                            } catch (IOException e) {
                                // ignore
                            }
                        }
                    }
                }
            }
        }
    }
    
    private void copyFile(InputStream in, OutputStream out) throws IOException {
        byte[] buffer = new byte[1024];
        int read;
        while ((read = in.read(buffer)) != -1) {
            out.write(buffer, 0, read);
        }
    }
    
    // JavaScript接口
    public class WebAppInterface {
        Context mContext;
        
        WebAppInterface(Context c) {
            mContext = c;
        }
        
        @android.webkit.JavascriptInterface
        public void showToast(String message) {
            Toast.makeText(mContext, message, Toast.LENGTH_SHORT).show();
        }
        
        @android.webkit.JavascriptInterface
        public String runPythonScript(String scriptName) {
            // 这里可以调用Python脚本
            return "脚本执行完成: " + scriptName;
        }
        
        @android.webkit.JavascriptInterface
        public String getScriptList() {
            // 返回可用的脚本列表
            return "[\"smart_auto_clicker.py\", \"four_mode_cycle.py\"]";
        }
    }
    
    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}