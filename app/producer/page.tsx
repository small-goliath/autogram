'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import Container from '@/components/layout/Container';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import { publicApi } from '@/lib/api';

const producerSchema = z.object({
  instagram_id: z
    .string()
    .min(1, 'Instagram ID를 입력해주세요')
    .regex(/^[a-zA-Z0-9._]+$/, 'Instagram ID 형식이 올바르지 않습니다'),
  instagram_password: z
    .string()
    .min(6, '비밀번호는 최소 6자 이상이어야 합니다')
    .max(100, '비밀번호가 너무 깁니다'),
});

type ProducerFormData = z.infer<typeof producerSchema>;

export default function ProducerPage() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ProducerFormData>({
    resolver: zodResolver(producerSchema),
  });

  const onSubmit = async (data: ProducerFormData) => {
    setIsSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(false);

    try {
      await publicApi.registerProducer({
        instagram_id: data.instagram_id,
        instagram_password: data.instagram_password,
      });

      setSubmitSuccess(true);
      reset();

      // Auto-hide success message after 5 seconds
      setTimeout(() => {
        setSubmitSuccess(false);
      }, 5000);
    } catch (error: any) {
      console.error('Failed to register producer:', error);
      setSubmitError(
        error.response?.data?.detail ||
        '등록에 실패했습니다. 잠시 후 다시 시도해주세요.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Container>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI 댓글 달기</h1>
        <p className="text-gray-600">
          다른 사람의 게시물에 AI 댓글을 달아 품앗이에 참여하세요
        </p>
      </div>

      <div className="max-w-2xl mx-auto">
        {submitSuccess && (
          <Card className="mb-6 bg-green-50 border-green-200">
            <div className="flex items-center gap-3">
              <div className="text-2xl">✓</div>
              <div>
                <h3 className="font-semibold text-green-900">등록 완료</h3>
                <p className="text-green-700 text-sm">
                  Producer로 성공적으로 등록되었습니다. 시스템이 자동으로 AI 댓글을 작성할 예정입니다.
                </p>
              </div>
            </div>
          </Card>
        )}

        {submitError && (
          <Card className="mb-6 bg-red-50 border-red-200">
            <div className="flex items-center gap-3">
              <div className="text-2xl">⚠️</div>
              <div>
                <h3 className="font-semibold text-red-900">등록 실패</h3>
                <p className="text-red-700 text-sm">{submitError}</p>
              </div>
            </div>
          </Card>
        )}

        <Card className="mb-6 bg-yellow-50 border-yellow-200">
          <div className="flex items-start gap-3">
            <div className="text-2xl">🔒</div>
            <div>
              <h3 className="font-semibold text-yellow-900 mb-2">보안 안내</h3>
              <ul className="space-y-1 text-sm text-yellow-800">
                <li className="flex items-start gap-2">
                  <span className="mt-1">•</span>
                  <span>비밀번호는 안전하게 암호화되어 저장됩니다.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1">•</span>
                  <span>시스템은 댓글 작성 목적으로만 계정을 사용합니다.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1">•</span>
                  <span>2단계 인증이 활성화된 경우 비활성화가 필요할 수 있습니다.</span>
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
                {...register('instagram_password')}
              />
              <p className="mt-1 text-sm text-gray-500">
                비밀번호는 암호화되어 안전하게 저장됩니다
              </p>
            </div>

            <Button
              type="submit"
              isLoading={isSubmitting}
              className="w-full"
              size="lg"
            >
              등록하기
            </Button>
          </form>
        </Card>

        <Card className="mt-6 bg-blue-50 border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-2">안내사항</h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>등록된 계정은 자동으로 다른 참여자의 게시물에 AI 댓글을 작성합니다.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>AI가 각 게시물의 내용을 분석하여 자연스러운 댓글을 작성합니다.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>품앗이 시스템을 통해 댓글을 주고받으며 상호 성장할 수 있습니다.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>계정 정보는 언제든지 관리자를 통해 삭제 요청할 수 있습니다.</span>
            </li>
          </ul>
        </Card>

        <Card className="mt-6 bg-red-50 border-red-200">
          <h3 className="font-semibold text-red-900 mb-2">주의사항</h3>
          <ul className="space-y-2 text-sm text-red-800">
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>Instagram의 이용 약관을 준수하며 사용해주세요.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>과도한 댓글 작성으로 인한 계정 제한은 사용자 책임입니다.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>2단계 인증(2FA)이 활성화되어 있으면 로그인이 실패할 수 있습니다.</span>
            </li>
          </ul>
        </Card>
      </div>
    </Container>
  );
}
