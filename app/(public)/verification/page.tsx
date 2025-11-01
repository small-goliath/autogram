'use client';

import { Alert } from '@/components/ui/Alert';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';
import { useEffect, useState, useMemo } from 'react';

interface Verification {
  id: number;
  username: string;
  instagram_link: string;
  link_owner_username: string;
  created_at: string;
}

// KST (Korea Standard Time) 형식으로 날짜 변환
const formatToKST = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleString('ko-KR', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });
};

// Instagram URL을 단축 형식으로 변환
const formatInstagramUrl = (url: string): string => {
  try {
    const match = url.match(/instagram\.com\/(p|reel)\/([^/?]+)/);
    if (match) {
      const [, type, shortcode] = match;
      return `instagram.com/${type}/${shortcode}`;
    }
    return url;
  } catch {
    return url;
  }
};

export default function VerificationPage() {
  const [verifications, setVerifications] = useState<Verification[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const fetchVerifications = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/user-action-verification?limit=1000');
        setVerifications(response.data || []);
      } catch (err: any) {
        setError(err.message || '검증 내역 조회에 실패했습니다');
      } finally {
        setIsLoading(false);
      }
    };

    fetchVerifications();
  }, []);

  // 미작성자(username)로만 필터링
  const filteredVerifications = useMemo(() => {
    if (!searchQuery.trim()) {
      return verifications;
    }

    const query = searchQuery.toLowerCase().trim();
    return verifications.filter(verification =>
      verification.username.toLowerCase().includes(query)
    );
  }, [verifications, searchQuery]);

  // 사용자별로 그룹화 (미작성 건수가 많은 순서로 정렬)
  const groupedByUser = useMemo(() => {
    const groups: Record<string, Verification[]> = {};

    filteredVerifications.forEach(verification => {
      if (!groups[verification.username]) {
        groups[verification.username] = [];
      }
      groups[verification.username].push(verification);
    });

    // 미작성 건수가 많은 순서로 정렬
    return Object.entries(groups).sort((a, b) => b[1].length - a[1].length);
  }, [filteredVerifications]);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            ⚠️ 댓글 미작성자 현황
          </h1>
          <p className="text-lg text-gray-600">
            댓글을 작성하지 않은 사용자를 확인하세요
          </p>
        </div>

        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        {/* 검색창 */}
        {!isLoading && verifications.length > 0 && (
          <div className="mb-6">
            <Input
              type="text"
              placeholder="사용자명으로 검색(부분검색 가능)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="max-w-md"
            />
            <p className="text-sm text-gray-500 mt-2">
              미작성자 수: {groupedByUser.length}명 / 총 미작성 건: {filteredVerifications.length}개
              {searchQuery && ` (전체: ${verifications.length}개)`}
            </p>
          </div>
        )}

        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p className="mt-4 text-gray-600">미작성자 불러오는 중...</p>
          </div>
        ) : verifications.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <svg
                className="mx-auto h-16 w-16 text-gray-400 mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-gray-600">모두 댓글을 작성했습니다! 🎉</p>
            </div>
          </Card>
        ) : filteredVerifications.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <svg
                className="mx-auto h-16 w-16 text-gray-400 mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              <p className="text-gray-600">"{searchQuery}"에 대한 검색 결과가 없습니다</p>
              <button
                onClick={() => setSearchQuery('')}
                className="mt-4 text-blue-600 hover:underline"
              >
                검색 초기화
              </button>
            </div>
          </Card>
        ) : (
          <div className="space-y-4">
            {groupedByUser.map(([username, userVerifications]) => (
              <Card key={username}>
                <div className="mb-4 pb-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-bold text-gray-900">@{username}</span>
                      <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold">
                        미작성 {userVerifications.length}건
                      </span>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  {userVerifications.map((verification) => (
                    <div
                      key={verification.id}
                      className="pl-4 border-l-2 border-gray-200 hover:border-blue-400 transition-colors"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs text-gray-500">링크 소유자:</span>
                        <span className="text-sm font-medium text-gray-700">
                          @{verification.link_owner_username}
                        </span>
                      </div>
                      <a
                        href={verification.instagram_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:underline break-all"
                        title={verification.instagram_link}
                      >
                        {formatInstagramUrl(verification.instagram_link)}
                      </a>
                      <p className="text-xs text-gray-400 mt-1">
                        기록: {formatToKST(verification.created_at)}
                      </p>
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
