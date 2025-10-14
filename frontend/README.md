# NutriAI Frontend

AI-powered nutrition assistant built with React, TypeScript, and shadcn/ui following Test-Driven Development (TDD).

## ✅ Implementation Status

All 8 user stories completed with **49 passing tests**:

- ✓ **US1**: User Registration
- ✓ **US2**: User Login
- ✓ **US3**: User Logout
- ✓ **US4**: Profile Management (goal & dietary preferences)
- ✓ **US5**: Recipe Generation with LLM
- ✓ **US6**: View Generated Recipes
- ✓ **US7**: Save Recipes
- ✓ **US8**: View Saved Recipes List

## 🛠 Tech Stack

- **Framework**: Vite + React 18 + TypeScript
- **UI Library**: shadcn/ui (Radix UI primitives)
- **Styling**: Tailwind CSS with CSS variables
- **Routing**: React Router v7
- **Forms**: React Hook Form + Zod validation
- **HTTP Client**: Axios
- **Testing**: Vitest + React Testing Library + MSW
- **State Management**: React hooks (useState, useEffect)

## 📁 Project Structure

```
src/
├── components/          # React components
│   ├── ui/             # shadcn/ui components (Button, Input, Label, Select)
│   ├── LoginForm.tsx
│   ├── RegisterForm.tsx
│   ├── Navbar.tsx
│   ├── ProfileForm.tsx
│   ├── RecipeGenerator.tsx
│   ├── RecipeList.tsx
│   └── ProtectedRoute.tsx
├── pages/              # Page components
│   ├── HomePage.tsx
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── ProfilePage.tsx
│   ├── GenerateRecipePage.tsx
│   └── RecipesPage.tsx
├── services/           # API services
│   ├── auth.ts
│   ├── profile.ts
│   └── recipes.ts
├── types/              # TypeScript types
│   └── api.ts
├── test/               # Test setup
│   ├── setup.ts
│   └── mocks/
│       ├── server.ts
│       └── handlers.ts
├── lib/                # Utilities
│   └── utils.ts
└── index.css          # Theme system (CSS variables)
```

## 🎨 Theme Customization

The entire app theme can be customized by editing **ONE file**: `src/index.css`

See [THEMING.md](THEMING.md) for detailed instructions.

**Quick example:**
```css
:root {
  --primary: 142 76% 36%;    /* Change to your brand color */
  --accent: 24 100% 50%;     /* Change to your accent color */
}
```

The app includes 3 preset themes:
1. Fresh & Healthy (default) - Green + Orange
2. Professional Medical - Blue + Green
3. Warm & Inviting - Coral + Amber

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ (v18.15.0+)
- npm 9+

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Run tests with UI
npm run test:ui

# Generate coverage report
npm run coverage

# Build for production
npm run build
```

### Environment Setup

The frontend expects the backend API to be running on `http://localhost:8000/api`.

API endpoints are proxied in `vite.config.ts`:
```typescript
server: {
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```

## 🧪 Testing

**Test Coverage**: 49 tests across 6 test files

```bash
# Run all tests
npm test

# Run specific test file
npm test src/components/RegisterForm.test.tsx

# Watch mode (default)
npm test

# Run once
npm test run
```

### Testing Tools
- **Vitest**: Fast unit test framework
- **React Testing Library**: Component testing utilities
- **MSW (Mock Service Worker)**: API mocking
- **@testing-library/user-event**: User interaction simulation

All API calls are mocked in `src/test/mocks/handlers.ts` for isolated testing.

## 📋 Available Routes

### Public Routes
- `/login` - Login page
- `/register` - Registration page

### Protected Routes (require authentication)
- `/` - Home page
- `/profile` - User profile management
- `/generate` - Recipe generation
- `/recipes` - Saved recipes list

Protected routes automatically redirect to `/login` if not authenticated.

## 🔐 Authentication

Authentication uses token-based auth with localStorage:
- Token stored in `localStorage.getItem('token')`
- User ID stored in `localStorage.getItem('user_id')`
- `authService.isAuthenticated()` checks for valid token
- `ProtectedRoute` component guards authenticated routes

## 🎯 Key Features

### Form Validation
- Client-side validation with Zod schemas
- Server-side error display
- Accessible error messages (aria-invalid)

### Loading States
- Skeleton loading for data fetching
- Disabled buttons during submission
- Loading text feedback

### Error Handling
- User-friendly error messages
- Retry functionality
- Graceful degradation

### Responsive Design
- Mobile-first approach
- Tailwind responsive utilities
- Grid layouts for recipe cards

### Accessibility
- Semantic HTML
- ARIA labels and roles
- Keyboard navigation
- Focus management

## 🔧 Configuration Files

- `vite.config.ts` - Vite configuration with path aliases
- `vitest.config.ts` - Test configuration
- `tailwind.config.js` - Tailwind with CSS variables
- `components.json` - shadcn/ui configuration
- `tsconfig.json` - TypeScript configuration

## 📦 Dependencies

### Core
- react@19.1.1
- react-dom@19.1.1
- react-router-dom@7.9.4
- axios@1.12.2

### Forms & Validation
- react-hook-form@7.65.0
- zod@4.1.12
- @hookform/resolvers@5.2.2

### UI
- @radix-ui/react-label@2.1.7
- tailwindcss@4.1.14
- class-variance-authority@0.7.1
- clsx@2.1.1
- tailwind-merge@3.3.1

### Testing (Dev)
- vitest@3.2.4
- @testing-library/react@16.3.0
- @testing-library/jest-dom@6.9.1
- @testing-library/user-event@14.6.1
- msw@2.11.5
- jsdom@24.0.0

## 📝 Scripts

```json
{
  "dev": "vite",
  "build": "tsc -b && vite build",
  "lint": "eslint .",
  "preview": "vite preview",
  "test": "vitest",
  "test:ui": "vitest --ui",
  "coverage": "vitest run --coverage"
}
```

## 🐛 Known Issues

- **Node.js Version**: If using Node 18.15.0, some packages show engine warnings but work correctly
- **shadcn CLI**: Requires Node 18.18.0+, components were created manually for compatibility

## 🎓 Development Notes

### TDD Approach
This project was built following strict Test-Driven Development:
1. **RED**: Write failing tests first
2. **GREEN**: Implement minimum code to pass tests
3. **REFACTOR**: Improve code while keeping tests green

### Code Quality
- TypeScript strict mode enabled
- ESLint configuration
- Consistent component structure
- Service layer for API calls
- Type-safe API interfaces

## 📄 License

This project is part of the NutriAI MVP.

---

**Built with TDD 🧪 | Styled with shadcn/ui 🎨 | Powered by React ⚛️**
