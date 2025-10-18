'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { adminApi, type SnsUser } from '@/lib/api';
import Container from '@/components/layout/Container';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';

const userSchema = z.object({
  username: z.string().min(1, '사용자명을 입력해주세요'),
  instagram_id: z.string().min(1, 'Instagram ID를 입력해주세요'),
  email: z.string().email('올바른 이메일을 입력해주세요'),
  is_active: z.boolean(),
});

type UserFormData = z.infer<typeof userSchema>;

type ModalState = {
  type: 'create' | 'edit' | 'delete' | null;
  user?: SnsUser;
};

export default function AdminUsersPage() {
  const router = useRouter();
  const [users, setUsers] = useState<SnsUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [modalState, setModalState] = useState<ModalState>({ type: null });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
  } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues: {
      username: '',
      instagram_id: '',
      email: '',
      is_active: true,
    },
  });

  useEffect(() => {
    // Check for authentication token
    const token = localStorage.getItem('auth_token');
    if (!token) {
      router.push('/admin/login');
      return;
    }

    fetchUsers();
  }, [router]);

  const fetchUsers = async () => {
    try {
      setIsLoading(true);
      const response = await adminApi.getSnsUsers();
      setUsers(response.data);
      setError('');
    } catch (err: any) {
      console.error('Failed to fetch users:', err);
      if (err.response?.status === 401) {
        localStorage.removeItem('auth_token');
        router.push('/admin/login');
      } else {
        setError('사용자 목록을 불러오는데 실패했습니다');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const openCreateModal = () => {
    reset({
      username: '',
      instagram_id: '',
      email: '',
      is_active: true,
    });
    setModalState({ type: 'create' });
  };

  const openEditModal = (user: SnsUser) => {
    reset({
      username: user.username,
      instagram_id: user.instagram_id,
      email: user.email,
      is_active: user.is_active,
    });
    setModalState({ type: 'edit', user });
  };

  const openDeleteModal = (user: SnsUser) => {
    setModalState({ type: 'delete', user });
  };

  const closeModal = () => {
    setModalState({ type: null });
    reset();
  };

  const onSubmit = async (data: UserFormData) => {
    setIsSubmitting(true);
    setError('');

    try {
      if (modalState.type === 'create') {
        await adminApi.createSnsUser(data);
      } else if (modalState.type === 'edit' && modalState.user) {
        await adminApi.updateSnsUser(modalState.user.id, data);
      }

      await fetchUsers();
      closeModal();
    } catch (err: any) {
      console.error('Failed to save user:', err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('사용자 저장에 실패했습니다');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!modalState.user) return;

    setIsSubmitting(true);
    setError('');

    try {
      await adminApi.deleteSnsUser(modalState.user.id);
      await fetchUsers();
      closeModal();
    } catch (err: any) {
      console.error('Failed to delete user:', err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('사용자 삭제에 실패했습니다');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <Container>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-gray-600">로딩 중...</div>
        </div>
      </Container>
    );
  }

  return (
    <Container>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">SNS 사용자 관리</h1>
            <p className="mt-2 text-gray-600">Instagram 사용자 계정을 관리합니다</p>
          </div>
          <Button onClick={openCreateModal}>새 사용자 추가</Button>
        </div>

        {error && !modalState.type && (
          <Card variant="bordered" className="border-red-300 bg-red-50">
            <p className="text-red-600">{error}</p>
          </Card>
        )}

        <Card>
          {users.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600">등록된 사용자가 없습니다</p>
              <Button onClick={openCreateModal} className="mt-4">첫 사용자 추가하기</Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>사용자명</TableHead>
                  <TableHead>Instagram ID</TableHead>
                  <TableHead>이메일</TableHead>
                  <TableHead>상태</TableHead>
                  <TableHead>생성일</TableHead>
                  <TableHead>작업</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.id}</TableCell>
                    <TableCell className="font-medium">{user.username}</TableCell>
                    <TableCell>{user.instagram_id}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          user.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {user.is_active ? '활성' : '비활성'}
                      </span>
                    </TableCell>
                    <TableCell>
                      {new Date(user.created_at).toLocaleDateString('ko-KR')}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => openEditModal(user)}
                        >
                          수정
                        </Button>
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => openDeleteModal(user)}
                        >
                          삭제
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </Card>
      </div>

      {/* Modal Overlay */}
      {modalState.type && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900">
                  {modalState.type === 'create' && '새 사용자 추가'}
                  {modalState.type === 'edit' && '사용자 정보 수정'}
                  {modalState.type === 'delete' && '사용자 삭제'}
                </h2>
                <button
                  onClick={closeModal}
                  className="text-gray-400 hover:text-gray-600"
                  disabled={isSubmitting}
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {error && modalState.type && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              {modalState.type === 'delete' ? (
                <div>
                  <p className="text-gray-700 mb-4">
                    정말로 <strong>{modalState.user?.username}</strong> 사용자를 삭제하시겠습니까?
                    이 작업은 되돌릴 수 없습니다.
                  </p>
                  <div className="flex gap-3">
                    <Button
                      variant="danger"
                      onClick={handleDelete}
                      isLoading={isSubmitting}
                      className="flex-1"
                    >
                      삭제
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={closeModal}
                      disabled={isSubmitting}
                      className="flex-1"
                    >
                      취소
                    </Button>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  <Input
                    label="사용자명"
                    placeholder="사용자명을 입력하세요"
                    error={errors.username?.message}
                    {...register('username')}
                  />

                  <Input
                    label="Instagram ID"
                    placeholder="Instagram ID를 입력하세요"
                    error={errors.instagram_id?.message}
                    {...register('instagram_id')}
                  />

                  <Input
                    label="이메일"
                    type="email"
                    placeholder="이메일을 입력하세요"
                    error={errors.email?.message}
                    {...register('email')}
                  />

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="is_active"
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      {...register('is_active')}
                    />
                    <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
                      활성 상태
                    </label>
                  </div>

                  <div className="flex gap-3 pt-2">
                    <Button
                      type="submit"
                      isLoading={isSubmitting}
                      className="flex-1"
                    >
                      {modalState.type === 'create' ? '추가' : '수정'}
                    </Button>
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={closeModal}
                      disabled={isSubmitting}
                      className="flex-1"
                    >
                      취소
                    </Button>
                  </div>
                </form>
              )}
            </div>
          </Card>
        </div>
      )}
    </Container>
  );
}
