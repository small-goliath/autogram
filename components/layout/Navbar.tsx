'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const Navbar = () => {
  const pathname = usePathname();

  const isAdmin = pathname?.startsWith('/admin');

  const publicLinks = [
    { href: '/', label: '홈' },
    { href: '/requests', label: '지난주 현황' },
    { href: '/verification', label: '품앗이 현황' },
    { href: '/consumer', label: 'AI 댓글 받기' },
    { href: '/producer', label: 'AI 댓글 달기' },
    { href: '/unfollow-checker', label: '언팔로워 확인' },
  ];

  const adminLinks = [
    { href: '/admin', label: '대시보드' },
    { href: '/admin/users', label: 'SNS 사용자 관리' },
  ];

  const links = isAdmin ? adminLinks : publicLinks;

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link href="/" className="flex items-center">
              <span className="text-2xl font-bold text-blue-600">Autogram</span>
            </Link>
            <div className="hidden sm:ml-8 sm:flex sm:space-x-4">
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    'inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                    pathname === link.href
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                  )}
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
          {isAdmin && (
            <div className="flex items-center">
              <button
                onClick={() => {
                  localStorage.removeItem('auth_token');
                  window.location.href = '/admin/login';
                }}
                className="text-sm font-medium text-gray-700 hover:text-red-600"
              >
                로그아웃
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
