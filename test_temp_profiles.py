#!/usr/bin/env python3
"""
Test script to verify temporary profile system works correctly
"""

import os
import tempfile
import shutil
from access_govisit import create_temporary_profile, cleanup_temporary_profile

def test_temporary_profiles():
    """Test the temporary profile creation and cleanup system"""
    print("🧪 Testing temporary profile system...")
    
    # Test 1: Create temporary profile
    print("\n1. Testing profile creation...")
    profile_path = create_temporary_profile()
    
    if os.path.exists(profile_path):
        print(f"✅ Profile created successfully: {profile_path}")
        print(f"   Profile exists: {os.path.exists(profile_path)}")
        print(f"   Is directory: {os.path.isdir(profile_path)}")
    else:
        print(f"❌ Failed to create profile: {profile_path}")
        return False
    
    # Test 2: Verify it's in temp directory
    print("\n2. Testing profile location...")
    temp_dir = tempfile.gettempdir()
    if profile_path.startswith(temp_dir):
        print(f"✅ Profile is in temporary directory: {temp_dir}")
    else:
        print(f"⚠️ Profile is not in expected temp directory")
        print(f"   Expected: {temp_dir}")
        print(f"   Actual: {profile_path}")
    
    # Test 3: Test cleanup
    print("\n3. Testing profile cleanup...")
    cleanup_temporary_profile(profile_path)
    
    if not os.path.exists(profile_path):
        print(f"✅ Profile cleaned up successfully")
    else:
        print(f"❌ Profile still exists after cleanup: {profile_path}")
        return False
    
    # Test 4: Verify no interference with existing profiles
    print("\n4. Testing no interference with existing profiles...")
    firefox_profiles_dir = os.path.expanduser("~/AppData/Roaming/Mozilla/Firefox/Profiles")
    
    if os.path.exists(firefox_profiles_dir):
        existing_profiles = [d for d in os.listdir(firefox_profiles_dir) 
                           if os.path.isdir(os.path.join(firefox_profiles_dir, d))]
        print(f"✅ Found existing Firefox profiles: {len(existing_profiles)}")
        print(f"   Profiles: {existing_profiles[:3]}...")  # Show first 3
        
        # Verify our temp profile didn't get created in Firefox profiles directory
        temp_profile_name = os.path.basename(profile_path)
        if temp_profile_name not in existing_profiles:
            print(f"✅ Temporary profile not in Firefox profiles directory")
        else:
            print(f"❌ Temporary profile found in Firefox profiles directory!")
            return False
    else:
        print(f"ℹ️ Firefox profiles directory not found: {firefox_profiles_dir}")
    
    print("\n🎉 All tests passed! Temporary profile system is working correctly.")
    return True

if __name__ == "__main__":
    success = test_temporary_profiles()
    if success:
        print("\n✅ Profile system is safe and won't interfere with your main Firefox profile!")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
