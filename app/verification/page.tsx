'use client';

import { useEffect, useState } from 'react';
import Container from '@/components/layout/Container';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { publicApi, UserActionVerification } from '@/lib/api';

export default function VerificationPage() {
  const [data, setData] = useState<UserActionVerification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usernameFilter, setUsernameFilter] = useState('');

  const fetchData = async (username?: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await publicApi.getUserActionVerification(username || undefined);
      setData(response.data);
    } catch (err) {
      console.error('Failed to fetch verification data:', err);
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

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const uncommentedCount = data.filter(item => !item.is_commented).length;

  return (
    <Container>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">품앗이 현황</h1>
        <p className="text-gray-600">댓글 작성 상태 및 미작성자를 확인하세요</p>
      </div>

      {uncommentedCount > 0 && (
        <Card className="mb-6 bg-red-50 border-red-200">
          <div className="flex items-center gap-3">
            <div className="text-2xl">⚠️</div>
            <div>
              <h3 className="font-semibold text-red-900">미작성 알림</h3>
              <p className="text-red-700 text-sm">
                {uncommentedCount}명의 사용자가 아직 댓글을 작성하지 않았습니다.
              </p>
            </div>
          </div>
        </Card>
      )}

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
                <TableHead>링크 소유자</TableHead>
                <TableHead>댓글 작성 여부</TableHead>
                <TableHead>확인 시간</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((item) => (
                <TableRow
                  key={item.id}
                  className={!item.is_commented ? 'bg-red-50 hover:bg-red-100' : ''}
                >
                  <TableCell className="font-medium">{item.username}</TableCell>
                  <TableCell>
                    <a
                      href={item.instagram_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 hover:underline"
                    >
                      {item.instagram_link.length > 40
                        ? `${item.instagram_link.substring(0, 40)}...`
                        : item.instagram_link}
                    </a>
                  </TableCell>
                  <TableCell className="font-medium">{item.link_owner_username}</TableCell>
                  <TableCell>
                    {item.is_commented ? (
                      <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                        ✓ 작성 완료
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800">
                        ✗ 미작성
                      </span>
                    )}
                  </TableCell>
                  <TableCell className="text-sm text-gray-600">
                    {formatDateTime(item.verified_at)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}

        {data.length > 0 && (
          <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
            <div>총 {data.length}개의 항목</div>
            <div>
              <span className="text-green-600 font-medium">
                작성 완료: {data.filter(item => item.is_commented).length}
              </span>
              {' / '}
              <span className="text-red-600 font-medium">
                미작성: {uncommentedCount}
              </span>
            </div>
          </div>
        )}
      </Card>
    </Container>
  );
}
