#made to swap porofiles and try to evade the captcha, however currently seems to be not needed since captcha prevention isnt high

import os
import shutil

def copy_firefox_profile_files(
    source_folder="C:\\Users\\shake\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\4g5qddpm.default-release",
    target_folder="C:\\Users\\shake\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\ezygy35n.Sele"
):
    files_to_copy = [
        "logins.json",
        "key4.db",
        "cookies.sqlite",
        "permissions.sqlite",
        "prefs.js",        # ⚠️ Be cautious with prefs.js; you might want to manually merge instead.
        "user.js",
        "cert9.db",
        "places.sqlite"
    ]

    copied = []
    missing = []

    for filename in files_to_copy:
        src_path = os.path.join(source_folder, filename)
        dst_path = os.path.join(target_folder, filename)

        if os.path.exists(src_path):
            try:
                shutil.copy2(src_path, dst_path)
                copied.append(filename)
            except Exception as e:
                print(f"⚠️ Failed to copy {filename}: {e}")
        else:
            missing.append(filename)

    print(f"✅ Copied: {copied}")
    if missing:
        print(f"❌ Missing files not copied: {missing}")

if __name__ == "__main__":
    copy_firefox_profile_files()
