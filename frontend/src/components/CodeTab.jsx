import React from 'react';
import { Play, Download } from 'lucide-react';

const CodeTab = ({ code, setCode }) => {
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-900">Code Editor</h2>
        <div className="flex gap-2">
          <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2" onClick={() => alert("Running ...")}>
            <Play size={16} />
            Run
          </button>
          <button className="bg-slate-200 hover:bg-slate-300 text-slate-700 px-4 py-2 rounded-lg flex items-center gap-2">
            <Download size={16} />
            Download
          </button>
        </div>
      </div>
      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        className="flex-1 bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Enter your code here..."
      />
    </div>
  );
};

export default CodeTab;