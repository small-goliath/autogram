'use client';

import { Alert } from '@/components/ui/Alert';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { createConsumer, deleteConsumer, getConsumer, getErrorMessage } from '@/lib/api';
import type { Consumer } from '@/types';
import { useState } from 'react';

export default function ConsumerPage() {
  const [username, setUsername] = useState('');
  const [viewUsername, setViewUsername] = useState('');
  const [consumerData, setConsumerData] = useState<Consumer | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
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

      await createConsumer({ instagram_username: username });

      setSuccess('AI 자동 댓글 받기 신청이 완료되었습니다!');

      // Reset form
      setUsername('');
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewConsumer = async () => {
    if (!viewUsername) {
      setError('사용자명을 입력해주세요');
      return;
    }

    try {
      setIsLoading(true);
      setError('');
      setSuccess('');
      const data = await getConsumer(viewUsername);
      setConsumerData(data);
    } catch (err: any) {
      setError(getErrorMessage(err));
      setConsumerData(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!consumerData) return;

    const confirmed = window.confirm(
      `정말로 @${consumerData.instagram_username} 계정을 삭제하시겠습니까?\n\n등록된 계정 정보가 삭제됩니다.\n이 작업은 되돌릴 수 없습니다.`
    );

    if (!confirmed) return;

    try {
      setIsDeleting(true);
      setError('');
      const response = await deleteConsumer(consumerData.instagram_username);
      setSuccess(response.message);
      setConsumerData(null);
      setViewUsername('');
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setIsDeleting(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusMap: { [key: string]: { variant: 'success' | 'warning' | 'gray'; label: string } } = {
      active: { variant: 'success', label: '활성' },
      pending: { variant: 'warning', label: '대기중' },
      inactive: { variant: 'gray', label: '비활성' }
    };
    const statusInfo = statusMap[status] || { variant: 'gray' as const, label: status };
    return <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>;
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

        <Card className="mb-6 bg-green-50 border-green-200">
          <h3 className="font-semibold text-green-900 mb-2">
            📋 이미 등록하셨나요?
          </h3>
          <p className="text-sm text-green-700 mb-3">
            등록된 계정 정보를 확인하려면 아래에 사용자명을 입력하세요:
          </p>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="사용자명 입력"
              value={viewUsername}
              onChange={(e) => setViewUsername(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && viewUsername) {
                  handleViewConsumer();
                }
              }}
              className="flex-1 px-3 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <Button
              variant="primary"
              onClick={handleViewConsumer}
              isLoading={isLoading}
            >
              조회
            </Button>
          </div>
        </Card>

        {consumerData && (
          <Card className="mb-6 bg-blue-50 border-blue-200">
            <div className="flex items-start justify-between mb-4">
              <h3 className="font-semibold text-blue-900 text-lg">
                등록된 계정 정보
              </h3>
              <Button
                variant="danger"
                onClick={handleDelete}
                isLoading={isDeleting}
                className="text-sm"
              >
                계정 삭제
              </Button>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b border-blue-200">
                <span className="text-blue-700">사용자명:</span>
                <span className="font-medium text-blue-900">@{consumerData.instagram_username}</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-blue-200">
                <span className="text-blue-700">상태:</span>
                {getStatusBadge(consumerData.status)}
              </div>
              <div className="flex items-center justify-between py-2 border-blue-200">
                <span className="text-blue-700">등록일:</span>
                <span className="text-sm text-blue-800">
                  {new Date(consumerData.created_at).toLocaleDateString('ko-KR')}
                </span>
              </div>
            </div>
            {consumerData.status === 'pending' && (
              <Alert variant="warning" className="mt-4">
                등록이 관리자 승인 대기 중입니다.
              </Alert>
            )}
            {consumerData.status === 'active' && (
              <Alert variant="success" className="mt-4">
                계정이 활성화되어 자동 댓글을 받고 있습니다!
              </Alert>
            )}
          </Card>
        )}

        <Card className="mb-6">
          <h2 className="text-xl font-bold mb-4">댓글 수신자 등록</h2>
          <div className="space-y-4">
            <Input
              label="인스타그램 사용자명"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="인스타그램 사용자명을 입력하세요"
              required
            />

            <Button
              variant="primary"
              fullWidth
              onClick={handleRegister}
              isLoading={isLoading}
            >
              등록하기
            </Button>
          </div>
        </Card>

        {error && <Alert variant="error" className="mb-6">{error}</Alert>}
        {success && <Alert variant="success" className="mb-6">{success}</Alert>}

        {/* Info Section */}
        <Card className="mt-8 bg-blue-50 border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-2">
            💡 이용 안내:
          </h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li>• 인스타그램 사용자명만으로 간편하게 등록할 수 있습니다</li>
            <li>• AI가 자동으로 게시물에 자연스러운 댓글을 달아줍니다</li>
            <li>• 게시물의 참여도와 가시성이 향상됩니다</li>
            <li>• 커뮤니티 활동이 더욱 활발해집니다</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
