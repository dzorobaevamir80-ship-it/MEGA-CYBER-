MEGA CYBER Android project
==========================

This is an Android/Kivy port of the supplied Pygame game. It is source code,
not an APK yet. The included GitHub Actions workflow builds a debug APK.

Build:
1. Create a GitHub repository and upload all files from this folder, including
   the hidden .github/workflows/build.yml file.
2. Open the repository -> Actions -> "Build MEGA CYBER APK" -> Run workflow.
3. When it finishes, open the run -> Artifacts -> MEGA-CYBER-APK and download.
4. Extract the ZIP and install the APK on your Samsung. Android may ask you to
   allow installation from that browser/file manager.

Note: This is a first Android port of the game mechanics. It uses Kivy because
Pygame is not a straightforward Android APK build target with Buildozer.
