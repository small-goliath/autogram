'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Alert } from '@/components/ui/Alert';
import { Badge } from '@/components/ui/Badge';
import { api } from '@/lib/api';

type ConsumerStatus = 'pending' | 'active' | 'inactive';

export default function ConsumerPage() {
  const [username, setUsername] = useState('');
  const [status, setStatus] = useState<{
    consumer?: { status: ConsumerStatus; created_at: string };
    exists: boolean;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleRegister = async () => {
    if (!username.trim()) {
      setError('인스타그램 사용자명을 입력해주세요');
      return;
    }

    try {
      setIsLoading(true);
      setError('');
      setSuccess('');

      const response = await api.post('/consumer/register', {
        instagram_username: username
      });

      setSuccess('등록 완료! 자동 댓글을 받게 됩니다.');
      setStatus({ consumer: response.data, exists: true });
    } catch (err: any) {
      setError(err.message || '등록에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCheckStatus = async () => {
    if (!username.trim()) {
      setError('인스타그램 사용자명을 입력해주세요');
      return;
    }

    try {
      setIsLoading(true);
      setError('');
      setSuccess('');

      const response = await api.get(`/consumer/${username}`);
      setStatus(response.data);
    } catch (err: any) {
      setError(err.message || '현황 조회에 실패했습니다');
      setStatus(null);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: ConsumerStatus) => {
    const variants = {
      active: 'success' as const,
      pending: 'warning' as const,
      inactive: 'secondary' as const
    };
    const labels = {
      active: '활성',
      pending: '대기중',
      inactive: '비활성'
    };
    return <Badge variant={variants[status]}>{labels[status]}</Badge>;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            🤖 AI 자동 댓글 받기
          </h1>
          <p className="text-lg text-gray-600 mb-4">
            인스타그램 게시물에 자동 댓글을 받으려면 등록하세요
          </p>
          <Alert variant="info">
            <strong>어떻게 작동하나요:</strong> AI 봇이 자동으로 게시물에 댓글을 달아 참여도를 높여줍니다.
          </Alert>
        </div>

        <Card className="mb-6">
          <div className="space-y-4">
            <Input
              label="인스타그램 사용자명"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="인스타그램 사용자명을 입력하세요"
            />

            <div className="grid grid-cols-2 gap-3">
              <Button
                variant="secondary"
                fullWidth
                onClick={handleCheckStatus}
                isLoading={isLoading}
              >
                현황 조회
              </Button>
              <Button
                variant="primary"
                fullWidth
                onClick={handleRegister}
                isLoading={isLoading}
              >
                등록하기
              </Button>
            </div>
          </div>
        </Card>

        {error && <Alert variant="error" className="mb-6">{error}</Alert>}
        {success && <Alert variant="success" className="mb-6">{success}</Alert>}

        {status && status.exists && status.consumer && (
          <Card>
            <h2 className="text-xl font-bold mb-4">등록 현황</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b">
                <span className="text-gray-600">사용자명:</span>
                <span className="font-medium">@{username}</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b">
                <span className="text-gray-600">상태:</span>
                {getStatusBadge(status.consumer.status)}
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-gray-600">등록일:</span>
                <span className="text-sm text-gray-500">
                  {new Date(status.consumer.created_at).toLocaleString()}
                </span>
              </div>
            </div>
          </Card>
        )}

        {status && !status.exists && (
          <Alert variant="warning">
            이 사용자명으로 등록된 내역이 없습니다. "등록하기"를 클릭하여 가입하세요!
          </Alert>
        )}
      </div>
    </div>
  );
}
