# Firebase Authentication Setup for BottlePlug Dashboard

## Prerequisites
- Firebase CLI installed (`npm install -g firebase-tools`)
- Firebase account

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project"
3. Enter project name: `bottleplug-dashboard`
4. Enable Google Analytics (optional)
5. Click "Create project"

## Step 2: Enable Authentication

1. In Firebase Console, go to "Authentication" → "Sign-in method"
2. Enable the following providers:
   - **Email/Password**
   - **Google**

### Email/Password Setup:
- Click "Email/Password"
- Enable "Email/Password"
- Enable "Email link (passwordless sign-in)" (optional)
- Click "Save"

### Google Setup:
- Click "Google"
- Enable Google sign-in
- Add your authorized domain (localhost for development)
- Click "Save"

## Step 3: Get Firebase Configuration

1. In Firebase Console, go to Project Settings (gear icon)
2. Scroll down to "Your apps"
3. Click "Add app" → "Web"
4. Register app with name "BottlePlug Dashboard"
5. Copy the configuration object

## Step 4: Configure Environment Variables

1. Create a `.env` file in your project root:
```bash
cp env.example .env
```

2. Update `.env` with your Firebase config:
```env
VITE_FIREBASE_API_KEY=your-actual-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

## Step 5: Test Authentication

1. Start the development server:
```bash
npm run dev
```

2. Try signing in with:
   - Email/Password
   - Google

## Step 6: Deploy (Optional)

1. Build the project:
```bash
npm run build
```

2. Deploy to Firebase Hosting:
```bash
firebase deploy
```

## Security Rules

The project includes basic security rules:
- Users can only access their own profile data
- All other data requires authentication
- Storage allows authenticated users to upload/read files

## Troubleshooting

### Common Issues:

1. **"Firebase not configured" error**
   - Check that your `.env` file exists and has correct values
   - Restart the development server after adding environment variables

2. **Google sign-in not working**
   - Ensure Google provider is enabled in Firebase Console
   - Add `localhost` to authorized domains for development

3. **Authentication state not persisting**
   - Check browser console for errors
   - Verify Firebase config values

### Development Mode

The app includes fallback demo mode when Firebase is not configured:
- Uses mock authentication
- Allows testing UI without Firebase setup
- Shows "Demo mode" messages

## Next Steps

1. Set up Firestore database for storing:
   - Products
   - Orders
   - Customers
   - Financial data

2. Configure Storage for:
   - Product images
   - User avatars
   - Document uploads

3. Set up proper security rules based on user roles 