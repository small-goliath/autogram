'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import AdminNavigation from '@/components/AdminNavigation';
import Table, { Pagination } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import Modal, { ConfirmDialog } from '@/components/ui/Modal';
import { Alert } from '@/components/ui/Alert';
import { Badge } from '@/components/ui/Badge';
import { api } from '@/lib/api';
import { SnsRaiseUser } from '@/types';

export default function AdminUsersPage() {
  return (
    <ProtectedRoute>
      <AdminNavigation />
      <UsersManagementContent />
    </ProtectedRoute>
  );
}

function UsersManagementContent() {
  const [users, setUsers] = useState<SnsRaiseUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');

  // Modal states
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{
    isOpen: boolean;
    user: SnsRaiseUser | null;
  }>({ isOpen: false, user: null });

  // Form state
  const [newUsername, setNewUsername] = useState('');

  // Fetch users
  const fetchUsers = async () => {
    try {
      setIsLoading(true);
      setError('');
      const response = await api.get('/api/admin/sns-users', {
        params: { page: currentPage, limit: 20, search: searchQuery }
      });
      setUsers(response.data.users || []);
      setTotalPages(response.data.total_pages || 1);
    } catch (err: any) {
      setError(err.message || '사용자 목록을 불러오는데 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [currentPage, searchQuery]);

  // Add user
  const handleAddUser = async () => {
    if (!newUsername.trim()) {
      setError('사용자명을 입력해주세요');
      return;
    }

    try {
      await api.post('/api/admin/sns-users', { username: newUsername });
      setIsAddModalOpen(false);
      setNewUsername('');
      fetchUsers();
    } catch (err: any) {
      setError(err.message || '사용자 추가에 실패했습니다');
    }
  };

  // Delete user
  const handleDeleteUser = async (user: SnsRaiseUser) => {
    try {
      await api.delete(`/api/admin/sns-users/${user.id}`);
      fetchUsers();
    } catch (err: any) {
      setError(err.message || '사용자 삭제에 실패했습니다');
    }
  };

  const columns = [
    {
      header: 'ID',
      accessor: 'id' as keyof SnsRaiseUser,
      className: 'text-gray-500'
    },
    {
      header: '사용자명',
      accessor: 'username' as keyof SnsRaiseUser,
      className: 'font-medium text-gray-900'
    },
    {
      header: '등록일',
      accessor: ((user: SnsRaiseUser) =>
        new Date(user.created_at).toLocaleDateString()) as any
    },
    {
      header: '작업',
      accessor: ((user: SnsRaiseUser) => (
        <Button
          variant="destructive"
          size="sm"
          onClick={() => setDeleteConfirm({ isOpen: true, user })}
        >
          삭제
        </Button>
      )) as any
    }
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            SNS 품앗이 사용자 관리
          </h1>
          <p className="text-gray-600">
            SNS 성장에 참여하는 인스타그램 사용자를 관리합니다
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="error" className="mb-6" onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Actions Bar */}
        <div className="bg-white rounded-lg shadow p-4 mb-6 flex items-center justify-between gap-4">
          <Input
            type="text"
            placeholder="사용자명으로 검색..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="max-w-md"
          />

          <Button variant="primary" onClick={() => setIsAddModalOpen(true)}>
            + 사용자 추가
          </Button>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {isLoading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          ) : (
            <>
              <Table
                data={users}
                columns={columns}
                keyExtractor={(user) => user.id}
                emptyMessage="등록된 사용자가 없습니다"
              />

              {totalPages > 1 && (
                <div className="p-4 border-t">
                  <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={setCurrentPage}
                  />
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Add User Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => {
          setIsAddModalOpen(false);
          setNewUsername('');
        }}
        title="새 사용자 추가"
        footer={
          <>
            <Button
              variant="outline"
              onClick={() => {
                setIsAddModalOpen(false);
                setNewUsername('');
              }}
            >
              취소
            </Button>
            <Button variant="primary" onClick={handleAddUser}>
              추가
            </Button>
          </>
        }
      >
        <Input
          label="인스타그램 사용자명"
          type="text"
          value={newUsername}
          onChange={(e) => setNewUsername(e.target.value)}
          placeholder="인스타그램 사용자명을 입력하세요"
          required
        />
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={deleteConfirm.isOpen}
        onClose={() => setDeleteConfirm({ isOpen: false, user: null })}
        onConfirm={() => {
          if (deleteConfirm.user) {
            handleDeleteUser(deleteConfirm.user);
          }
        }}
        title="사용자 삭제"
        message={`정말로 "${deleteConfirm.user?.username}" 사용자를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.`}
        confirmText="삭제"
        variant="danger"
      />
    </div>
  );
}
