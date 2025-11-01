'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import AdminNavigation from '@/components/AdminNavigation';
import Table from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import Modal, { ConfirmDialog } from '@/components/ui/Modal';
import { Alert } from '@/components/ui/Alert';
import { Badge } from '@/components/ui/Badge';
import { api } from '@/lib/api';
import { Helper } from '@/types';

export default function AdminHelpersPage() {
  return (
    <ProtectedRoute>
      <AdminNavigation />
      <HelpersManagementContent />
    </ProtectedRoute>
  );
}

function HelpersManagementContent() {
  const [helpers, setHelpers] = useState<Helper[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Modal states
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{
    isOpen: boolean;
    helper: Helper | null;
  }>({ isOpen: false, helper: null });

  // Form state
  const [formData, setFormData] = useState({
    instagram_username: '',
    instagram_password: '',
    verification_code: ''
  });

  // Fetch helpers
  const fetchHelpers = async () => {
    try {
      setIsLoading(true);
      setError('');
      const response = await api.get('/api/admin/helpers');
      setHelpers(response.data || []);
    } catch (err: any) {
      setError(err.message || '헬퍼 계정 목록을 불러오는데 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHelpers();
  }, []);

  // Add helper
  const handleAddHelper = async () => {
    if (!formData.instagram_username || !formData.instagram_password) {
      setError('모든 필드를 입력해주세요');
      return;
    }

    try {
      // Only send verification_code if it's provided
      const payload = formData.verification_code
        ? formData
        : { instagram_username: formData.instagram_username, instagram_password: formData.instagram_password };

      await api.post('/api/admin/helpers', payload);
      setIsAddModalOpen(false);
      setFormData({ instagram_username: '', instagram_password: '', verification_code: '' });
      fetchHelpers();
    } catch (err: any) {
      // Extract error message from response
      const errorMessage = err.response?.data?.detail || err.message || '헬퍼 계정 추가에 실패했습니다';
      setError(errorMessage);
      console.error('Helper registration error:', err);
    }
  };

  // Delete helper
  const handleDeleteHelper = async (helper: Helper) => {
    try {
      await api.delete(`/api/admin/helpers/${helper.id}`);
      fetchHelpers();
    } catch (err: any) {
      setError(err.message || '헬퍼 계정 삭제에 실패했습니다');
    }
  };

  // Toggle active status
  const toggleActive = async (helper: Helper) => {
    try {
      await api.patch(`/api/admin/helpers/${helper.id}`, {
        is_active: !helper.is_active
      });
      fetchHelpers();
    } catch (err: any) {
      setError(err.message || '헬퍼 계정 상태 변경에 실패했습니다');
    }
  };

  const columns = [
    {
      header: 'ID',
      accessor: 'id' as keyof Helper,
      className: 'text-gray-500'
    },
    {
      header: '사용자명',
      accessor: 'instagram_username' as keyof Helper,
      className: 'font-medium text-gray-900'
    },
    {
      header: '상태',
      accessor: ((helper: Helper) => (
        <Badge variant={helper.is_active ? 'success' : 'secondary'}>
          {helper.is_active ? '활성' : '비활성'}
        </Badge>
      )) as any
    },
    {
      header: '마지막 사용',
      accessor: ((helper: Helper) =>
        helper.last_used_at
          ? new Date(helper.last_used_at).toLocaleString()
          : '없음') as any
    },
    {
      header: '작업',
      accessor: ((helper: Helper) => (
        <div className="flex gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => toggleActive(helper)}
          >
            {helper.is_active ? '비활성화' : '활성화'}
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={() => setDeleteConfirm({ isOpen: true, helper })}
          >
            삭제
          </Button>
        </div>
      )) as any
    }
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            인스타그램 헬퍼 계정 관리
          </h1>
          <p className="text-gray-600">
            자동 댓글 작성에 사용되는 인스타그램 계정을 관리합니다
          </p>
        </div>

        {error && (
          <Alert variant="error" className="mb-6" onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <div className="bg-white rounded-lg shadow p-4 mb-6 flex justify-end">
          <Button variant="primary" onClick={() => setIsAddModalOpen(true)}>
            + 헬퍼 계정 추가
          </Button>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          {isLoading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          ) : (
            <Table
              data={helpers}
              columns={columns}
              keyExtractor={(helper) => helper.id}
              emptyMessage="등록된 헬퍼 계정이 없습니다"
            />
          )}
        </div>
      </div>

      <Modal
        isOpen={isAddModalOpen}
        onClose={() => {
          setIsAddModalOpen(false);
          setFormData({ instagram_username: '', instagram_password: '', verification_code: '' });
        }}
        title="헬퍼 계정 추가"
        footer={
          <>
            <Button
              variant="outline"
              onClick={() => {
                setIsAddModalOpen(false);
                setFormData({ instagram_username: '', instagram_password: '', verification_code: '' });
              }}
            >
              취소
            </Button>
            <Button variant="primary" onClick={handleAddHelper}>
              추가
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label="인스타그램 사용자명"
            type="text"
            value={formData.instagram_username}
            onChange={(e) =>
              setFormData({ ...formData, instagram_username: e.target.value })
            }
            placeholder="인스타그램 사용자명"
            required
          />
          <Input
            label="인스타그램 비밀번호"
            type="password"
            value={formData.instagram_password}
            onChange={(e) =>
              setFormData({ ...formData, instagram_password: e.target.value })
            }
            placeholder="인스타그램 비밀번호"
            required
          />
          <Input
            label="2단계 인증 코드 (선택사항)"
            type="text"
            value={formData.verification_code}
            onChange={(e) =>
              setFormData({ ...formData, verification_code: e.target.value })
            }
            placeholder="2단계 인증이 설정된 경우 입력"
          />
        </div>
      </Modal>

      <ConfirmDialog
        isOpen={deleteConfirm.isOpen}
        onClose={() => setDeleteConfirm({ isOpen: false, helper: null })}
        onConfirm={() => {
          if (deleteConfirm.helper) {
            handleDeleteHelper(deleteConfirm.helper);
          }
        }}
        title="헬퍼 계정 삭제"
        message={`정말로 "${deleteConfirm.helper?.instagram_username}" 계정을 삭제하시겠습니까?`}
        confirmText="삭제"
        variant="danger"
      />
    </div>
  );
}
