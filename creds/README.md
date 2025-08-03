# Credentials Setup

## For new users:
1. Go to https://codeforces.com/settings/api
2. Generate your API key and secret
3. Create `credentials_local.py` in this folder with:

```python
apiKey = "your_actual_api_key"
apiSecret = "your_actual_api_secret"
```

## Files:
- `credentials.py` - Template with placeholder values (tracked by git)
- `credentials_local.py` - Your actual keys (ignored by git)
- The update script automatically uses local credentials if available