---
globs: ["frontend/**/*.ts", "frontend/**/*.tsx"]
description: TypeScript and React coding standards
---

# TypeScript / React Rules

## Components
- Functional components only (no class components)
- One component per file, named export matching filename
- Props interface: `interface FooProps { ... }` above component
- Use `React.FC` is optional, prefer explicit return type

## TypeScript
- Strict mode enabled (`strict: true` in tsconfig)
- Prefer `type` for unions/intersections, `interface` for object shapes
- Use `import type { ... }` for type-only imports
- No `any` — use `unknown` and narrow types
- Enums: prefer `as const` objects over TypeScript enums

## State Management
- Server state: TanStack Query (`useQuery`, `useMutation`)
- Client state: Zustand stores (`frontend/src/stores/`)
- Form state: local `useState` (no form library yet)

## UI Patterns
- Components: shadcn/ui (`frontend/src/components/ui/`)
- Styling: Tailwind CSS v4 utility classes
- Icons: lucide-react
- Modals: shared `Modal` component (`components/ui/modal.tsx`)
- Notifications: sonner toasts (`toast.success()`, `toast.error()`)
- Loading: spinner or skeleton states

## API Layer
- Services in `frontend/src/services/` (one per backend module)
- Axios client with JWT interceptors (`services/api.ts`)
- Token refresh with mutex lock (already implemented)
- AbortController for cancellable requests
- Error handling: `getErrorMessage()` from `utils/errorUtils.ts`

## Page Pattern
```tsx
// 1. Loading state
if (isLoading) return <Spinner />;
// 2. Error state
if (error) return <ErrorMessage error={error} />;
// 3. Content
return <div>...</div>;
```

## File Structure
```
frontend/src/
├── components/ui/     # shadcn/ui + shared components
├── pages/             # Page components (one per route)
├── services/          # API service modules
├── stores/            # Zustand stores
├── utils/             # Helpers (dateUtils, errorUtils, constants)
├── types/             # Shared TypeScript types
└── App.tsx            # Router setup
```
