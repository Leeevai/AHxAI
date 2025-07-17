import React from 'react';

const ExplanationTab = ({ explanation }) => {
  return (
    <div className="h-full flex flex-col">
      <h2 className="text-lg font-semibold text-slate-900 mb-4">Code Explanation</h2>
      <div className="flex-1 bg-white rounded-lg p-4 border border-slate-200 overflow-y-auto">
        <p className="text-slate-700 mb-4">{explanation}</p>
        
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
          <h4 className="text-yellow-800 font-medium mb-2">⚠️ Performance Warning</h4>
          <p className="text-yellow-700 text-sm">
            O(n²) complexity - consider quicksort for larger datasets.
          </p>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="text-green-800 font-medium mb-2">✅ Suggestions</h4>
          <ul className="text-green-700 text-sm space-y-1">
            <li>• Add input validation</li>
            <li>• Early termination optimization</li>
            <li>• TypeScript types</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ExplanationTab;