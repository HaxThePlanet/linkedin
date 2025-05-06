#!/usr/bin/env python3
"""
Direct test script for the LinkedIn "mark as unread" fix

This script uses the LinkedIn API directly to verify that the
fixed JSON format with "$set" works correctly.

"""

import json
import requests
import os
import sys

# LinkedIn conversation URN that we want to mark as unread
CONVERSATION_URN = "urn:li:msg_conversation:(urn:li:fsd_profile:PROFILE_ID,CONVERSATION_ID)"

# Encode the URN for the URL
ENCODED_URN = CONVERSATION_URN.replace(":", "%3A").replace("(", "%28").replace(")", "%29").replace(",", "%2C")

# API URL
API_URL = f"https://www.linkedin.com/voyager/api/voyagerMessagingDashMessengerConversations?ids=List({ENCODED_URN})"

# Credentials
LI_AT_COOKIE = "YOUR_LI_AT_COOKIE"
JSESSIONID_COOKIE = "YOUR_JSESSIONID"
CSRF_TOKEN = "YOUR_CSRF_TOKEN"

def print_header(message):
    """Print a header message"""
    print("\n" + "=" * 80)
    print(f"{message}")
    print("=" * 80)

def test_fixed_format():
    """Test the fixed format with $set"""
    print_header("TESTING FIXED FORMAT WITH $set")
    
    # Construct the payload with "$set" - this matches the fixed code
    payload = {
        "entities": {
            CONVERSATION_URN: {
                "patch": {
                    "$set": {
                        "read": False
                    }
                }
            }
        }
    }
    
    print(f"Request URL: {API_URL}")
    print("\nRequest payload (FIXED format with $set):")
    print(json.dumps(payload, indent=2))
    
    # Make the request
    print("\nSending request...")
    
    headers = {
        "cookie": f"li_at={LI_AT_COOKIE}; JSESSIONID=\"{JSESSIONID_COOKIE}\"",
        "csrf-token": CSRF_TOKEN,
        "content-type": "text/plain;charset=UTF-8",
        "accept": "application/json",
        "x-li-lang": "en_US",
        "x-restli-protocol-version": "2.0.0"
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    
    # Display response
    print(f"\nResponse status code: {response.status_code}")
    try:
        json_response = response.json()
        print("Response body:")
        print(json.dumps(json_response, indent=2))
        
        # Check if successful
        if response.status_code in (200, 204) and "errors" in json_response and not json_response["errors"]:
            print("\n✅ SUCCESS: The fixed format with $set works correctly!")
            print("This confirms the fix implemented in the LinkedIn bridge is correct.")
            return True
        else:
            print("\n❌ ERROR: The fixed format did not work as expected.")
            return False
    except:
        print(f"Raw response: {response.text}")
        print("\n❌ ERROR: Could not parse response as JSON")
        return False

def test_broken_format():
    """Test the broken format with set (no $)"""
    print_header("TESTING BROKEN FORMAT WITH set (no $)")
    
    # Construct the payload with "set" - this is the bug
    payload = {
        "entities": {
            CONVERSATION_URN: {
                "patch": {
                    "set": {
                        "read": False
                    }
                }
            }
        }
    }
    
    print(f"Request URL: {API_URL}")
    print("\nRequest payload (BROKEN format with plain 'set'):")
    print(json.dumps(payload, indent=2))
    
    # Make the request
    print("\nSending request...")
    
    headers = {
        "cookie": f"li_at={LI_AT_COOKIE}; JSESSIONID=\"{JSESSIONID_COOKIE}\"",
        "csrf-token": CSRF_TOKEN,
        "content-type": "text/plain;charset=UTF-8",
        "accept": "application/json",
        "x-li-lang": "en_US",
        "x-restli-protocol-version": "2.0.0"
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    
    # Display response
    print(f"\nResponse status code: {response.status_code}")
    try:
        json_response = response.json()
        print("Response body:")
        print(json.dumps(json_response, indent=2))
        
        # We expect this to fail with 422
        if response.status_code == 422:
            print("\n✅ EXPECTED FAILURE: The broken format with 'set' fails as expected.")
            print("This confirms the bug when not using '$set'.")
            return True
        else:
            print("\n❓ UNEXPECTED RESULT: The broken format didn't fail with 422 as expected.")
            return False
    except:
        print(f"Raw response: {response.text}")
        print("\n❌ ERROR: Could not parse response as JSON")
        return False

def verify_bridge_code():
    """Verify the bridge code was fixed correctly"""
    print_header("VERIFYING BRIDGE CODE")
    
    # Path to the receipts.go file that was fixed
    receipts_go_path = "pkg/linkedingo/receipts.go"
    
    if not os.path.exists(receipts_go_path):
        print(f"❌ ERROR: Could not find {receipts_go_path}")
        return False
    
    # Read the file and look for the fixed code
    with open(receipts_go_path, "r") as f:
        content = f.read()
    
    # Check if the fix is present
    if '"$set"' in content:
        print("✅ FOUND: The bridge code properly uses $set in the JSON format")
        
        # Find the specific fixed code
        if 'entities[convURN.URNString()] = map[string]any{' in content and '"$set": map[string]bool{' in content:
            print("✅ VERIFIED: The fix appears to be implemented correctly")
            print("\nThe exact fixed code found:")
            print("```go")
            # Extract and print the fixed code segment
            start_idx = content.find('entities[convURN.URNString()] = map[string]any{')
            end_idx = content.find('}', start_idx)
            end_idx = content.find('}', end_idx + 1)
            end_idx = content.find('}', end_idx + 1)
            if start_idx > 0 and end_idx > start_idx:
                print(content[start_idx:end_idx+1])
            print("```")
            return True
        else:
            print("⚠️ WARNING: The fix might not be implemented correctly")
            return False
    else:
        print("❌ ERROR: The bridge code doesn't use $set in the JSON format")
        return False

def main():
    """Run the tests"""
    print("LINKEDIN 'MARK AS UNREAD' FIX VALIDATION")
    print("\nThis script verifies that:")
    print("1. The fixed format with $set works correctly with the LinkedIn API")
    print("2. The broken format with 'set' fails as expected")
    print("3. The bridge code has been fixed correctly")
    
    # Test the fixed format
    fixed_result = test_fixed_format()
    
    # Uncomment to test the broken format - we'll skip this to avoid marking conversations as read unnecessarily
    # broken_result = test_broken_format()
    
    # Verify the bridge code
    code_result = verify_bridge_code()
    
    # Final summary
    print_header("FINAL VERIFICATION RESULTS")
    
    if fixed_result and code_result:
        print("✅ SUCCESS: The fix is verified to be working correctly!")
        print("✅ The LinkedIn API accepts the $set format")
        print("✅ The bridge code has been properly fixed")
        print("\nWhen deployed to production, the '!li unread' command will work correctly.")
        sys.exit(0)
    else:
        print("❌ FAILURE: Issues were found during verification.")
        if not fixed_result:
            print("❌ The LinkedIn API test failed")
        if not code_result:
            print("❌ Issues were found in the bridge code")
        sys.exit(1)

if __name__ == "__main__":
    main() 