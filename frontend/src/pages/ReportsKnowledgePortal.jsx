import React, { useState, useEffect, useCallback } from 'react';
import {
  FileText,
  BookOpen,
  Download,
  Plus,
  RefreshCw,
  Search,
  Filter,
  CheckCircle2,
  Calendar,
  Layers,
  Printer,
  Copy,
  Check,
  Tag,
  Server,
  User,
  Clock,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { dashboardApi } from '../services/dashboardApi';
import { knowledgeApi } from '../services/knowledgeApi';
import StatusBadge from '../components/common/StatusBadge';
import SkeletonLoader from '../components/common/SkeletonLoader';
import EmptyState from '../components/common/EmptyState';

export default function ReportsKnowledgePortal({ onNavigateModule, onAddToast }) {
  const [activeTab, setActiveTab] = useState('reports'); // 'reports' | 'knowledge'

  // Reports State
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportType, setReportType] = useState('incident_lifecycle');
  const [reportTitle, setReportTitle] = useState('');
  const [generatingReport, setGeneratingReport] = useState(false);
  const [copiedReport, setCopiedReport] = useState(false);

  // Knowledge Base State
  const [articles, setArticles] = useState([]);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [kbCategory, setKbCategory] = useState('ALL');
  const [kbSearch, setKbSearch] = useState('');
  const [isNewArticleOpen, setIsNewArticleOpen] = useState(false);
  const [newArticleData, setNewArticleData] = useState({
    title: '',
    category: 'PLAYBOOK',
    service_id: '',
    author: 'Administrator',
    content: '',
    tags: 'resilience,failover'
  });

  const [loading, setLoading] = useState(false);

  // Load Reports and Articles
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [repsRes, artsRes] = await Promise.all([
        dashboardApi.listReports().catch(() => ({ reports: [] })),
        knowledgeApi.listArticles().catch(() => [])
      ]);

      const repList = repsRes.reports || [];
      setReports(repList);
      if (repList.length > 0 && !selectedReport) {
        setSelectedReport(repList[0]);
      }

      setArticles(artsRes || []);
      if (artsRes && artsRes.length > 0 && !selectedArticle) {
        setSelectedArticle(artsRes[0]);
      }
    } catch (err) {
      console.warn('Reports & Knowledge data fetch:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedReport, selectedArticle]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Generate Report
  const handleGenerateReport = async () => {
    setGeneratingReport(true);
    try {
      const newRep = await dashboardApi.generateReport({
        report_type: reportType,
        report_title: reportTitle.trim() || undefined,
        data_source: 'simulated',
        report_format: 'markdown'
      });
      setReports(prev => [newRep, ...prev]);
      setSelectedReport(newRep);
      setReportTitle('');
      if (onAddToast) onAddToast(`Generated report: ${newRep.report_title}`, 'success', 'Report Created');
    } catch (err) {
      console.error('Failed to generate report:', err);
      if (onAddToast) onAddToast(err.message, 'error', 'Report Error');
    } finally {
      setGeneratingReport(false);
    }
  };

  // Create Knowledge Article
  const handleCreateArticle = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        title: newArticleData.title,
        category: newArticleData.category,
        service_id: newArticleData.service_id || null,
        author: newArticleData.author,
        content: newArticleData.content,
        tags: newArticleData.tags ? newArticleData.tags.split(',').map(t => t.trim()) : []
      };
      const created = await knowledgeApi.createArticle(payload);
      setArticles(prev => [created, ...prev]);
      setSelectedArticle(created);
      setIsNewArticleOpen(false);
      setNewArticleData({
        title: '',
        category: 'PLAYBOOK',
        service_id: '',
        author: 'Administrator',
        content: '',
        tags: 'resilience,failover'
      });
      if (onAddToast) onAddToast(`Knowledge article '${created.title}' published`, 'success', 'Article Created');
    } catch (err) {
      console.error('Failed to create article:', err);
      if (onAddToast) onAddToast(err.message, 'error', 'Article Error');
    }
  };

  const handleCopyReport = () => {
    if (!selectedReport) return;
    navigator.clipboard.writeText(selectedReport.report_content || '');
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2000);
  };

  const filteredArticles = articles.filter(a => {
    const matchesCat = kbCategory === 'ALL' || a.category === kbCategory;
    const matchesSearch = !kbSearch || 
      a.title?.toLowerCase().includes(kbSearch.toLowerCase()) || 
      a.content?.toLowerCase().includes(kbSearch.toLowerCase()) ||
      a.service_id?.toLowerCase().includes(kbSearch.toLowerCase());
    return matchesCat && matchesSearch;
  });

  return (
    <div className="portal-container animate-fade-in" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Top Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{ background: 'rgba(14, 165, 233, 0.15)', padding: '0.4rem', borderRadius: '8px', color: '#0ea5e9' }}>
              <BookOpen size={22} />
            </div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 700, margin: 0, color: 'var(--text-primary, #f8fafc)' }}>
              Reports and Knowledge Portal
            </h1>
            <span style={{ fontSize: '0.72rem', background: '#3b82f622', color: '#60a5fa', padding: '0.15rem 0.5rem', borderRadius: '4px', border: '1px solid #3b82f644' }}>
              PORTAL 8
            </span>
            <span style={{ fontSize: '0.72rem', background: '#10b98122', color: '#34d399', padding: '0.15rem 0.5rem', borderRadius: '4px', border: '1px solid #10b98144' }}>
              KNOWLEDGE BASE
            </span>
          </div>
          <p style={{ margin: '0.25rem 0 0', fontSize: '0.85rem', color: 'var(--text-secondary, #94a3b8)' }}>
            Centralized post-mortem reports archive, compliance summaries, standard operating procedures (SOPs), and remediation playbooks.
          </p>
        </div>

        {/* Global Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button
            onClick={loadData}
            disabled={loading}
            className="header-secondary-btn"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.5rem 0.85rem', borderRadius: '6px', cursor: 'pointer' }}
          >
            <RefreshCw size={14} className={loading ? 'spin-icon' : ''} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="portal-tabs-nav" style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--border-color, #1e293b)', paddingBottom: '0.5rem' }}>
        <button
          className={`portal-tab-btn ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => setActiveTab('reports')}
        >
          <FileText size={15} />
          <span>Executive & Technical Reports ({reports.length})</span>
        </button>

        <button
          className={`portal-tab-btn ${activeTab === 'knowledge' ? 'active' : ''}`}
          onClick={() => setActiveTab('knowledge')}
        >
          <BookOpen size={15} />
          <span>Resilience Knowledge Base ({articles.length})</span>
        </button>
      </div>

      {/* TAB 1: REPORTS CENTER */}
      {activeTab === 'reports' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Generate Report Bar */}
          <div style={{
            background: 'var(--card-bg, #0f172a)',
            borderRadius: '10px',
            border: '1px solid var(--border-color, #1e293b)',
            padding: '1rem 1.25rem',
            display: 'flex',
            alignItems: 'center',
            gap: '1rem',
            flexWrap: 'wrap'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1' }}>Report Type:</span>
              <select
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                style={{
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid rgba(255,255,255,0.15)',
                  borderRadius: '6px',
                  color: '#f8fafc',
                  padding: '0.4rem 0.65rem',
                  fontSize: '0.8rem'
                }}
              >
                <option value="incident_lifecycle">10-Step Guided Incident Lifecycle Investigation</option>
                <option value="executive_summary">Executive Cloud Resilience & Posture Summary</option>
                <option value="cascade_analysis">Deep-Dive Cascading Blast Radius Analysis</option>
                <option value="recovery_validation">5-Pillar Recovery Verification Audit</option>
              </select>
            </div>

            <div style={{ flex: 1, minWidth: '220px' }}>
              <input
                type="text"
                placeholder="Optional custom title (e.g., Q4 Tier-0 Payment Cascade Post-Mortem)"
                value={reportTitle}
                onChange={(e) => setReportTitle(e.target.value)}
                style={{
                  width: '100%',
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid rgba(255,255,255,0.15)',
                  borderRadius: '6px',
                  color: '#f8fafc',
                  padding: '0.4rem 0.75rem',
                  fontSize: '0.8rem'
                }}
              />
            </div>

            <button
              onClick={handleGenerateReport}
              disabled={generatingReport}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.45rem 1rem',
                borderRadius: '6px',
                border: 'none',
                background: 'linear-gradient(135deg, #0284c7, #2563eb)',
                color: '#ffffff',
                fontWeight: 600,
                fontSize: '0.82rem',
                cursor: generatingReport ? 'not-allowed' : 'pointer'
              }}
            >
              <Plus size={14} />
              <span>{generatingReport ? 'Generating...' : 'Generate Report'}</span>
            </button>
          </div>

          {/* Master-Detail Layout */}
          <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '1.25rem' }}>
            {/* Reports List */}
            <div style={{
              background: 'var(--card-bg, #0f172a)',
              borderRadius: '10px',
              border: '1px solid var(--border-color, #1e293b)',
              padding: '1rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem',
              maxHeight: '620px',
              overflowY: 'auto'
            }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                Generated Reports ({reports.length})
              </div>

              {reports.map((rep) => {
                const isSelected = selectedReport?.id === rep.id;
                return (
                  <div
                    key={rep.id}
                    onClick={() => setSelectedReport(rep)}
                    style={{
                      padding: '0.75rem',
                      borderRadius: '8px',
                      background: isSelected ? 'rgba(56, 189, 248, 0.15)' : 'rgba(30, 41, 59, 0.4)',
                      border: isSelected ? '1px solid #38bdf8' : '1px solid rgba(255,255,255,0.06)',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                  >
                    <div style={{ fontSize: '0.82rem', fontWeight: 600, color: isSelected ? '#38bdf8' : '#f8fafc' }}>
                      {rep.report_title}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: '#94a3b8', marginTop: '0.2rem' }}>
                      Type: {rep.report_type}
                    </div>
                    <div style={{ fontSize: '0.68rem', color: '#64748b', marginTop: '0.3rem' }}>
                      {new Date(rep.created_at).toLocaleString()}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Report Viewer */}
            <div style={{
              background: 'var(--card-bg, #0f172a)',
              borderRadius: '10px',
              border: '1px solid var(--border-color, #1e293b)',
              padding: '1.25rem',
              display: 'flex',
              flexDirection: 'column'
            }}>
              {!selectedReport ? (
                <EmptyState
                  title="No Report Selected"
                  description="Select a report from the list or generate a new one using the controls above."
                />
              ) : (
                <>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color, #1e293b)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
                    <div>
                      <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0, color: 'var(--text-primary, #f8fafc)' }}>
                        {selectedReport.report_title}
                      </h3>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
                        ID: {selectedReport.id} | Generated: {new Date(selectedReport.created_at).toLocaleString()}
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <button
                        onClick={handleCopyReport}
                        className="header-secondary-btn"
                        style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', padding: '0.35rem 0.65rem', borderRadius: '4px', cursor: 'pointer' }}
                        title="Copy Markdown"
                      >
                        {copiedReport ? <Check size={13} color="#10b981" /> : <Copy size={13} />}
                        <span>{copiedReport ? 'Copied' : 'Copy'}</span>
                      </button>

                      <button
                        onClick={() => window.print()}
                        className="header-secondary-btn"
                        style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', padding: '0.35rem 0.65rem', borderRadius: '4px', cursor: 'pointer' }}
                        title="Print / PDF"
                      >
                        <Printer size={13} />
                        <span>Print</span>
                      </button>
                    </div>
                  </div>

                  <div style={{
                    background: '#090d16',
                    padding: '1.25rem',
                    borderRadius: '8px',
                    border: '1px solid rgba(255,255,255,0.06)',
                    maxHeight: '520px',
                    overflowY: 'auto',
                    fontSize: '0.88rem',
                    lineHeight: '1.6',
                    color: '#cbd5e1',
                    whiteSpace: 'pre-line'
                  }}>
                    {selectedReport.report_content}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: KNOWLEDGE BASE */}
      {activeTab === 'knowledge' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Filter Bar */}
          <div style={{
            background: 'var(--card-bg, #0f172a)',
            borderRadius: '10px',
            border: '1px solid var(--border-color, #1e293b)',
            padding: '1rem 1.25rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1rem',
            flexWrap: 'wrap'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Category:</span>
                <select
                  value={kbCategory}
                  onChange={(e) => setKbCategory(e.target.value)}
                  style={{
                    background: 'rgba(15, 23, 42, 0.8)',
                    border: '1px solid rgba(255,255,255,0.15)',
                    borderRadius: '6px',
                    color: '#f8fafc',
                    padding: '0.35rem 0.6rem',
                    fontSize: '0.78rem'
                  }}
                >
                  <option value="ALL">All Categories</option>
                  <option value="PLAYBOOK">Incident Playbooks</option>
                  <option value="SOP">Standard Operating Procedures</option>
                  <option value="POSTMORTEM">Past Post-Mortems</option>
                  <option value="TROUBLESHOOTING">Troubleshooting Guides</option>
                </select>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'rgba(15, 23, 42, 0.8)', padding: '0.35rem 0.65rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.1)' }}>
                <Search size={14} color="#94a3b8" />
                <input
                  type="text"
                  placeholder="Search articles..."
                  value={kbSearch}
                  onChange={(e) => setKbSearch(e.target.value)}
                  style={{ background: 'transparent', border: 'none', color: '#f8fafc', fontSize: '0.8rem', outline: 'none' }}
                />
              </div>
            </div>

            <button
              onClick={() => setIsNewArticleOpen(true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.45rem 1rem',
                borderRadius: '6px',
                border: 'none',
                background: 'linear-gradient(135deg, #0ea5e9, #6366f1)',
                color: '#ffffff',
                fontWeight: 600,
                fontSize: '0.82rem',
                cursor: 'pointer'
              }}
            >
              <Plus size={14} />
              <span>New Knowledge Article</span>
            </button>
          </div>

          {/* Master Detail Layout */}
          <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: '1.25rem' }}>
            {/* Articles List */}
            <div style={{
              background: 'var(--card-bg, #0f172a)',
              borderRadius: '10px',
              border: '1px solid var(--border-color, #1e293b)',
              padding: '1rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem',
              maxHeight: '620px',
              overflowY: 'auto'
            }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                Articles ({filteredArticles.length})
              </div>

              {filteredArticles.map(art => {
                const isSelected = selectedArticle?.id === art.id;
                return (
                  <div
                    key={art.id}
                    onClick={() => setSelectedArticle(art)}
                    style={{
                      padding: '0.75rem',
                      borderRadius: '8px',
                      background: isSelected ? 'rgba(14, 165, 233, 0.15)' : 'rgba(30, 41, 59, 0.4)',
                      border: isSelected ? '1px solid #0ea5e9' : '1px solid rgba(255,255,255,0.06)',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <span style={{ fontSize: '0.82rem', fontWeight: 600, color: isSelected ? '#38bdf8' : '#f8fafc' }}>
                        {art.title}
                      </span>
                    </div>
                    <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.35rem', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.68rem', background: '#3b82f622', color: '#60a5fa', padding: '0.1rem 0.35rem', borderRadius: '3px' }}>
                        {art.category}
                      </span>
                      {art.service_id && (
                        <span style={{ fontSize: '0.68rem', color: '#94a3b8' }}>
                          svc: {art.service_id}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Article Detail Viewer */}
            <div style={{
              background: 'var(--card-bg, #0f172a)',
              borderRadius: '10px',
              border: '1px solid var(--border-color, #1e293b)',
              padding: '1.25rem',
              display: 'flex',
              flexDirection: 'column'
            }}>
              {!selectedArticle ? (
                <EmptyState
                  title="No Article Selected"
                  description="Select a knowledge article to read the full operational guidance."
                />
              ) : (
                <>
                  <div style={{ borderBottom: '1px solid var(--border-color, #1e293b)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0, color: 'var(--text-primary, #f8fafc)' }}>
                      {selectedArticle.title}
                    </h3>
                    <div style={{ display: 'flex', gap: '1rem', marginTop: '0.4rem', fontSize: '0.75rem', color: '#94a3b8' }}>
                      <span>Category: <strong style={{ color: '#38bdf8' }}>{selectedArticle.category}</strong></span>
                      <span>Author: {selectedArticle.author || 'Administrator'}</span>
                      <span>Updated: {new Date(selectedArticle.updated_at).toLocaleString()}</span>
                    </div>
                  </div>

                  <div style={{
                    background: '#090d16',
                    padding: '1.25rem',
                    borderRadius: '8px',
                    border: '1px solid rgba(255,255,255,0.06)',
                    maxHeight: '520px',
                    overflowY: 'auto',
                    fontSize: '0.88rem',
                    lineHeight: '1.6',
                    color: '#cbd5e1',
                    whiteSpace: 'pre-line'
                  }}>
                    {selectedArticle.content}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* New Article Modal */}
      {isNewArticleOpen && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '1rem'
        }}>
          <div style={{
            background: '#0f172a',
            border: '1px solid #334155',
            borderRadius: '10px',
            width: '100%',
            maxWidth: '650px',
            padding: '1.5rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            boxShadow: '0 10px 25px rgba(0,0,0,0.5)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, margin: 0, color: '#f8fafc' }}>
                New Resilience Knowledge Article
              </h3>
              <button
                onClick={() => setIsNewArticleOpen(false)}
                style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '1.2rem' }}
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleCreateArticle} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.25rem' }}>
                  Article Title:
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., SOP: Handling Payment Gateway Timeout Storm"
                  value={newArticleData.title}
                  onChange={(e) => setNewArticleData(prev => ({ ...prev, title: e.target.value }))}
                  style={{ width: '100%', background: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '6px', color: '#f8fafc', padding: '0.5rem 0.75rem', fontSize: '0.85rem' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.25rem' }}>
                    Category:
                  </label>
                  <select
                    value={newArticleData.category}
                    onChange={(e) => setNewArticleData(prev => ({ ...prev, category: e.target.value }))}
                    style={{ width: '100%', background: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '6px', color: '#f8fafc', padding: '0.5rem 0.75rem', fontSize: '0.85rem' }}
                  >
                    <option value="PLAYBOOK">Incident Playbook</option>
                    <option value="SOP">Standard Operating Procedure</option>
                    <option value="POSTMORTEM">Post-Mortem Record</option>
                    <option value="TROUBLESHOOTING">Troubleshooting Guide</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.25rem' }}>
                    Target Service ID (Optional):
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., payment-service"
                    value={newArticleData.service_id}
                    onChange={(e) => setNewArticleData(prev => ({ ...prev, service_id: e.target.value }))}
                    style={{ width: '100%', background: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '6px', color: '#f8fafc', padding: '0.5rem 0.75rem', fontSize: '0.85rem' }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.25rem' }}>
                  Markdown Content:
                </label>
                <textarea
                  rows={8}
                  required
                  placeholder="## Summary\nDescribe symptoms...\n\n## Action Items\n1. Inspect circuit breaker\n2. Shift traffic..."
                  value={newArticleData.content}
                  onChange={(e) => setNewArticleData(prev => ({ ...prev, content: e.target.value }))}
                  style={{ width: '100%', background: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '6px', color: '#f8fafc', padding: '0.5rem 0.75rem', fontSize: '0.82rem', fontFamily: 'monospace' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                <button
                  type="button"
                  onClick={() => setIsNewArticleOpen(false)}
                  className="header-secondary-btn"
                  style={{ padding: '0.45rem 1rem', borderRadius: '6px', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '0.45rem 1.25rem',
                    borderRadius: '6px',
                    border: 'none',
                    background: 'linear-gradient(135deg, #0ea5e9, #6366f1)',
                    color: '#ffffff',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  Publish Article
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
