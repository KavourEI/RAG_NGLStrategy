# Streamlit Cloud Secrets Setup Guide

## Problem: 401 Not Authenticated Error

If you're getting `Error: status_code: 401, body: {'detail': 'Not authenticated'}`, it means your API credentials are not being properly passed to the API endpoints.

## Required Secrets

Your Streamlit Cloud app needs these three secrets configured:

1. **LLAMA_CLOUD_API_KEY** - Your LlamaCloud API key for document indexing
2. **LLAMA_ORG_ID** - Your LlamaCloud organization ID
3. **OLLAMA_ORG_ID** - Your Ollama organization ID (used as Bearer token for API calls)

## How to Add Secrets to Streamlit Cloud

### Step 1: Access Streamlit Cloud App Settings
1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Find your **RAG_NGLStrategy** app in the list
3. Click on the **three dots** menu (•••) at the top right
4. Select **Edit secrets**

### Step 2: Add Secrets in TOML Format

In the secrets editor, add your credentials in TOML format:

```toml
LLAMA_CLOUD_API_KEY = "your_actual_api_key_here"
LLAMA_ORG_ID = "your_org_id_here"
OLLAMA_ORG_ID = "your_ollama_org_id_here"
```

**Important:** 
- Each secret should be on its own line
- Use `=` to assign values (TOML format)
- Values should be in double quotes if they contain special characters
- Do NOT include comments or anything after the value

### Step 3: Save and Restart

1. Click **Save** button
2. Streamlit will automatically restart your app
3. Check the logs to verify secrets are loaded

## Verification

Run the verification script to check your local setup:

```bash
python verify_secrets.py
```

If everything is configured correctly, you should see:
```
✅ LlamaCloud API Key: ****...****
✅ LlamaCloud Organization ID: ****...****
✅ Ollama Organization ID: ****...****
```

## Troubleshooting

### Still getting 401 error?

1. **Verify secret values are correct:**
   - Copy/paste them carefully from your LlamaCloud dashboard
   - Check for extra spaces or quotes around values
   
2. **Ensure API endpoints are correct:**
   - LlamaCloud index should use your organization credentials
   - Ollama API should use the correct base URL

3. **Check Streamlit app logs:**
   - In Streamlit Cloud, click **Manage app** → **View logs**
   - Look for error messages about missing or invalid credentials

4. **Test locally first:**
   ```bash
   # Create a .env file in your project root
   echo 'LLAMA_CLOUD_API_KEY=your_key' > .env
   echo 'LLAMA_ORG_ID=your_org_id' >> .env
   echo 'OLLAMA_ORG_ID=your_ollama_id' >> .env
   
   # Run the verification
   python verify_secrets.py
   ```

5. **Check API credentials:**
   - Log in to LlamaCloud and verify your API key is active
   - Ensure the organization ID matches your LlamaCloud account
   - Verify Ollama credentials are correct

## App Code Changes

The app has been updated to:
- ✅ Properly validate that secrets are set
- ✅ Use correct secret names (`OLLAMA_ORG_ID` instead of `OLLAMA_API_KEY`)
- ✅ Pass credentials correctly to API endpoints
- ✅ Provide clear error messages if secrets are missing

## Environment Variables (Local Development)

For local development, create a `.env` file in your project root:

```
LLAMA_CLOUD_API_KEY=sk-...
LLAMA_ORG_ID=org-...
OLLAMA_ORG_ID=...
```

The app will automatically load these via `python-dotenv`.

## API Endpoints

The app uses:
- **LlamaCloud API:** For document indexing and retrieval (requires `LLAMA_CLOUD_API_KEY` and `LLAMA_ORG_ID`)
- **Ollama API:** For language model inference (requires `OLLAMA_ORG_ID` as Bearer token)

Make sure both API services are accessible and your credentials have the necessary permissions.
