'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { adminApi } from '@/lib/api';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';

const loginSchema = z.object({
  username: z.string().min(1, '사용자명을 입력해주세요'),
  password: z.string().min(1, '비밀번호를 입력해주세요'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function AdminLoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    setError('');

    try {
      const response = await adminApi.login(data.username, data.password);

      // Save token to localStorage
      localStorage.setItem('auth_token', response.data.access_token);

      // Redirect to admin dashboard
      router.push('/admin');
    } catch (err: any) {
      console.error('Login error:', err);

      if (err.response?.status === 401) {
        setError('사용자명 또는 비밀번호가 올바르지 않습니다');
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('로그인 중 오류가 발생했습니다');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Autogram</h1>
          <p className="mt-2 text-gray-600">관리자 로그인</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <Input
            label="사용자명"
            placeholder="사용자명을 입력하세요"
            error={errors.username?.message}
            {...register('username')}
          />

          <Input
            type="password"
            label="비밀번호"
            placeholder="비밀번호를 입력하세요"
            error={errors.password?.message}
            {...register('password')}
          />

          <Button
            type="submit"
            className="w-full"
            isLoading={isLoading}
          >
            로그인
          </Button>
        </form>
      </Card>
    </div>
  );
}
