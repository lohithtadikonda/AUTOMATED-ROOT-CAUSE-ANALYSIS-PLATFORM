# Root Cause Analysis Platform - Authentication System

A complete sign-in page with MongoDB Atlas backend authentication for your Root Cause Analysis platform.

## 🌟 Features

- **Beautiful Sign-in UI** - Modern, responsive design
- **Secure Authentication** - JWT tokens, bcrypt password hashing
- **MongoDB Atlas** - Cloud-based, scalable database (no local MongoDB needed!)
- **Remember Me** - Extended session support
- **Password Reset** - Forgot password functionality
- **Protected Routes** - Middleware for securing endpoints

## 📋 Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- MongoDB Atlas account (free tier available)

## 🚀 Quick Start

### 1. Set Up MongoDB Atlas (FREE Cloud Database)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free account
3. Click "Build a Database" → Choose "FREE" tier (M0)
4. Choose your cloud provider and region
5. Click "Create Cluster"
6. Create a database user:
   - Click "Database Access" → "Add New Database User"
   - Choose "Password" authentication
   - Set username and password (remember these!)
7. Whitelist your IP:
   - Click "Network Access" → "Add IP Address"
   - Click "Allow Access from Anywhere" (or add your specific IP)
8. Get your connection string:
   - Click "Database" → "Connect" → "Connect your application"
   - Copy the connection string (looks like: `mongodb+srv://...`)

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your MongoDB Atlas connection string:

```env
MONGODB_URI=mongodb+srv://your-username:your-password@cluster0.xxxxx.mongodb.net/rca-platform?retryWrites=true&w=majority
JWT_SECRET=your-random-secret-key-here
PORT=3000
```

**Important:** Replace:
- `your-username` with your MongoDB username
- `your-password` with your MongoDB password
- `cluster0.xxxxx` with your actual cluster URL
- `your-random-secret-key-here` with a strong random string

### 4. Run the Server

```bash
npm start
```

Or for development with auto-restart:

```bash
npm run dev
```

### 5. Access the Application

Open your browser and go to:
```
http://localhost:3000/signin-page.html
```

## 📁 Project Structure

```
├── server.js              # Express server with MongoDB connection
├── signin-page.html       # Sign-in page UI
├── package.json          # Dependencies
├── .env                  # Environment variables (create this)
└── .env.example          # Environment variables template
```

## 🔐 API Endpoints

### Authentication

**Sign Up**
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "firstName": "John",
  "lastName": "Doe"
}
```

**Sign In**
```http
POST /api/auth/signin
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "remember": true
}
```

**Get Current User** (Protected)
```http
GET /api/auth/me
Authorization: Bearer <your-jwt-token>
```

**Forgot Password**
```http
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

## 🔧 Testing the API

You can test the API using curl:

```bash
# Sign up a new user
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "firstName": "Test",
    "lastName": "User"
  }'

# Sign in
curl -X POST http://localhost:3000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

## 🛡️ Security Features

- **Password Hashing**: bcrypt with salt rounds
- **JWT Tokens**: Secure token-based authentication
- **CORS Protection**: Configurable CORS settings
- **Input Validation**: Server-side validation
- **Secure Headers**: Protection against common vulnerabilities

## 📊 Database Schema

**User Model**
```javascript
{
  email: String (unique, required),
  password: String (hashed, required),
  firstName: String (required),
  lastName: String (required),
  role: String (user/admin/analyst),
  createdAt: Date,
  lastLogin: Date
}
```

## 🎨 Customization

### Modify the UI

Edit `signin-page.html` to customize:
- Colors (change gradient in CSS)
- Logo (add your logo image)
- Feature list
- Form fields

### Add More User Fields

In `server.js`, update the `userSchema`:

```javascript
const userSchema = new mongoose.Schema({
  // ... existing fields
  company: String,
  department: String,
  // ... add more fields
});
```

## 🚢 Deployment

### Deploy to Heroku

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-rca-platform

# Set environment variables
heroku config:set MONGODB_URI="your-connection-string"
heroku config:set JWT_SECRET="your-secret-key"

# Deploy
git push heroku main
```

### Deploy to Vercel/Netlify

For frontend deployment, these platforms work great. For the backend, consider:
- Railway
- Render
- Fly.io

## 🔍 Troubleshooting

**MongoDB Connection Failed**
- Check your connection string format
- Verify username/password are correct
- Ensure IP is whitelisted in MongoDB Atlas
- Check if cluster is active

**Port Already in Use**
- Change PORT in `.env` file
- Or stop the process using port 3000

**JWT Token Invalid**
- Check JWT_SECRET matches in `.env`
- Token may have expired (default: 7 days)

## 📝 Next Steps

1. Create a sign-up page
2. Add password reset email functionality
3. Build the dashboard after login
4. Add user profile management
5. Implement role-based access control
6. Add OAuth (Google, GitHub) login

## 📄 License

MIT

## 🤝 Contributing

Feel free to submit issues and enhancement requests!
