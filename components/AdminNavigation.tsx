'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { logout } from '@/lib/auth';

const adminNavLinks = [
  { href: '/admin/users', label: 'SNS 품앗이 사용자' },
  { href: '/admin/helpers', label: '헬퍼 계정' }
];

export default function AdminNavigation() {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/admin/login');
  };

  return (
    <nav className="bg-gray-900 text-white">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/admin/users" className="flex items-center space-x-3">
            <img
              src="/logo.png"
              alt="Autogram Logo"
              className="w-10 h-10 rounded-lg"
            />
            <span className="text-xl font-bold">Autogram 관리자</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center space-x-1">
            {adminNavLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  pathname === link.href
                    ? 'bg-gray-800 text-white'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`}
              >
                {link.label}
              </Link>
            ))}

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="ml-4 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 transition-colors flex items-center gap-2"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
              로그아웃
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
