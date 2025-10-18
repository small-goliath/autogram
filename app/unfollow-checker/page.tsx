'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import Container from '@/components/layout/Container';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import { publicApi, UnfollowerCheckResponse } from '@/lib/api';

const unfollowerSchema = z.object({
  instagram_id: z
    .string()
    .min(1, 'Instagram ID를 입력해주세요')
    .regex(/^[a-zA-Z0-9._]+$/, 'Instagram ID 형식이 올바르지 않습니다'),
  instagram_password: z
    .string()
    .min(6, '비밀번호는 최소 6자 이상이어야 합니다')
    .max(100, '비밀번호가 너무 깁니다'),
});

type UnfollowerFormData = z.infer<typeof unfollowerSchema>;

export default function UnfollowCheckerPage() {
  const [isChecking, setIsChecking] = useState(false);
  const [results, setResults] = useState<UnfollowerCheckResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<UnfollowerFormData>({
    resolver: zodResolver(unfollowerSchema),
  });

  const onSubmit = async (data: UnfollowerFormData) => {
    setIsChecking(true);
    setError(null);
    setResults(null);

    try {
      const response = await publicApi.checkUnfollowers({
        instagram_id: data.instagram_id,
        instagram_password: data.instagram_password,
      });

      setResults(response.data);
    } catch (err: any) {
      console.error('Failed to check unfollowers:', err);
      setError(
        err.response?.data?.detail ||
        '언팔로워 확인에 실패했습니다. 계정 정보를 확인하고 다시 시도해주세요.'
      );
    } finally {
      setIsChecking(false);
    }
  };

  return (
    <Container>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">언팔로워 확인</h1>
        <p className="text-gray-600">나를 언팔로우한 사람들을 찾아보세요</p>
      </div>

      <div className="max-w-2xl mx-auto">
        {error && (
          <Card className="mb-6 bg-red-50 border-red-200">
            <div className="flex items-center gap-3">
              <div className="text-2xl">⚠️</div>
              <div>
                <h3 className="font-semibold text-red-900">확인 실패</h3>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          </Card>
        )}

        <Card className="mb-6 bg-blue-50 border-blue-200">
          <div className="flex items-start gap-3">
            <div className="text-2xl">ℹ️</div>
            <div>
              <h3 className="font-semibold text-blue-900 mb-2">안내사항</h3>
              <ul className="space-y-1 text-sm text-blue-800">
                <li className="flex items-start gap-2">
                  <span className="mt-1">•</span>
                  <span>이 도구는 일회성으로 사용되며 계정 정보를 저장하지 않습니다.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1">•</span>
                  <span>팔로워 및 팔로잉 목록을 비교하여 언팔로워를 찾습니다.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1">•</span>
                  <span>확인 과정은 몇 분 정도 소요될 수 있습니다.</span>
                </li>
              </ul>
            </div>
          </div>
        </Card>

        <Card>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <Input
                label="Instagram ID"
                placeholder="your_instagram_id"
                error={errors.instagram_id?.message}
                disabled={isChecking}
                {...register('instagram_id')}
              />
              <p className="mt-1 text-sm text-gray-500">
                @ 없이 Instagram ID만 입력해주세요
              </p>
            </div>

            <div>
              <Input
                type="password"
                label="Instagram 비밀번호"
                placeholder="비밀번호를 입력하세요"
                error={errors.instagram_password?.message}
                disabled={isChecking}
                {...register('instagram_password')}
              />
              <p className="mt-1 text-sm text-gray-500">
                비밀번호는 저장되지 않으며 일회성으로만 사용됩니다
              </p>
            </div>

            <Button
              type="submit"
              isLoading={isChecking}
              className="w-full"
              size="lg"
            >
              {isChecking ? '확인 중...' : '언팔로워 확인'}
            </Button>
          </form>
        </Card>

        {isChecking && (
          <Card className="mt-6 bg-yellow-50 border-yellow-200">
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-yellow-600"></div>
              <div>
                <h3 className="font-semibold text-yellow-900">확인 중</h3>
                <p className="text-yellow-700 text-sm">
                  팔로워 및 팔로잉 목록을 분석하고 있습니다. 잠시만 기다려주세요...
                </p>
              </div>
            </div>
          </Card>
        )}

        {results && (
          <Card className="mt-6">
            <div className="mb-4">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                확인 결과
              </h3>
              <p className="text-gray-600">
                총 <span className="font-bold text-blue-600">{results.total_count}명</span>이
                당신을 언팔로우했습니다.
              </p>
            </div>

            {results.total_count === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-3">🎉</div>
                <p className="text-gray-600">
                  언팔로우한 사람이 없습니다!
                </p>
              </div>
            ) : (
              <div className="mt-4">
                <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <ul className="space-y-2">
                    {results.unfollowers.map((username, index) => (
                      <li
                        key={index}
                        className="flex items-center justify-between bg-white px-4 py-3 rounded-lg shadow-sm"
                      >
                        <span className="font-medium text-gray-900">
                          @{username}
                        </span>
                        <a
                          href={`https://www.instagram.com/${username}/`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 text-sm"
                        >
                          프로필 보기
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </Card>
        )}

        <Card className="mt-6 bg-red-50 border-red-200">
          <h3 className="font-semibold text-red-900 mb-2">주의사항</h3>
          <ul className="space-y-2 text-sm text-red-800">
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>2단계 인증(2FA)이 활성화되어 있으면 확인이 실패할 수 있습니다.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>과도한 사용은 Instagram의 제한을 받을 수 있습니다.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>개인 계정이거나 차단된 계정은 목록에 표시되지 않을 수 있습니다.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>결과는 확인 시점 기준이며 실시간으로 변경될 수 있습니다.</span>
            </li>
          </ul>
        </Card>
      </div>
    </Container>
  );
}
