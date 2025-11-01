import AdminNavigation from '@/components/AdminNavigation';

export const metadata = {
  title: 'Admin - Autogram',
  description: 'Autogram admin panel'
};

export default function AdminLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gray-50">
      {children}
    </div>
  );
}
