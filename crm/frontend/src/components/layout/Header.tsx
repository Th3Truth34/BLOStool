import { useEffect, useState } from 'react';
import { Bell } from 'lucide-react';
import api from '../../api/client';

export default function Header() {
  const [userName, setUserName] = useState('');

  useEffect(() => {
    api.get('/auth/me').then(({ data }) => {
      setUserName(data.full_name);
    }).catch(() => {});
  }, []);

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8">
      <div />
      <div className="flex items-center gap-4">
        <button className="p-2 rounded-lg hover:bg-gray-100 relative">
          <Bell size={20} className="text-gray-600" />
        </button>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-medium">
            {userName ? userName.charAt(0).toUpperCase() : 'U'}
          </div>
          <span className="text-sm font-medium text-gray-700">{userName}</span>
        </div>
      </div>
    </header>
  );
}
