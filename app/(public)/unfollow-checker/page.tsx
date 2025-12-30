'use client';

import { Alert } from '@/components/ui/Alert';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { getErrorMessage, registerUnfollowerServiceUser } from '@/lib/api';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export default function UnfollowCheckerPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    totp_secret: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleRegister = async () => {
    if (!formData.username || !formData.password) {
      setError('사용자명과 비밀번호는 필수 입력 항목입니다');
      return;
    }

    try {
      setIsLoading(true);
      setError('');
      setSuccess('');

      const response = await registerUnfollowerServiceUser({
        username: formData.username,
        password: formData.password,
        totp_secret: formData.totp_secret || undefined
      });

      setSuccess(response.message);

      // Redirect to unfollower list after 2 seconds
      const username = formData.username;
      setTimeout(() => {
        router.push(`/unfollow-checker/${username}`);
      }, 2000);
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            🔍 인스타 언팔로워 검색기
          </h1>
          <p className="text-lg text-gray-600 mb-4">
            나를 언팔로우한 계정을 찾아보세요!
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
            <strong>보안 정보:</strong> 입력하신 계정 정보는 암호화되어 안전하게 저장되며, 언팔로워 검색 목적으로만 사용됩니다.
          </Alert>
        </div>

        <Card className="mb-6 bg-green-50 border-green-200">
          <h3 className="font-semibold text-green-900 mb-2">
            📋 이미 등록하셨나요?
          </h3>
          <p className="text-sm text-green-700 mb-3">
            등록된 계정의 언팔로워 목록을 확인하려면 아래에 사용자명을 입력하세요:
          </p>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="사용자명 입력"
              id="view-username-input"
              className="flex-1 px-3 py-2 border border-green-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.currentTarget.value) {
                  router.push(`/unfollow-checker/${e.currentTarget.value}`);
                }
              }}
            />
            <Button
              variant="primary"
              onClick={() => {
                const input = document.getElementById('view-username-input') as HTMLInputElement;
                if (input && input.value) {
                  router.push(`/unfollow-checker/${input.value}`);
                }
              }}
            >
              보기
            </Button>
          </div>
        </Card>

        <Card className="mb-6">
          <h2 className="text-xl font-bold mb-4">계정 등록</h2>
          <div className="space-y-4">
            <Input
              label="사용자명 (username)"
              type="text"
              value={formData.username}
              onChange={(e) =>
                setFormData({ ...formData, username: e.target.value })
              }
              placeholder="인스타그램 사용자명을 입력하세요"
              required
              helperText="SNS 품앗이에 등록된 사용자명을 입력해주세요."
            />

            <Input
              label="인스타그램 비밀번호"
              type="password"
              value={formData.password}
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
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
            <li>• 계정을 등록하면 언팔로워 검색 서비스를 이용할 수 있습니다</li>
            <li>• 나를 팔로우하지 않는 계정 목록을 확인할 수 있습니다</li>
            <li>• 계정 정보는 암호화되어 저장되며 검색 목적으로만 사용됩니다</li>
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
