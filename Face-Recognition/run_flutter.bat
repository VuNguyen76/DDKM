@echo off
echo ========================================
echo Starting Flutter Face Recognition App
echo ========================================
echo.

cd face_recognition_app
echo Getting Flutter dependencies...
flutter pub get
echo.

echo Available devices:
flutter devices
echo.

echo Starting Flutter app...
echo Note: If you have multiple devices, use: flutter run -d [device-id]
flutter run

