# Authentication in MOSAIC

This directory contains the authentication implementation for MOSAIC using Clerk.

## Current Implementation

The current implementation uses Clerk for authentication with the following features:

- Sign-in and sign-up pages using Clerk components
- User profile management in settings
- Protected routes with Clerk middleware
- Authentication state management with Clerk

## Files Structure

- `layout.tsx`: Layout for authentication pages
- `sign-in/page.tsx`: Sign-in page using Clerk's SignIn component
- `sign-up/page.tsx`: Sign-up page using Clerk's SignUp component
- `README.md`: This file

## Clerk Integration

The following components have been integrated with Clerk:

1. **Middleware**: Using Clerk's middleware to protect routes
2. **Layout**: Using Clerk's ClerkProvider in the root layout
3. **Authentication Pages**: Using Clerk's SignIn and SignUp components
4. **User Profile**: Using Clerk's UserProfile component in the settings page
5. **Sidebar**: Using Clerk's SignInButton and SignOutButton components

## Environment Variables

The following environment variables are required for Clerk to work:

```
# Clerk Authentication Keys
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_publishable_key
CLERK_SECRET_KEY=your_secret_key

# Clerk URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/auth/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/auth/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/

# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Next Steps

1. **Webhook Integration**: Set up Clerk webhooks to sync user data with the backend
2. **User Data Export/Deletion**: Implement GDPR-compliant user data export and deletion
3. **API Authorization**: Update backend API endpoints to verify Clerk JWT tokens
4. **Role-Based Access Control**: Implement role-based access control using Clerk roles

## Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Next.js Authentication](https://nextjs.org/docs/authentication)
