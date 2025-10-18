'use client';

import { useEffect, useState } from 'react';
import Container from '@/components/layout/Container';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { publicApi, RequestByWeek } from '@/lib/api';

export default function RequestsPage() {
  const [data, setData] = useState<RequestByWeek[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usernameFilter, setUsernameFilter] = useState('');

  const fetchData = async (username?: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await publicApi.getRequestsByWeek(username || undefined);
      setData(response.data);
    } catch (err) {
      console.error('Failed to fetch requests:', err);
      setError('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setUsernameFilter(value);

    // Debounce the API call
    const timeoutId = setTimeout(() => {
      fetchData(value);
    }, 500);

    return () => clearTimeout(timeoutId);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; className: string }> = {
      pending: { label: '대기중', className: 'bg-yellow-100 text-yellow-800' },
      completed: { label: '완료', className: 'bg-green-100 text-green-800' },
      failed: { label: '실패', className: 'bg-red-100 text-red-800' },
    };

    const statusInfo = statusMap[status] || { label: status, className: 'bg-gray-100 text-gray-800' };

    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${statusInfo.className}`}>
        {statusInfo.label}
      </span>
    );
  };

  return (
    <Container>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">지난주 현황</h1>
        <p className="text-gray-600">지난주 제출된 Instagram 링크를 확인하세요</p>
      </div>

      <Card>
        <div className="mb-6">
          <Input
            type="text"
            placeholder="사용자 이름으로 검색..."
            value={usernameFilter}
            onChange={handleFilterChange}
            label="사용자 이름 필터"
          />
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">데이터를 불러오는 중...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-600">{error}</p>
          </div>
        ) : data.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">표시할 데이터가 없습니다.</p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>사용자명</TableHead>
                <TableHead>Instagram 링크</TableHead>
                <TableHead>제출 날짜</TableHead>
                <TableHead>주차</TableHead>
                <TableHead>상태</TableHead>
                <TableHead>댓글 수</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((request) => (
                <TableRow key={request.id}>
                  <TableCell className="font-medium">{request.username}</TableCell>
                  <TableCell>
                    <a
                      href={request.instagram_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 hover:underline"
                    >
                      {request.instagram_link.length > 40
                        ? `${request.instagram_link.substring(0, 40)}...`
                        : request.instagram_link}
                    </a>
                  </TableCell>
                  <TableCell>{formatDate(request.request_date)}</TableCell>
                  <TableCell className="text-sm text-gray-500">
                    {formatDate(request.week_start_date)} - {formatDate(request.week_end_date)}
                  </TableCell>
                  <TableCell>{getStatusBadge(request.status)}</TableCell>
                  <TableCell>
                    <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                      {request.comment_count}
                    </span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}

        {data.length > 0 && (
          <div className="mt-4 text-sm text-gray-600">
            총 {data.length}개의 요청
          </div>
        )}
      </Card>
    </Container>
  );
}
