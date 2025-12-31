'use client';

import { Alert } from '@/components/ui/Alert';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { deleteUnfollowerServiceUser, getErrorMessage, getUnfollowers } from '@/lib/api';
import type { Unfollower, UnfollowersResponse } from '@/types';
import Image from 'next/image';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function UnfollowerListPage() {
  const params = useParams();
  const router = useRouter();
  const owner = params.owner as string;

  const [data, setData] = useState<UnfollowersResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState('');
  const [deleteSuccess, setDeleteSuccess] = useState('');

  useEffect(() => {
    const fetchUnfollowers = async () => {
      try {
        setIsLoading(true);
        setError('');
        const response = await getUnfollowers(owner);
        setData(response);
      } catch (err: any) {
        setError(err.message || '언팔로워 목록을 불러오는데 실패했습니다');
      } finally {
        setIsLoading(false);
      }
    };

    if (owner) {
      fetchUnfollowers();
    }
  }, [owner]);

  const handleDelete = async () => {
    const confirmed = window.confirm(
      `정말로 @${owner} 계정을 삭제하시겠습니까?\n\n등록된 계정 정보와 모든 언팔로워 목록이 삭제됩니다.\n이 작업은 되돌릴 수 없습니다.`
    );

    if (!confirmed) return;

    try {
      setIsDeleting(true);
      setError('');
      const response = await deleteUnfollowerServiceUser(owner);
      setDeleteSuccess(response.message);

      // Redirect to main page after 2 seconds
      setTimeout(() => {
        router.push('/unfollow-checker');
      }, 2000);
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">언팔로워 목록을 불러오는 중...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <Link
            href="/unfollow-checker"
            className="text-blue-600 hover:text-blue-800 mb-4 inline-block"
          >
            ← 돌아가기
          </Link>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-3">
                🔍 언팔로워 목록
              </h1>
              <p className="text-lg text-gray-600">
                @{owner}님의 언팔로워
              </p>
            </div>
            {data && (
              <Button
                variant="danger"
                onClick={handleDelete}
                isLoading={isDeleting}
                className="ml-4"
              >
                계정 삭제
              </Button>
            )}
          </div>
        </div>

        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        {deleteSuccess && (
          <Alert variant="success" className="mb-6">
            {deleteSuccess}
          </Alert>
        )}

        {data && (
          <>
            <Card className="mb-6 bg-blue-50 border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-blue-900">
                    총 {data.count}명의 언팔로워
                  </h2>
                  <p className="text-sm text-blue-700 mt-1">
                    나를 팔로우하지 않는 계정 목록입니다.
                  </p>
                </div>
              </div>
            </Card>

            {data.unfollowers.length === 0 ? (
              <Card className="text-center py-12">
                <p className="text-gray-600 text-lg">
                  🎉 언팔로워가 없습니다!
                </p>
                <p className="text-gray-500 text-sm mt-2">
                  모든 사람이 나를 팔로우하고 있습니다.
                </p>
              </Card>
            ) : (
              <div className="grid gap-4">
                {data.unfollowers.map((unfollower: Unfollower) => (
                  <Card
                    key={unfollower.unfollower_username}
                    className="hover:shadow-lg transition-shadow"
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex-shrink-0">
                        <Image
                          src={unfollower.unfollower_profile_url}
                          alt={unfollower.unfollower_username}
                          width={60}
                          height={60}
                          className="rounded-full"
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <a
                          href={`https://www.instagram.com/${unfollower.unfollower_username}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-lg font-semibold text-gray-900 hover:text-blue-600"
                        >
                          @{unfollower.unfollower_username}
                        </a>
                        <p className="text-sm text-gray-600 truncate">
                          {unfollower.unfollower_fullname}
                        </p>
                        {unfollower.updated_at && (
                          <p className="text-xs text-gray-400 mt-1">
                            업데이트: {new Date(unfollower.updated_at).toLocaleDateString('ko-KR')}
                          </p>
                        )}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
