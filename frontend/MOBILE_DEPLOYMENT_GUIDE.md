# KOSHA LABS – Android & iOS Native Mobile Deployment Guide

This guide details the complete native packaging, compilation, hardware scanner integration, and store publishing workflow for the **Kosha Labs Intelligent Worker Identity Management System** wrapped with **Capacitor**.

---

## 1. Application Identifiers & Specifications

| Property | Value | Notes |
| :--- | :--- | :--- |
| **Application ID / Package** | `com.koshalabs.workerverification` | Configured across Android (`applicationId`) and iOS (`CFBundleIdentifier`) |
| **App Display Name** | `Kosha Labs` | User-facing title on home screens and task switchers |
| **Runtime Framework** | Capacitor 8.6 + React 19 + TypeScript | Native WebView with bridge plugins |
| **Web Distribution Dir** | `dist` | Generated via `npm run build` |
| **Android Project Root** | `frontend/android` | Ready for Android Studio & Gradle |
| **iOS Project Root** | `frontend/ios/App` | Ready for Xcode & CocoaPods/SPM |

---

## 2. Brand Assets & Native Configuration

### Generated Icons & Splash Screens
- **Android Mipmaps:** Custom emerald-500 fingerprint & shield emblem generated across all screen densities:
  - `mipmap-mdpi/` (48×48)
  - `mipmap-hdpi/` (72×72)
  - `mipmap-xhdpi/` (96×96)
  - `mipmap-xxhdpi/` (144×144)
  - `mipmap-xxxhdpi/` (192×192)
- **iOS AppIcon:** Master 1024×1024 App Store icon at `ios/App/App/Assets.xcassets/AppIcon.appiconset/App-Icon-512@2x.png`.
- **Splash Screen:** Deep slate background (`#020617`) with emerald glow and auto-hide transition via `@capacitor/splash-screen`.

### Native Permissions
- **Android (`AndroidManifest.xml`):**
  - `INTERNET` and `ACCESS_NETWORK_STATE`: For encrypted API connectivity to the biometric FastAPI backend.
  - `CAMERA`: For scanning worker QR codes and inspection documentation.
  - `android.hardware.usb.host`: Hardware host mode for USB OTG external fingerprint scanners.
  - `BLUETOOTH`, `BLUETOOTH_ADMIN`, `BLUETOOTH_CONNECT`: For wireless Bluetooth optical biometric readers.
  - `usesCleartextTraffic="true"`: Enabled for local development environments (`http://10.0.2.2:3000`).
- **iOS (`Info.plist`):**
  - `NSCameraUsageDescription`: Worker document and QR badge verification.
  - `NSBluetoothAlwaysUsageDescription` & `NSBluetoothPeripheralUsageDescription`: Wireless biometric scanner communication.
  - `NSAppTransportSecurity`: Configured for development endpoints.

---

## 3. Fingerprint Scanner Hardware SDK Integration

The mobile application is architected to ingest fingerprint scans from two primary sources:
1. **Direct File / Multi-Session Upload:** High-resolution optical scan images (BMP / WSQ / PNG) captured and passed to the ML inference pipeline.
2. **External Optical / Capacitive Fingerprint Scanners:** Industrial turnkey readers connected via USB OTG or Bluetooth.

### Supported Industrial Hardware
- **Mantra MFS100 / MFS500** (USB OTG & BLE)
- **SecuGen Hamster Pro 20 / Hamster IV**
- **Morpho (IDEMIA) MSO 1300 E3**
- **Startek FM220U**

### Native Android Bridge Implementation (For Physical USB OTG Scanners)
When integrating vendor hardware SDKs (e.g., `MFS100SDK.aar` or `SecuGen.FDxSDKPro.jar`):
1. Place the vendor `.aar` / `.jar` inside `frontend/android/app/libs/`.
2. In `frontend/android/app/src/main/java/com/koshalabs/workerverification/MainActivity.java`, register a custom Capacitor plugin bridge:
   ```java
   @CapacitorPlugin(name = "FingerprintScanner")
   public class FingerprintScannerPlugin extends Plugin {
       @PluginMethod
       public void captureFingerprint(PluginCall call) {
           // Invoke vendor SDK capture routine:
           // 1. Check USB device attachment
           // 2. Request UsbManager permission
           // 3. Capture raw bitmap & minutiae
           // 4. Return base64 bitmap string to web layer:
           JSObject ret = new JSObject();
           ret.put("imageBase64", base64Bmp);
           ret.put("qualityScore", qualityScore);
           call.resolve(ret);
       }
   }
   ```
3. In `frontend/src/services/biometrics.ts`, the scanner layer passes the captured base64 string directly to `/api/ml/extract` and `/api/biometrics/recognize`, matching against the 128-D Siamese CNN model.

> [!IMPORTANT]
> **No Camera Simulation:** The phone camera is never used as an insecure substitute for a genuine biometric sensor. The system strictly processes uncompressed ridge topology matrices through the calibrated 128-D Euclidean Siamese network.

---

## 4. Android Build & Deployment

### Prerequisites on Build Machine
- **JDK 17:** (`export JAVA_HOME=/path/to/jdk-17`)
- **Android Studio** (Hedgehog, Iguana, or Ladybug) with **Android SDK 34 / 35** and **Command-line Tools**.

### A. Development Build (Debug APK)
```bash
cd frontend
npm run build
npx cap sync android

cd android
./gradlew assembleDebug
```
*Output Artifact:* `android/app/build/outputs/apk/debug/app-debug.apk`

Install directly onto an Android device via ADB:
```bash
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

### B. Production Release Build (Signed AAB for Google Play)
1. Generate an upload keystore (if not already created):
   ```bash
   keytool -genkey -v -keystore kosha-upload-key.jks -alias kosha-key -keyalg RSA -keysize 2048 -validity 10000
   ```
2. Configure credentials in `android/key.properties`:
   ```properties
   storePassword=YOUR_KEYSTORE_PASSWORD
   keyPassword=YOUR_KEY_PASSWORD
   keyAlias=kosha-key
   storeFile=../kosha-upload-key.jks
   ```
3. Compile the release bundle:
   ```bash
   cd android
   ./gradlew bundleRelease
   ```
*Output Artifact:* `android/app/build/outputs/bundle/release/app-release.aab`  
Upload `app-release.aab` directly to the **Google Play Console** under Closed/Open Testing or Production track.

---

## 5. iOS Build & TestFlight Deployment

### Prerequisites on Build Machine
- **macOS** with **Xcode 15 or 16** installed from the Mac App Store.
- **Active Apple Developer Account** enrolled in the Apple Developer Program ($99/yr).

### A. Open and Configure in Xcode
```bash
cd frontend
npm run build
npx cap sync ios
npx cap open ios
```

1. In Xcode, select the root project **App**.
2. Under **Signing & Capabilities**:
   - Check **Automatically manage signing**.
   - Select your registered **Team**.
   - Verify Bundle Identifier: `com.koshalabs.workerverification`.
3. Select an iOS Simulator (e.g. *iPhone 16 Pro*) or connected physical iPhone.
4. Press **Cmd + R** to build and run.

### B. TestFlight / App Store Connect Archive
1. In Xcode, select destination **Any iOS Device (arm64)**.
2. Select menu **Product -> Archive**.
3. Once the Organizer window opens:
   - Click **Distribute App**.
   - Select **App Store Connect** -> **Upload**.
   - Ensure App Store distribution certificate and provisioning profile are selected.
4. Once processing finishes on App Store Connect (10-15 mins):
   - Add Internal and External Testers in **TestFlight**.
   - Submit for App Review for App Store release.

---

## 6. Production Backend & Environment Configuration

### Dynamic API Endpoint Configuration
In the mobile app, backend API endpoints are dynamically resolved so the mobile app can connect to remote staging or production servers without recompilation:

1. **Environment Variable (Build-Time):**
   Set `VITE_API_BASE_URL` in `frontend/.env.production`:
   ```env
   VITE_API_BASE_URL=https://api.koshalabs.com/api
   ```
2. **Runtime Configuration (In-App Terminal):**
   In the mobile app **Settings / Terminal Config**, operators can enter the server IP or domain:
   ```
   Server URL: https://api.koshalabs.com
   ML Microservice: http://192.168.1.150:8000
   ```
   Stored securely in native persistent storage via `@capacitor/preferences`.
