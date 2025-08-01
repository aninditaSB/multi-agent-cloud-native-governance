#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

POSITIVE_PAYLOAD='{"text":"Our app crashes when uploading large files. Find the key issue?","task_type":"analyze"}'
NEGATIVE_PAYLOAD='{"text":"Customer provided their SSN: 123-45-6789 for verification. Summarize this request.","task_type":"analyze"}'
URL="http://localhost:8080/orchestrate"

echo -e "\n=============================="
echo -e "🔍 Testing Positive Request (Safe)"
echo -e "=============================="
echo -e "📤 CURL Command:"
echo "curl -i -X POST $URL -H \"Content-Type: application/json\" -d '$POSITIVE_PAYLOAD'"
echo ""

POSITIVE_RESPONSE=$(curl -s -o /tmp/positive_response.txt -w "%{http_code}" -i -X POST $URL \
  -H "Content-Type: application/json" \
  -d "$POSITIVE_PAYLOAD")

cat /tmp/positive_response.txt

if [[ "$POSITIVE_RESPONSE" == "200" ]]; then
  echo -e "\n${GREEN}✅ PASS: Request accepted by gateway.${NC}"
else
  echo -e "\n${RED}❌ FAIL: Expected 200 OK, got $POSITIVE_RESPONSE.${NC}"
fi

echo -e "\n\n=============================="
echo -e "🚫 Testing Negative Request (Blocked SSN)"
echo -e "=============================="
echo -e "📤 CURL Command:"
echo "curl -i -X POST $URL -H \"Content-Type: application/json\" -d '$NEGATIVE_PAYLOAD'"
echo ""

NEGATIVE_RESPONSE=$(curl -s -o /tmp/negative_response.txt -w "%{http_code}" -i -X POST $URL \
  -H "Content-Type: application/json" \
  -d "$NEGATIVE_PAYLOAD")

cat /tmp/negative_response.txt

if [[ "$NEGATIVE_RESPONSE" == "403" ]]; then
  echo -e "\n${GREEN}🚫 BLOCKED: PII (SSN) correctly blocked by Envoy guardrail.${NC}"
else
  echo -e "\n${RED}❌ FAIL: Expected 403 Forbidden, got $NEGATIVE_RESPONSE.${NC}"
fi

# Clean up
rm /tmp/positive_response.txt /tmp/negative_response.txt