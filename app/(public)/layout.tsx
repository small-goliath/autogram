import Link from 'next/link';
import { Navigation } from '@/components/Navigation';

export default function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
        <div className="h-16 px-6 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <img
              src="/logo.png"
              alt="Autogram Logo"
              className="w-10 h-10 rounded-lg"
            />
            <span className="text-xl font-bold text-gray-900">Autogram</span>
          </Link>
        </div>

        {/* Navigation Tabs */}
        <Navigation />
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-6">
        <div className="container mx-auto px-4 text-center text-sm text-gray-600">
          <p>&copy; 2025 Autogram. All rights reserved. | 모든 권리 보유.</p>
        </div>
      </footer>
    </div>
  );
}
