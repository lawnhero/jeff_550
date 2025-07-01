# Admin Authentication Setup

## Knowledge Base Manager Access

The Knowledge Base Manager page is protected with password authentication to ensure only authorized instructors can upload and manage course materials.

## Password Configuration

### Option 1: Using secrets.toml (Recommended for local development)

1. The password is stored in `.streamlit/secrets.toml`
2. Default password: `ISOM550_Admin_2024!`
3. To change the password, edit the file:
   ```toml
   [general]
   admin_password = "YourNewSecurePassword"
   ```

### Option 2: Using Environment Variables (Recommended for production)

1. Set the environment variable:
   ```bash
   export ADMIN_PASSWORD="YourSecurePassword"
   ```

2. Update `.streamlit/secrets.toml` to use the environment variable:
   ```toml
   [general]
   admin_password = "$ADMIN_PASSWORD"
   ```

## Security Best Practices

1. **Change the default password** before deploying to production
2. **Use a strong password** with at least 12 characters, including:
   - Uppercase and lowercase letters
   - Numbers
   - Special characters
3. **Never commit secrets.toml** to version control (it's already in .gitignore)
4. **Use environment variables** for production deployments
5. **Regularly rotate passwords** for enhanced security

## Deployment Instructions

### Streamlit Cloud
1. In your Streamlit Cloud app dashboard, go to "Secrets"
2. Add the following:
   ```toml
   [general]
   admin_password = "YourProductionPassword"
   ```

### Other Cloud Platforms
- Set `ADMIN_PASSWORD` as an environment variable in your deployment platform
- Ensure the environment variable is properly configured before starting the app

## Troubleshooting

### Password Not Working
1. Check that the password in secrets.toml matches what you're entering
2. Verify there are no extra spaces or characters
3. If using environment variables, ensure they're properly set

### Can't Access Admin Page
1. Make sure you're on the "Knowledge Base Manager" page (check sidebar menu)
2. Clear your browser cache and try again
3. Restart the Streamlit app if needed

### Reset Authentication
To reset the authentication session:
1. Clear browser cookies for the app
2. Or restart the Streamlit app
3. Or use the "Logout" button in the admin sidebar

## Current Setup

- **Default Password**: `ISOM550_Admin_2024!`
- **Configuration File**: `.streamlit/secrets.toml`
- **Protected Page**: Knowledge Base Manager
- **Access Method**: Password-based authentication with session state

## For Students

Students do not need any special access. They can use the main Virtual TA interface without authentication. Only instructors need the admin password to access the Knowledge Base Manager. 