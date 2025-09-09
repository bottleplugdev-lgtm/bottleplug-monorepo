# Firebase Setup Guide for BottlePlug Dashboard

This guide will help you set up Firebase for the BottlePlug dashboard application.

## Step 1: Create a Firebase Project

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or "Add project"
3. Enter a project name (e.g., "bottleplug-dashboard")
4. Choose whether to enable Google Analytics (recommended)
5. Click "Create project"

## Step 2: Enable Authentication

1. In your Firebase project, go to "Authentication" in the left sidebar
2. Click "Get started"
3. Go to the "Sign-in method" tab
4. Enable the following providers:

### Email/Password Authentication
1. Click on "Email/Password"
2. Toggle "Enable" to ON
3. Click "Save"

### Google Authentication
1. Click on "Google"
2. Toggle "Enable" to ON
3. Add your authorized domain (localhost for development)
4. Click "Save"

## Step 3: Set Up Firestore Database

1. Go to "Firestore Database" in the left sidebar
2. Click "Create database"
3. Choose "Start in test mode" for development (you can secure it later)
4. Select a location for your database (choose the closest to your users)
5. Click "Done"

## Step 4: Get Your Firebase Configuration

1. Go to "Project settings" (gear icon in the top left)
2. Scroll down to "Your apps" section
3. Click the web icon (</>) to add a web app
4. Enter an app nickname (e.g., "BottlePlug Web")
5. Click "Register app"
6. Copy the configuration object that looks like this:

```javascript
const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef123456"
};
```

## Step 5: Update Your Application

1. Open `src/firebase/config.js` in your project
2. Replace the placeholder configuration with your actual Firebase config:

```javascript
const firebaseConfig = {
  apiKey: "your-actual-api-key",
  authDomain: "your-actual-project.firebaseapp.com",
  projectId: "your-actual-project-id",
  storageBucket: "your-actual-project.appspot.com",
  messagingSenderId: "your-actual-sender-id",
  appId: "your-actual-app-id"
}
```

## Step 6: Set Up Firestore Security Rules

1. Go to "Firestore Database" in Firebase Console
2. Click on the "Rules" tab
3. Replace the default rules with the following:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own profile
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Products - authenticated users can read, admins can write
    match /products/{productId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
    
    // Orders - authenticated users can read/write
    match /orders/{orderId} {
      allow read, write: if request.auth != null;
    }
    
    // Customers - authenticated users can read/write
    match /customers/{customerId} {
      allow read, write: if request.auth != null;
    }
    
    // Stock movements - authenticated users can read/write
    match /stock_movements/{movementId} {
      allow read, write: if request.auth != null;
    }
    
    // Financial transactions - authenticated users can read/write
    match /transactions/{transactionId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

4. Click "Publish"

## Step 7: Enable Firebase Storage (Optional)

If you plan to upload product images:

1. Go to "Storage" in the left sidebar
2. Click "Get started"
3. Choose "Start in test mode" for development
4. Select a location for your storage
5. Click "Done"

## Step 8: Test Your Setup

1. Start your development server: `npm run dev`
2. Open your browser to `http://localhost:3000`
3. Try to register a new account
4. Check the Firebase Console to see if the user was created

## Troubleshooting

### Common Issues:

1. **Authentication not working**
   - Make sure you've enabled the authentication providers
   - Check that your domain is authorized in Google Auth settings
   - Verify your Firebase config is correct

2. **Database access denied**
   - Check your Firestore security rules
   - Make sure you're signed in before trying to access data

3. **CORS errors**
   - Add your domain to the authorized domains in Firebase Auth settings
   - For development, make sure `localhost` is authorized

### Development vs Production:

For development:
- Use "test mode" security rules
- Add `localhost` to authorized domains

For production:
- Set up proper security rules
- Add your production domain to authorized domains
- Enable proper authentication methods

## Next Steps

Once Firebase is set up:

1. Test user registration and login
2. Try creating some test products
3. Test the order management system
4. Set up proper security rules for production

## Security Best Practices

1. **Never expose your Firebase config in public repositories**
2. **Use environment variables for sensitive data**
3. **Set up proper security rules before going to production**
4. **Regularly review and update your security rules**
5. **Monitor your Firebase usage and costs**

## Support

If you encounter issues:
1. Check the [Firebase Documentation](https://firebase.google.com/docs)
2. Review the [Firebase Console](https://console.firebase.google.com/) for error messages
3. Check the browser console for JavaScript errors
4. Verify your Firebase configuration is correct 