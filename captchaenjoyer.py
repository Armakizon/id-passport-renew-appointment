# Enhanced captcha evasion with multiple strategies
import os
import shutil
import random
import time
from datetime import datetime

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

def rotate_profiles():
    """Rotate between multiple Firefox profiles to avoid detection"""
    profiles = [
        "C:\\Users\\shake\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\4g5qddpm.default-release",
        "C:\\Users\\shake\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\ezygy35n.Sele",
        "C:\\Users\\shake\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\ghm9bfgv.Default Userd",
        "C:\\Users\\shake\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\nhi655hy.Default User"
    ]
    
    # Randomly select a source profile
    source = random.choice(profiles)
    # Use a different target profile
    target = random.choice([p for p in profiles if p != source])
    
    print(f"🔄 Rotating profiles: {os.path.basename(source)} → {os.path.basename(target)}")
    copy_firefox_profile_files(source, target)

def add_random_delay():
    """Add random delays to make requests look more human-like"""
    delay = random.uniform(2, 8)  # Random delay between 2-8 seconds
    print(f"⏱️ Adding random delay: {delay:.1f} seconds")
    time.sleep(delay)

def get_random_user_agent():
    """Return a random user agent string to vary browser fingerprint"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]
    return random.choice(user_agents)

def smart_cookie_management():
    """Smart cookie management - only clear suspicious ones, not all"""
    cookie_strategies = [
        'keep_all_cookies',           # 40% chance - most natural
        'clear_tracking_cookies',     # 35% chance - moderate
        'clear_session_cookies',      # 20% chance - occasional
        'clear_all_cookies'           # 5% chance - rare, only when needed
    ]
    
    strategy = random.choices(cookie_strategies, weights=[40, 35, 20, 5])[0]
    
    if strategy == 'keep_all_cookies':
        print("🍪 Keeping all cookies (natural behavior)")
    elif strategy == 'clear_tracking_cookies':
        print("🧹 Clearing only tracking cookies (moderate cleanup)")
    elif strategy == 'clear_session_cookies':
        print("🗑️ Clearing session cookies (occasional cleanup)")
    else:
        print("⚠️ Clearing all cookies (emergency cleanup only)")
    
    return strategy

def use_incognito_mode():
    """Configure browser to use incognito/private browsing"""
    incognito_config = {
        'mode': random.choice(['private', 'incognito', 'normal']),
        'clear_on_exit': random.choice([True, False]),
        'tracking_protection': random.choice([True, False])
    }
    
    print(f"🕵️ Browser mode: {incognito_config['mode']}")
    if incognito_config['clear_on_exit']:
        print("   📝 Will clear data on exit")
    if incognito_config['tracking_protection']:
        print("   🛡️ Tracking protection enabled")
    
    return incognito_config

def randomize_browser_fingerprint():
    """Randomize various browser fingerprinting elements"""
    fingerprint_config = {
        'screen_resolution': random.choice([
            (1920, 1080), (1366, 768), (1440, 900), (1536, 864), (1280, 720)
        ]),
        'timezone': random.choice([
            'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
            'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Asia/Tokyo'
        ]),
        'language': random.choice([
            'en-US', 'en-GB', 'en-CA', 'de-DE', 'fr-FR', 'es-ES'
        ]),
        'color_depth': random.choice([24, 32]),
        'pixel_ratio': random.choice([1, 1.25, 1.5, 2]),
        'hardware_concurrency': random.choice([2, 4, 8, 16])
    }
    
    print(f"🎨 Randomizing fingerprint: {fingerprint_config['screen_resolution']}px, {fingerprint_config['timezone']}")
    return fingerprint_config

def create_human_like_patterns():
    """Create human-like interaction patterns"""
    patterns = {
        'typing_speed': random.uniform(0.1, 0.3),  # seconds between keystrokes
        'mouse_speed': random.uniform(0.5, 2.0),   # seconds for mouse movements
        'scroll_behavior': random.choice(['smooth', 'jerky', 'natural']),
        'click_delay': random.uniform(0.1, 0.5)    # seconds after hover before click
    }
    
    print(f"👤 Human patterns: {patterns['typing_speed']:.2f}s typing, {patterns['mouse_speed']:.2f}s mouse")
    return patterns

def apply_anti_captcha_strategies():
    """Apply all anti-captcha strategies"""
    print("🛡️ Applying anti-captcha strategies...")
    
    # 1. Profile rotation
    rotate_profiles()
    
    # 2. Random delay
    add_random_delay()
    
    # 3. Get random user agent
    ua = get_random_user_agent()
    print(f"🌐 Using User-Agent: {ua[:50]}...")
    
    # 4. Smart cookie management (instead of clearing all)
    cookie_strategy = smart_cookie_management()
    
    # 5. Incognito mode configuration
    incognito_config = use_incognito_mode()
    
    # 6. Randomize browser fingerprint
    fingerprint = randomize_browser_fingerprint()
    
    # 7. Create human-like patterns
    patterns = create_human_like_patterns()
    
    print("✅ Anti-captcha strategies applied")
    return {
        'user_agent': ua,
        'cookie_strategy': cookie_strategy,
        'incognito_config': incognito_config,
        'fingerprint': fingerprint,
        'patterns': patterns
    }

if __name__ == "__main__":
    # Test the enhanced functionality
    apply_anti_captcha_strategies()
