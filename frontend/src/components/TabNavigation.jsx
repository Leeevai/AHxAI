import React from 'react';
import { Code, MessageSquare, Eye } from 'lucide-react';

const TabNavigation = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'code', label: 'Code', icon: Code },
    { id: 'explain', label: 'Explanation', icon: MessageSquare },
    { id: 'visualize', label: 'Visualize', icon: Eye }
  ];

  return (
    <div className="flex space-x-1 mb-6">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => setActiveTab(tab.id)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium ${
            activeTab === tab.id
              ? 'bg-blue-500 text-white'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          <tab.icon size={16} />
          {tab.label}
        </button>
      ))}
    </div>
  );
};

export default TabNavigation;