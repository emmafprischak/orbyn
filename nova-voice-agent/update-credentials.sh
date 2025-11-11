#!/bin/bash
# Script to update API credentials in .env file

echo "🔧 Nova Voice Agent - API Key Updater"
echo "======================================"
echo ""

ENV_FILE="/home/user/orbyn/nova-voice-agent/.env"

echo "Current .env location: $ENV_FILE"
echo ""
echo "Please provide your new API credentials:"
echo ""

# Cal.com API Key
read -p "Enter Cal.com API Key (cal_live_...): " CAL_KEY
if [ ! -z "$CAL_KEY" ]; then
    sed -i "s/^CAL_API_KEY=.*/CAL_API_KEY=$CAL_KEY/" "$ENV_FILE"
    echo "✅ Updated Cal.com API key"
fi

# Cal.com Event Type ID
read -p "Enter Cal.com Event Type ID (numeric): " CAL_EVENT_ID
if [ ! -z "$CAL_EVENT_ID" ]; then
    sed -i "s/^CAL_EVENT_TYPE=.*/CAL_EVENT_TYPE=$CAL_EVENT_ID/" "$ENV_FILE"
    echo "✅ Updated Cal.com Event Type ID"
fi

# Notion Token
read -p "Enter Notion Integration Token (secret_... or ntn_...): " NOTION_TOKEN
if [ ! -z "$NOTION_TOKEN" ]; then
    sed -i "s/^NOTION_TOKEN=.*/NOTION_TOKEN=$NOTION_TOKEN/" "$ENV_FILE"
    echo "✅ Updated Notion token"
fi

# Notion Database ID
read -p "Enter Notion Database ID (32 chars, no dashes): " NOTION_DB
if [ ! -z "$NOTION_DB" ]; then
    sed -i "s/^NOTION_DATABASE_ID=.*/NOTION_DATABASE_ID=$NOTION_DB/" "$ENV_FILE"
    echo "✅ Updated Notion database ID"
fi

echo ""
echo "======================================"
echo "✅ API credentials updated!"
echo "🔄 Please restart the Nova server for changes to take effect"
echo ""
echo "To restart:"
echo "  cd /home/user/orbyn/nova-voice-agent"
echo "  python3 -m backend.main"
