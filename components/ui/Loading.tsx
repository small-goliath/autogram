import React from 'react';
import { cn } from '@/lib/utils';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({ size = 'md', className }) => {
  const sizeStyles = {
    sm: 'w-5 h-5 border-2',
    md: 'w-10 h-10 border-4',
    lg: 'w-15 h-15 border-6',
  };

  return (
    <div
      className={cn(
        'animate-spin rounded-full border-gray-200 border-t-primary-500',
        sizeStyles[size],
        className
      )}
      role="status"
      aria-label="로딩 중"
    >
      <span className="sr-only">로딩 중...</span>
    </div>
  );
};

interface LoadingOverlayProps {
  message?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ message = '로딩 중...' }) => {
  return (
    <div className="absolute inset-0 bg-white/90 flex flex-col items-center justify-center gap-4 z-50 rounded-lg">
      <Spinner size="lg" />
      <p className="text-sm text-gray-600">{message}</p>
    </div>
  );
};
