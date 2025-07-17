import React from 'react';
import { Settings } from 'lucide-react';

const Header = () => {
  return (
    <header className="bg-white border-b border-slate-200 p-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Coding AI Agent</h1>
          <p className="text-slate-600 text-sm">Your intelligent coding companion</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="p-2 hover:bg-slate-100 rounded">
            <Settings size={20} className="text-slate-600" />
          </button>
          <div className="w-8 h-8 bg-blue-500 rounded-full"></div>
        </div>
      </div>
    </header>
  );
};

export default Header;