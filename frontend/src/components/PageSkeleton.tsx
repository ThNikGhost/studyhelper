/**
 * PageSkeleton - Loading fallback for lazy-loaded pages.
 *
 * Shows an animated skeleton UI while the page chunk is being loaded.
 * Used as Suspense fallback in App.tsx.
 */
export function PageSkeleton() {
  return (
    <div className="container mx-auto p-6 animate-pulse">
      {/* Header skeleton */}
      <div className="h-8 bg-muted rounded-md w-48 mb-6" />

      {/* Content skeleton */}
      <div className="space-y-4">
        <div className="h-32 bg-muted rounded-lg" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="h-24 bg-muted rounded-lg" />
          <div className="h-24 bg-muted rounded-lg" />
        </div>
        <div className="h-48 bg-muted rounded-lg" />
      </div>
    </div>
  )
}
