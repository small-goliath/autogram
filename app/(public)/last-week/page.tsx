'use client';

import { Alert } from '@/components/ui/Alert';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';
import { RequestByWeek } from '@/types';
import { useEffect, useMemo, useState } from 'react';

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

export default function LastWeekPage() {
  const [requests, setRequests] = useState<RequestByWeek[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const fetchRequests = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/request-by-week');
        setRequests(response.data || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load requests');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRequests();
  }, []);

  // Username으로 필터링
  const filteredRequests = useMemo(() => {
    if (!searchQuery.trim()) {
      return requests;
    }

    const query = searchQuery.toLowerCase().trim();
    return requests.filter(request =>
      request.username.toLowerCase().includes(query)
    );
  }, [requests, searchQuery]);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            📊 지난주 현황
          </h1>
          <p className="text-lg text-gray-600">
            지난주 인스타그램 링크 공유 요청을 확인하세요
          </p>
        </div>

        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        {/* 검색창 */}
        {!isLoading && requests.length > 0 && (
          <div className="mb-6">
            <Input
              type="text"
              placeholder="사용자명으로 검색(부분검색 가능)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="max-w-md"
            />
            <p className="text-sm text-gray-500 mt-2">
              총 공유 건: {filteredRequests.length}개
              {searchQuery && ` (전체: ${requests.length}개)`}
            </p>
          </div>
        )}

        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p className="mt-4 text-gray-600">요청 불러오는 중...</p>
          </div>
        ) : requests.length === 0 ? (
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
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <p className="text-gray-600">지난주 요청이 없습니다</p>
            </div>
          </Card>
        ) : filteredRequests.length === 0 ? (
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
            {filteredRequests.map((request) => (
              <Card key={request.id} hover>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        @{request.username}
                      </h3>
                      <Badge variant="info">
                        공유 날짜: {new Date(request.week_start_date).toLocaleDateString('ko-KR')}
                      </Badge>
                    </div>
                    <a
                      href={request.instagram_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline break-all"
                    >
                      {request.instagram_link}
                    </a>
                    <p className="text-sm text-gray-500 mt-2">
                      서버 반영일자: {formatToKST(request.created_at)}
                    </p>
                  </div>
                  <svg
                    className="w-6 h-6 text-gray-400 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7l5 5m0 0l-5 5m5-5H6"
                    />
                  </svg>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
