# Deploying GMRS to Vercel

## Prerequisites
1. A Vercel account (sign up at https://vercel.com)
2. Your project pushed to GitHub

## Deployment Steps

### Method 1: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/dashboard
   - Sign in with your GitHub account

2. **Import Your Project**
   - Click "Add New..." → "Project"
   - Select your GitHub repository: `guidancemanagementreport-droid/GMRS`
   - Click "Import"

3. **Configure Project Settings**
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as default)
   - **Build Command**: Leave empty (Vercel will auto-detect)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

4. **Add Environment Variables**
   Click "Environment Variables" and add:
   - `SECRET_KEY`: Your Flask secret key (generate a secure random string)
   - `SUPABASE_URL`: `https://wnbmaltublivkfiwzltq.supabase.co`
   - `SUPABASE_KEY`: Your Supabase anon key

5. **Deploy**
   - Click "Deploy"
   - Wait for the build to complete
   - Your app will be live at `https://your-project-name.vercel.app`

### Method 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```
   Follow the prompts to link your project.

4. **Set Environment Variables**
   ```bash
   vercel env add SECRET_KEY
   vercel env add SUPABASE_URL
   vercel env add SUPABASE_KEY
   ```

5. **Deploy to Production**
   ```bash
   vercel --prod
   ```

## Important Notes

⚠️ **Vercel Limitations for Flask Apps:**
- Static files (CSS, JS, images) should be served from `/static` route
- Sessions may have limitations (consider using serverless-compatible session storage)
- File uploads may need special handling
- Some Flask features may not work in serverless environment

✅ **What Works:**
- All your routes and blueprints
- Supabase integration
- Templates and rendering
- API endpoints

## Troubleshooting

### Build Errors
- Check that `requirements.txt` has all dependencies
- Ensure Python version is compatible (Vercel uses Python 3.9+)

### Runtime Errors
- Check environment variables are set correctly
- Review Vercel function logs in the dashboard
- Ensure Supabase credentials are correct

### Static Files Not Loading
- Verify static file paths in templates use `url_for('static', ...)`
- Check that files are in `app/static/` directory

## Post-Deployment

1. **Update CORS Settings** (if needed)
   - In Supabase dashboard, add your Vercel domain to allowed origins

2. **Test Your App**
   - Visit your Vercel URL
   - Test login/register functionality
   - Verify all routes work correctly

3. **Custom Domain** (Optional)
   - Go to Project Settings → Domains
   - Add your custom domain

## Support

If you encounter issues:
- Check Vercel logs: Dashboard → Your Project → Functions → View Logs
- Review Vercel documentation: https://vercel.com/docs
- Flask on Vercel guide: https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python

