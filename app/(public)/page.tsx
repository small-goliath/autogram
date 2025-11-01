'use client';

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Card, CardHeader, CardTitle, CardBody } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';
import { LoadingOverlay } from '@/components/ui/Loading';
import { getAnnouncements, getErrorMessage } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { Announcement } from '@/types';

export default function AnnouncementsPage() {
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnnouncements = async () => {
      try {
        setLoading(true);
        const data = await getAnnouncements();
        setAnnouncements(data);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };

    fetchAnnouncements();
  }, []);

  if (loading) {
    return (
      <div className="container max-w-4xl mx-auto px-4 py-8 relative min-h-[400px]">
        <LoadingOverlay message="공지사항을 불러오는 중..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container max-w-4xl mx-auto px-4 py-8">
        <Alert variant="error" title="오류가 발생했습니다">
          {error}
        </Alert>
      </div>
    );
  }

  return (
    <div className="container max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">공지사항</h1>

      {announcements.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">등록된 공지사항이 없습니다</h3>
            <p className="mt-1 text-sm text-gray-500">새로운 공지사항이 등록되면 이곳에 표시됩니다.</p>
          </div>
        </Card>
      ) : (
        <div className="space-y-6">
          {announcements.map((announcement) => (
            <Card key={announcement.id} hover>
              <CardHeader>
                <CardTitle>{announcement.title}</CardTitle>
                <p className="text-sm text-gray-500 mt-1">
                  {formatDate(announcement.created_at)}
                </p>
              </CardHeader>
              <CardBody>
                <div className="prose prose-gray prose-lg max-w-none prose-headings:font-bold prose-h1:text-3xl prose-h2:text-2xl prose-h3:text-xl prose-p:text-gray-700 prose-li:text-gray-700 prose-strong:text-gray-900 prose-strong:font-semibold">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {announcement.content}
                  </ReactMarkdown>
                </div>

                {announcement.kakao_openchat_link && (
                  <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-semibold text-gray-900 mb-3">카카오톡 오픈채팅</h4>
                    <div className="flex items-center gap-4">
                      {announcement.kakao_qr_code_url && (
                        <div className="flex-shrink-0">
                          <img
                            src={announcement.kakao_qr_code_url}
                            alt="카카오톡 QR 코드"
                            className="w-32 h-32 border border-gray-200 rounded"
                          />
                          <p className="text-xs text-gray-500 text-center mt-1">
                            QR 코드로 참여하기
                          </p>
                        </div>
                      )}
                      <div className="flex-1">
                        <p className="text-sm text-gray-600 mb-3">
                          궁금한 점이 있거나 함께 소통하고 싶으시다면<br />
                          카카오톡 오픈채팅방에 참여해주세요!
                        </p>
                        <a
                          href={announcement.kakao_openchat_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-400 text-gray-900 font-medium rounded-lg hover:bg-yellow-500 transition-colors"
                        >
                          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 3c5.799 0 10.5 3.664 10.5 8.185 0 4.52-4.701 8.184-10.5 8.184a13.5 13.5 0 01-1.727-.11l-4.408 2.883c-.501.265-.678.236-.472-.413l.892-3.678c-2.88-1.46-4.785-3.99-4.785-6.866C1.5 6.665 6.201 3 12 3z" />
                          </svg>
                          채팅방 참여하기
                        </a>
                      </div>
                    </div>
                  </div>
                )}
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
