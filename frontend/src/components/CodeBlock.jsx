import React, { useState } from 'react';
import { Copy } from 'lucide-react';

const CodeBlock = ({ code, language = 'javascript', title }) => {
  const [copied, setCopied] = useState(false);
  
  const copyCode = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-slate-900 rounded-lg overflow-hidden border border-slate-700">
      <div className="bg-slate-800 px-4 py-2 flex items-center justify-between border-b border-slate-700">
        <span className="text-slate-300 text-sm font-medium">{title || language}</span>
        <button
          onClick={copyCode}
          className="text-slate-400 hover:text-slate-200 transition-colors"
        >
          {copied ? <span className="text-green-400">Copied!</span> : <Copy size={16} />}
        </button>
      </div>
      <pre className="p-4 overflow-x-auto text-sm text-slate-100">
        <code>{code}</code>
      </pre>
    </div>
  );
};

export default CodeBlock;