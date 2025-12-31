'use client';

import { Alert } from '@/components/ui/Alert';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { createProducer, deleteProducer, getErrorMessage, getProducer } from '@/lib/api';
import type { Producer } from '@/types';
import Image from 'next/image';
import { useState } from 'react';

export default function ProducerPage() {
  const [formData, setFormData] = useState({
    instagram_username: '',
    instagram_password: '',
    totp_secret: ''
  });
  const [viewUsername, setViewUsername] = useState('');
  const [producerData, setProducerData] = useState<Producer | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleRegister = async () => {
    if (!formData.instagram_username || !formData.instagram_password) {
      setError('사용자명과 비밀번호는 필수 입력 항목입니다');
      return;
    }

    try {
      setIsLoading(true);
      setError('');
      setSuccess('');

      await createProducer({
        instagram_username: formData.instagram_username,
        instagram_password: formData.instagram_password,
        totp_secret: formData.totp_secret || undefined
      });

      setSuccess('AI 자동 댓글 제공자로 등록되었습니다!');

      // Reset form
      setFormData({
        instagram_username: '',
        instagram_password: '',
        totp_secret: ''
      });
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewProducer = async () => {
    if (!viewUsername) {
      setError('사용자명을 입력해주세요');
      return;
    }

    try {
      setIsLoading(true);
      setError('');
      setSuccess('');
      const data = await getProducer(viewUsername);
      setProducerData(data);
    } catch (err: any) {
      setError(getErrorMessage(err));
      setProducerData(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!producerData) return;

    const confirmed = window.confirm(
      `정말로 @${producerData.instagram_username} 계정을 삭제하시겠습니까?\n\n등록된 계정 정보가 삭제됩니다.\n이 작업은 되돌릴 수 없습니다.`
    );

    if (!confirmed) return;

    try {
      setIsDeleting(true);
      setError('');
      const response = await deleteProducer(producerData.instagram_username);
      setSuccess(response.message);
      setProducerData(null);
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
            🚀 AI 자동 댓글 제공하기
          </h1>
          <p className="text-lg text-gray-600 mb-4">
            인스타그램 계정을 등록하여 자동 댓글을 제공하세요
          </p>

          <Alert variant="error" className="mb-4">
            <strong>⚠️ 중요한 주의사항:</strong>
            <ul className="mt-2 space-y-1 list-disc list-inside">
              <li>인스타그램의 보안 정책에 따라 계정이 일시적으로 잠길 수 있습니다</li>
              <li>계정 잠김 또는 제한에 대한 책임은 사용자에게 있습니다</li>
              <li>본 서비스는 계정 문제에 대해 책임지지 않습니다</li>
            </ul>
          </Alert>

          <Alert variant="warning">
            <strong>보안 정보:</strong> 입력하신 계정 정보는 암호화되어 안전하게 저장되며, 자동 댓글 작성 목적으로만 사용됩니다.
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
                  handleViewProducer();
                }
              }}
              className="flex-1 px-3 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <Button
              variant="primary"
              onClick={handleViewProducer}
              isLoading={isLoading}
            >
              조회
            </Button>
          </div>
        </Card>

        {producerData && (
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
                <span className="font-medium text-blue-900">@{producerData.instagram_username}</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-blue-200">
                <span className="text-blue-700">상태:</span>
                {getStatusBadge(producerData.status)}
              </div>
              <div className="flex items-center justify-between py-2 border-b border-blue-200">
                <span className="text-blue-700">등록일:</span>
                <span className="text-sm text-blue-800">
                  {new Date(producerData.created_at).toLocaleDateString('ko-KR')}
                </span>
              </div>
              {producerData.last_used_at && (
                <div className="flex items-center justify-between py-2 border-blue-200">
                  <span className="text-blue-700">마지막 사용:</span>
                  <span className="text-sm text-blue-800">
                    {new Date(producerData.last_used_at).toLocaleDateString('ko-KR')}
                  </span>
                </div>
              )}
            </div>
            {producerData.status === 'pending' && (
              <Alert variant="warning" className="mt-4">
                등록이 관리자 승인 대기 중입니다.
              </Alert>
            )}
            {producerData.status === 'active' && (
              <Alert variant="success" className="mt-4">
                계정이 활성화되어 자동 댓글을 제공하고 있습니다!
              </Alert>
            )}
          </Card>
        )}

        <Card className="mb-6">
          <h2 className="text-xl font-bold mb-4">제공자 등록</h2>
          <div className="space-y-4">
            <Input
              label="사용자명 (username)"
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
              helperText="비밀번호는 암호화되어 안전하게 저장됩니다."
            />

            <Input
              label="TOTP Secret (2단계 인증 설정된 계정인 경우 필수)"
              type="text"
              value={formData.totp_secret}
              onChange={(e) =>
                setFormData({ ...formData, totp_secret: e.target.value })
              }
              placeholder="2단계 인증을 사용하는 경우 공백 없이 32자 TOTP Secret 입력"
              helperText="2단계 인증을 사용하지 않는 경우 비워두세요. 암호화되어 안전하게 저장됩니다."
              maxLength={32}
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
            <li>• 귀하의 계정이 다른 사용자의 게시물에 자동으로 댓글을 달게 됩니다</li>
            <li>• 댓글은 자연스럽고 지능적으로 생성됩니다</li>
            <li>• 커뮤니티 참여도 향상에 도움이 됩니다</li>
            <li>• 계정 정보는 암호화되며 절대 공유되지 않습니다</li>
            <li>• 인스타그램 정책에 따라 과도한 요청은 제한될 수 있습니다</li>
          </ul>
        </Card>

        <Card className="mt-4 bg-gray-50 border-gray-200">
          <h3 className="font-semibold text-gray-900 mb-2">
            ℹ️ TOTP Secret이란?
          </h3>
          <p className="text-sm text-gray-700 mb-4">
            2단계 인증을 사용하는 계정의 경우, 인증 앱(Google Authenticator 등)에
            등록할 때 받은 32자리 비밀 코드입니다. 2단계 인증을 사용하지 않는다면
            이 필드를 비워두시면 됩니다.
          </p>
          <div className="mt-4 border border-gray-300 rounded-lg overflow-hidden">
            <Image
              src="/TOTP_secret.png"
              alt="TOTP Secret 확인 방법"
              width={800}
              height={600}
              className="w-full h-auto"
              priority
            />
          </div>
        </Card>
      </div>
    </div>
  );
}
