'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Container from '@/components/layout/Container';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { publicApi, NoticesResponse } from '@/lib/api';

export default function HomePage() {
  const [data, setData] = useState<NoticesResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNotices = async () => {
      try {
        const response = await publicApi.getNotices();
        setData(response.data);
      } catch (error) {
        console.error('Failed to fetch notices:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNotices();
  }, []);

  return (
    <Container>
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Autogram에 오신 것을 환영합니다
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          AI 댓글을 주고받는 Instagram 품앗이 서비스
        </p>
      </div>

      {/* Service Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
        <Card>
          <div className="text-center">
            <div className="text-4xl mb-4">📝</div>
            <h3 className="text-xl font-semibold mb-2">AI 댓글 받기</h3>
            <p className="text-gray-600 mb-4">
              Instagram 게시물에 AI가 작성한 자연스러운 댓글을 받아보세요
            </p>
            <Link href="/consumer">
              <Button>신청하기</Button>
            </Link>
          </div>
        </Card>

        <Card>
          <div className="text-center">
            <div className="text-4xl mb-4">✍️</div>
            <h3 className="text-xl font-semibold mb-2">AI 댓글 달기</h3>
            <p className="text-gray-600 mb-4">
              다른 사람의 게시물에 AI 댓글을 달아 품앗이에 참여하세요
            </p>
            <Link href="/producer">
              <Button>신청하기</Button>
            </Link>
          </div>
        </Card>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <Link href="/requests">
          <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
            <div className="text-center">
              <div className="text-3xl mb-3">📊</div>
              <h3 className="text-lg font-semibold mb-2">지난주 현황</h3>
              <p className="text-gray-600 text-sm">
                지난주 제출된 Instagram 링크 확인
              </p>
            </div>
          </Card>
        </Link>

        <Link href="/verification">
          <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
            <div className="text-center">
              <div className="text-3xl mb-3">🔍</div>
              <h3 className="text-lg font-semibold mb-2">품앗이 현황</h3>
              <p className="text-gray-600 text-sm">
                댓글 작성 상태 및 미작성자 확인
              </p>
            </div>
          </Card>
        </Link>

        <Link href="/unfollow-checker">
          <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
            <div className="text-center">
              <div className="text-3xl mb-3">👥</div>
              <h3 className="text-lg font-semibold mb-2">언팔로워 확인</h3>
              <p className="text-gray-600 text-sm">
                나를 언팔로우한 사람 찾기
              </p>
            </div>
          </Card>
        </Link>
      </div>

      {/* KakaoTalk Link */}
      {!loading && data && (
        <Card className="bg-yellow-50 border-yellow-200">
          <div className="text-center">
            <h3 className="text-xl font-semibold mb-4">카카오톡 오픈채팅</h3>
            <p className="text-gray-700 mb-4">
              품앗이 참여를 위해 카카오톡 오픈채팅방에 참여하세요
            </p>
            <a
              href={data.kakaotalk_open_chat_link}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button>오픈채팅 참여하기</Button>
            </a>
          </div>
        </Card>
      )}

      {/* Notices */}
      {!loading && data && data.notices.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6">공지사항</h2>
          <div className="space-y-4">
            {data.notices.map((notice) => (
              <Card
                key={notice.id}
                className={notice.is_important ? 'border-l-4 border-red-500' : ''}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {notice.is_pinned && (
                        <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                          고정
                        </span>
                      )}
                      {notice.is_important && (
                        <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">
                          중요
                        </span>
                      )}
                      <h3 className="text-lg font-semibold">{notice.title}</h3>
                    </div>
                    <p className="text-gray-600 whitespace-pre-wrap">{notice.content}</p>
                    <p className="text-sm text-gray-400 mt-2">
                      {new Date(notice.created_at).toLocaleDateString('ko-KR')}
                    </p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </Container>
  );
}
