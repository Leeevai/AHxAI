import React from 'react';
import { Play, Eye } from 'lucide-react';
import CodeBlock from './CodeBlock';

const VisualizationTab = ({ visualizationCode }) => {
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-900">Visualization</h2>
        <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
          <Play size={16} />
          Run Visualization
        </button>
      </div>
      <div className="flex-1 space-y-4">
        <CodeBlock code={visualizationCode} title="Data Structure Visualization" />
        <div className="bg-white border-2 border-dashed border-slate-300 rounded-lg p-8 flex items-center justify-center">
          <div className="text-center text-slate-500">
            <Eye size={32} className="mx-auto mb-2 opacity-50" />
            <p>Visualization output will appear here</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VisualizationTab;