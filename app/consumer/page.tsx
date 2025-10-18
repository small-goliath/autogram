'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import Container from '@/components/layout/Container';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';
import Button from '@/components/ui/Button';
import { publicApi } from '@/lib/api';

const consumerSchema = z.object({
  instagram_id: z
    .string()
    .min(1, 'Instagram ID를 입력해주세요')
    .regex(/^[a-zA-Z0-9._]+$/, 'Instagram ID 형식이 올바르지 않습니다'),
  comment_tone: z
    .string()
    .min(10, '댓글 톤은 최소 10자 이상 입력해주세요')
    .max(1000, '댓글 톤은 최대 1000자까지 입력할 수 있습니다'),
  special_requests: z
    .string()
    .max(1000, '특별 요청사항은 최대 1000자까지 입력할 수 있습니다')
    .optional(),
});

type ConsumerFormData = z.infer<typeof consumerSchema>;

export default function ConsumerPage() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ConsumerFormData>({
    resolver: zodResolver(consumerSchema),
  });

  const onSubmit = async (data: ConsumerFormData) => {
    setIsSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(false);

    try {
      await publicApi.registerConsumer({
        instagram_id: data.instagram_id,
        comment_tone: data.comment_tone,
        special_requests: data.special_requests || undefined,
      });

      setSubmitSuccess(true);
      reset();

      // Auto-hide success message after 5 seconds
      setTimeout(() => {
        setSubmitSuccess(false);
      }, 5000);
    } catch (error: any) {
      console.error('Failed to register consumer:', error);
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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI 댓글 받기</h1>
        <p className="text-gray-600">
          Instagram 게시물에 AI가 작성한 자연스러운 댓글을 받아보세요
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
                  Consumer로 성공적으로 등록되었습니다. AI가 곧 댓글을 작성할 예정입니다.
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
              <Textarea
                label="댓글 톤 및 스타일"
                placeholder="예: 친근하고 밝은 톤으로 작성해주세요. 이모지를 적절히 사용하고, 격식을 갖추지 않은 편안한 말투로 작성해주세요."
                rows={5}
                error={errors.comment_tone?.message}
                {...register('comment_tone')}
              />
              <p className="mt-1 text-sm text-gray-500">
                AI가 작성할 댓글의 톤과 스타일을 자세히 설명해주세요 (최소 10자)
              </p>
            </div>

            <div>
              <Textarea
                label="특별 요청사항 (선택사항)"
                placeholder="예: 특정 단어를 피해주세요, 특정 주제에 대해서만 댓글을 달아주세요 등"
                rows={4}
                error={errors.special_requests?.message}
                {...register('special_requests')}
              />
              <p className="mt-1 text-sm text-gray-500">
                댓글 작성 시 특별히 고려해야 할 사항이 있다면 입력해주세요
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
              <span>AI가 작성한 댓글은 자연스럽고 진정성 있게 작성됩니다.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>댓글 톤을 상세히 설명할수록 더 만족스러운 결과를 얻을 수 있습니다.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>등록 후 품앗이 참여자들이 AI 댓글을 작성할 예정입니다.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>Instagram 계정은 공개 계정이어야 합니다.</span>
            </li>
          </ul>
        </Card>
      </div>
    </Container>
  );
}
