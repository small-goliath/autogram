import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Autogram - Instagram SNS 성장 도우미',
  description: 'Instagram 링크 공유 및 댓글 교환 서비스',
  keywords: ['인스타그램', 'Instagram', 'SNS', '팔로워', '댓글', '자동화'],
  icons: {
    icon: '/logo.png',
    apple: '/logo.png',
  },
  openGraph: {
    title: 'Autogram - Instagram SNS 성장 도우미',
    description: 'Instagram 링크 공유 및 댓글 교환 서비스',
    images: ['/logo.png'],
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <head>
        <link
          rel="stylesheet"
          as="style"
          crossOrigin="anonymous"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css"
        />
      </head>
      <body>{children}</body>
    </html>
  )
}
