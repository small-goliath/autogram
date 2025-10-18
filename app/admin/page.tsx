'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { adminApi, type Admin } from '@/lib/api';
import Container from '@/components/layout/Container';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';

export default function AdminDashboardPage() {
  const router = useRouter();
  const [admin, setAdmin] = useState<Admin | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    // Check for authentication token
    const token = localStorage.getItem('auth_token');
    if (!token) {
      router.push('/admin/login');
      return;
    }

    // Fetch admin info
    const fetchAdminInfo = async () => {
      try {
        const response = await adminApi.getMe();
        setAdmin(response.data);
      } catch (err: any) {
        console.error('Failed to fetch admin info:', err);
        if (err.response?.status === 401) {
          // Token is invalid, redirect to login
          localStorage.removeItem('auth_token');
          router.push('/admin/login');
        } else {
          setError('관리자 정보를 불러오는데 실패했습니다');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchAdminInfo();
  }, [router]);

  if (isLoading) {
    return (
      <Container>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-gray-600">로딩 중...</div>
        </div>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Card>
          <div className="text-center text-red-600">{error}</div>
        </Card>
      </Container>
    );
  }

  if (!admin) {
    return null;
  }

  return (
    <Container>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">관리자 대시보드</h1>
          <p className="mt-2 text-gray-600">Autogram 관리자 페이지에 오신 것을 환영합니다</p>
        </div>

        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">관리자 정보</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between py-2 border-b border-gray-100">
              <span className="text-gray-600">사용자명</span>
              <span className="font-medium text-gray-900">{admin.username}</span>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-gray-100">
              <span className="text-gray-600">이메일</span>
              <span className="font-medium text-gray-900">{admin.email}</span>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-gray-100">
              <span className="text-gray-600">권한</span>
              <span className="font-medium text-gray-900">
                {admin.is_superadmin ? '슈퍼관리자' : '관리자'}
              </span>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-gray-100">
              <span className="text-gray-600">상태</span>
              <span className={`font-medium ${admin.is_active ? 'text-green-600' : 'text-red-600'}`}>
                {admin.is_active ? '활성' : '비활성'}
              </span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-gray-600">마지막 로그인</span>
              <span className="font-medium text-gray-900">
                {admin.last_login_at ? new Date(admin.last_login_at).toLocaleString('ko-KR') : '정보 없음'}
              </span>
            </div>
          </div>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">SNS 사용자 관리</h3>
            <p className="text-gray-600 mb-4">
              Instagram 사용자 계정을 생성, 수정, 삭제할 수 있습니다
            </p>
            <Link href="/admin/users">
              <Button>사용자 관리 페이지로 이동</Button>
            </Link>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">헬퍼 관리</h3>
            <p className="text-gray-600 mb-4">
              Instagram 헬퍼 계정을 등록하고 관리할 수 있습니다
            </p>
            <Button disabled variant="secondary">
              준비 중
            </Button>
          </Card>
        </div>
      </div>
    </Container>
  );
}
