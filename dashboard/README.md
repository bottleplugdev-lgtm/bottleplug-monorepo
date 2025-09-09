# BottlePlug Dashboard

A comprehensive Vue.js dashboard for managing alcohol and beverages business operations. Built with modern web technologies and Firebase integration.

## 🚀 Features

### Authentication
- **Google Sign-in** - Seamless authentication with Google accounts
- **Email/Password Sign-in** - Traditional authentication method
- **User Registration** - Complete user onboarding with profile creation
- **Role-based Access** - Admin and user role management

### Dashboard Modules

#### 📊 Overview
- Real-time business metrics and KPIs
- Revenue tracking and growth indicators
- Top-selling products analysis
- Recent activity feed
- Quick action buttons for common tasks

#### 🍷 Products Management
- Add, edit, and delete products
- Category-based organization
- Product images and descriptions
- Price and stock management
- Search and filter functionality

#### 📦 Stock Management
- Real-time stock level monitoring
- Low stock alerts and notifications
- Stock in/out operations
- Inventory value tracking
- Stock history and audit trails

#### 🛒 Order Management
- Complete order lifecycle management
- Order status tracking (Pending, Processing, Completed)
- Customer order history
- New order creation with multiple items
- Order filtering and search

#### 👥 Customer Management
- Customer profile management
- Purchase history tracking
- Retail shop details
- Customer segmentation
- Contact information management

#### 💰 Financial Management
- Revenue and expense tracking
- Profit and loss analysis
- Financial reporting
- Transaction history
- Budget monitoring

#### 📈 Analytics
- Sales performance metrics
- Customer behavior analysis
- Product performance insights
- Geographic distribution
- Trend analysis and forecasting

#### ⚙️ Settings
- User profile management
- Business information settings
- Security preferences
- Notification settings
- Billing and subscription management

## 🛠️ Technology Stack

- **Frontend Framework**: Vue 3 with Composition API
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Pinia
- **Routing**: Vue Router 4
- **Backend/Authentication**: Firebase
  - Firebase Auth for authentication
  - Firestore for database
  - Firebase Storage for file uploads
- **Icons**: Lucide Vue Next
- **Notifications**: Vue3 Toastify
- **Charts**: Chart.js (ready for implementation)

## 📋 Prerequisites

- Node.js (v16 or higher)
- npm or yarn package manager
- Firebase project setup

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bottleplug-dashboard
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Firebase Configuration**
   
   Create a Firebase project at [Firebase Console](https://console.firebase.google.com/) and get your configuration:
   
   ```javascript
   // src/firebase/config.js
   const firebaseConfig = {
     apiKey: "your-api-key",
     authDomain: "your-auth-domain",
     projectId: "your-project-id",
     storageBucket: "your-storage-bucket",
     messagingSenderId: "your-messaging-sender-id",
     appId: "your-app-id"
   }
   ```

4. **Firebase Security Rules**
   
   Set up Firestore security rules:
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
     }
   }
   ```

5. **Run the development server**
   ```bash
   npm run dev
   ```

6. **Open your browser**
   Navigate to `http://localhost:3000`

## 📁 Project Structure

```
src/
├── components/          # Reusable Vue components
├── views/              # Page components
│   ├── dashboard/      # Dashboard page components
│   ├── Login.vue       # Authentication pages
│   └── Register.vue
├── stores/             # Pinia stores
│   └── auth.js         # Authentication store
├── router/             # Vue Router configuration
│   └── index.js
├── firebase/           # Firebase configuration
│   └── config.js
├── assets/             # Static assets
├── style.css           # Global styles
└── main.js             # Application entry point
```

## 🎨 Customization

### Colors and Theme
The dashboard uses a custom color palette defined in `tailwind.config.js`:

```javascript
colors: {
  primary: {
    50: '#f0f9ff',
    500: '#3b82f6',
    600: '#2563eb',
    // ... more shades
  },
  secondary: {
    // ... secondary color shades
  }
}
```

### Adding New Features
1. Create new Vue components in `src/views/dashboard/`
2. Add routes in `src/router/index.js`
3. Update navigation in `src/views/Dashboard.vue`
4. Create Pinia stores for state management if needed

## 📊 Data Models

### User Profile
```javascript
{
  id: 'user-id',
  email: 'user@example.com',
  displayName: 'John Doe',
  firstName: 'John',
  lastName: 'Doe',
  phone: '+1234567890',
  businessName: 'BottlePlug Store',
  role: 'admin' | 'user',
  createdAt: Timestamp,
  photoURL: 'https://...'
}
```

### Product
```javascript
{
  id: 'product-id',
  name: 'Premium Whiskey',
  category: 'Spirits',
  description: 'Premium aged whiskey',
  price: 45.99,
  stock: 100,
  image: 'https://...',
  sku: 'WHISKEY-001',
  createdAt: Timestamp,
  updatedAt: Timestamp
}
```

### Order
```javascript
{
  id: 'order-id',
  customerId: 'customer-id',
  items: [
    {
      productId: 'product-id',
      name: 'Premium Whiskey',
      quantity: 2,
      price: 45.99,
      total: 91.98
    }
  ],
  total: 91.98,
  status: 'pending' | 'processing' | 'completed',
  createdAt: Timestamp,
  updatedAt: Timestamp
}
```

## 🚀 Deployment

### Firebase Hosting
1. Install Firebase CLI: `npm install -g firebase-tools`
2. Login: `firebase login`
3. Initialize: `firebase init hosting`
4. Build: `npm run build`
5. Deploy: `firebase deploy`

### Vercel
1. Connect your repository to Vercel
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Deploy automatically on push

## 🔒 Security Considerations

- All Firebase security rules are properly configured
- Authentication is required for all sensitive operations
- Role-based access control implemented
- Input validation on all forms
- XSS protection through Vue's built-in sanitization

## 📱 Responsive Design

The dashboard is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔮 Future Enhancements

- [ ] Real-time notifications
- [ ] Advanced analytics and reporting
- [ ] Mobile app development
- [ ] Integration with payment gateways
- [ ] Barcode scanning functionality
- [ ] Multi-language support
- [ ] Advanced inventory forecasting
- [ ] Customer loyalty program
- [ ] Supplier management
- [ ] Advanced reporting and exports

---

**BottlePlug Dashboard** - Empowering alcohol and beverage businesses with modern technology. 