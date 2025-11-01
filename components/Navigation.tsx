'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const publicTabs = [
  { name: '공지사항', href: '/' },
  { name: '지난주 현황', href: '/last-week' },
  { name: 'SNS 키우기 품앗이 현황', href: '/verification' },
  { name: '[AI] 자동 댓글 받기 신청', href: '/consumer' },
  { name: '[AI] 자동 댓글 달기 신청', href: '/producer' },
  { name: '인스타 언팔검색기', href: '/unfollow-checker' },
];

export const Navigation: React.FC = () => {
  const pathname = usePathname();

  return (
    <nav className="bg-white border-b-2 border-gray-200 overflow-x-auto">
      <div className="flex">
        {publicTabs.map((tab) => {
          const isActive = pathname === tab.href;
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={cn(
                'px-6 py-4 text-sm font-medium whitespace-nowrap transition-all border-b-3',
                isActive
                  ? 'text-primary-500 font-semibold border-primary-500 bg-primary-50/30'
                  : 'text-gray-600 border-transparent hover:text-gray-900 hover:bg-gray-50'
              )}
            >
              {tab.name}
            </Link>
          );
        })}
      </div>
    </nav>
  );
};
