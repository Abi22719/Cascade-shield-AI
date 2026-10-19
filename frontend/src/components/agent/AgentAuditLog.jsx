import React, { useState } from 'react';
import { FileText, Copy, Download, Check, X } from 'lucide-react';

export default function AgentAuditLog({ isOpen, onClose, session }) {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const jsonContent = JSON.stringify(session, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([jsonContent], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agent-session-${session?.id || 'audit'}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="agent-modal-backdrop">
      <div className="agent-modal-box">
        <div className="agent-modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={18} color="#38bdf8" />
            <span style={{ fontWeight: 700, fontSize: '1rem', color: '#f8fafc' }}>
              Reproducible Session Audit Trail
            </span>
          </div>
          <button 
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
          >
            <X size={18} />
          </button>
        </div>

        <div className="agent-modal-body">
          <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
            Complete deterministic log of all diagnostic actions, selection scores, parameters, and results.
          </div>

          <pre 
            style={{ 
              background: '#090d16', 
              border: '1px solid #1e293b', 
              borderRadius: '6px', 
              padding: '0.8rem', 
              fontSize: '0.72rem', 
              color: '#94a3b8', 
              overflowX: 'auto',
              maxHeight: '400px'
            }}
          >
            {jsonContent}
          </pre>
        </div>

        <div className="agent-modal-footer">
          <button className="btn-agent-secondary" onClick={handleCopy}>
            {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
            <span>{copied ? 'Copied' : 'Copy JSON'}</span>
          </button>
          <button className="btn-agent-primary" onClick={handleDownload}>
            <Download size={14} />
            <span>Download Audit File</span>
          </button>
        </div>
      </div>
    </div>
  );
}
