'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Alert } from '@/components/ui/Alert';
import { Badge } from '@/components/ui/Badge';
import { api } from '@/lib/api';

type ProducerStatus = 'pending' | 'active' | 'inactive';

export default function ProducerPage() {
  const [formData, setFormData] = useState({
    instagram_username: '',
    instagram_password: '',
    verification_code: ''
  });
  const [status, setStatus] = useState<{
    producer?: {
      status: ProducerStatus;
      created_at: string;
      verification_code?: string;
    };
    exists: boolean;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleRegister = async () => {
    if (!formData.instagram_username || !formData.instagram_password) {
      setError('모든 필수 항목을 입력해주세요');
      return;
    }

    try {
      setIsLoading(true);
      setError('');
      setSuccess('');

      const response = await api.post('/producer/register', {
        instagram_username: formData.instagram_username,
        instagram_password: formData.instagram_password,
        verification_code: formData.verification_code || undefined
      });

      setSuccess(
        response.data.verification_code
          ? `등록 대기 중입니다! 인증 코드: ${response.data.verification_code}`
          : '댓글 제공자로 등록되었습니다!'
      );
      setStatus({ producer: response.data, exists: true });
    } catch (err: any) {
      setError(err.message || '등록에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCheckStatus = async () => {
    if (!formData.instagram_username) {
      setError('인스타그램 사용자명을 입력해주세요');
      return;
    }

    try {
      setIsLoading(true);
      setError('');
      setSuccess('');

      const response = await api.get(`/producer/${formData.instagram_username}`);
      setStatus(response.data);
    } catch (err: any) {
      setError(err.message || '현황 조회에 실패했습니다');
      setStatus(null);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: ProducerStatus) => {
    const variants = {
      active: 'success' as const,
      pending: 'warning' as const,
      inactive: 'gray' as const
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
            🚀 AI 자동 댓글 제공하기
          </h1>
          <p className="text-lg text-gray-600 mb-4">
            인스타그램 계정을 등록하여 자동 댓글을 제공하세요
          </p>
          <Alert variant="warning">
            <strong>중요:</strong> 인스타그램 계정 정보는 암호화되어 저장되며 자동 댓글 작성에만 사용됩니다. 개인 정보는 절대 접근하지 않습니다.
          </Alert>
        </div>

        <Card className="mb-6">
          <h2 className="text-xl font-bold mb-4">제공자 등록</h2>
          <div className="space-y-4">
            <Input
              label="인스타그램 사용자명"
              type="text"
              value={formData.instagram_username}
              onChange={(e) =>
                setFormData({ ...formData, instagram_username: e.target.value })
              }
              placeholder="인스타그램 사용자명을 입력하세요"
              required
            />

            <Input
              label="인스타그램 비밀번호"
              type="password"
              value={formData.instagram_password}
              onChange={(e) =>
                setFormData({ ...formData, instagram_password: e.target.value })
              }
              placeholder="인스타그램 비밀번호를 입력하세요"
              required
              helperText="비밀번호는 암호화되어 안전하게 저장됩니다"
            />

            <Input
              label="인증 코드 (선택사항)"
              type="text"
              value={formData.verification_code}
              onChange={(e) =>
                setFormData({ ...formData, verification_code: e.target.value })
              }
              placeholder="인증 코드가 있다면 입력하세요"
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

        {status && status.exists && status.producer && (
          <Card>
            <h2 className="text-xl font-bold mb-4">제공자 현황</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b">
                <span className="text-gray-600">사용자명:</span>
                <span className="font-medium">@{formData.instagram_username}</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b">
                <span className="text-gray-600">상태:</span>
                {getStatusBadge(status.producer.status)}
              </div>
              {status.producer.verification_code && (
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-gray-600">인증 코드:</span>
                  <Badge variant="warning">{status.producer.verification_code}</Badge>
                </div>
              )}
              <div className="flex items-center justify-between py-2">
                <span className="text-gray-600">등록일:</span>
                <span className="text-sm text-gray-500">
                  {new Date(status.producer.created_at).toLocaleString()}
                </span>
              </div>
            </div>

            {status.producer.status === 'pending' && (
              <Alert variant="info" className="mt-4">
                등록이 관리자 승인 대기 중입니다. 나중에 다시 확인해주세요.
              </Alert>
            )}

            {status.producer.status === 'active' && (
              <Alert variant="success" className="mt-4">
                계정이 활성화되어 자동 댓글을 제공하고 있습니다!
              </Alert>
            )}
          </Card>
        )}

        {status && !status.exists && (
          <Alert variant="warning">
            이 사용자명으로 등록된 내역이 없습니다. "등록하기"를 클릭하여 가입하세요!
          </Alert>
        )}

        {/* Info Section */}
        <Card className="mt-8 bg-blue-50 border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-2">
            💡 어떻게 작동하나요:
          </h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li>• 귀하의 계정이 다른 사용자의 게시물에 자동으로 댓글을 달게 됩니다</li>
            <li>• 댓글은 자연스럽고 지능적으로 생성됩니다</li>
            <li>• 커뮤니티 참여도 향상에 도움이 됩니다</li>
            <li>• 계정 정보는 암호화되며 절대 공유되지 않습니다</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
