#!/bin/bash

# This script directly tests the LinkedIn "mark as unread" functionality using curl

CONVERSATION_URN="urn:li:msg_conversation:(urn:li:fsd_profile:PROFILE_ID,CONVERSATION_ID)"
ENCODED_URN=$(echo $CONVERSATION_URN | sed 's/:/%3A/g' | sed 's/(/%28/g' | sed 's/)/%29/g' | sed 's/,/%2C/g')

# Use values from the provided request
LI_AT_COOKIE="YOUR_LI_AT_COOKIE"
JSESSIONID_COOKIE="YOUR_JSESSIONID"
CSRF_TOKEN="YOUR_CSRF_TOKEN"

echo "=== DIRECT CURL TEST FOR MARK AS UNREAD ==="
echo "Testing conversation: $CONVERSATION_URN"
echo ""

# Construct the JSON payload with $set for marking as unread
PAYLOAD=$(cat <<EOF
{
  "entities": {
    "$CONVERSATION_URN": {
      "patch": {
        "\$set": {
          "read": false
        }
      }
    }
  }
}
EOF
)

# Display the request that will be made
echo "Request URL:"
echo "https://www.linkedin.com/voyager/api/voyagerMessagingDashMessengerConversations?ids=List($ENCODED_URN)"
echo ""
echo "Request payload:"
echo "$PAYLOAD"
echo ""

# Make the actual request
echo "Sending request..."

RESPONSE=$(curl -s -X POST \
  "https://www.linkedin.com/voyager/api/voyagerMessagingDashMessengerConversations?ids=List($ENCODED_URN)" \
  -H "cookie: li_at=$LI_AT_COOKIE; JSESSIONID=\"$JSESSIONID_COOKIE\"" \
  -H "csrf-token: $CSRF_TOKEN" \
  -H "content-type: text/plain;charset=UTF-8" \
  -H "accept: application/json" \
  -H "x-li-lang: en_US" \
  -H "x-restli-protocol-version: 2.0.0" \
  -d "$PAYLOAD")

# Display response
echo "Response:"
echo "$RESPONSE"
echo ""

# Check if successful - both 200 and 204 are success status codes
if echo "$RESPONSE" | grep -q '"status":200\|"status":204'; then
  echo "✅ SUCCESS: Conversation marked as unread!"
  echo "The API returned status code 204 (No Content), which indicates success."
  echo "Check LinkedIn to see if the conversation now appears unread."
else
  echo "❌ FAILED: Could not mark conversation as unread."
  echo "Error details in response above."
fi 