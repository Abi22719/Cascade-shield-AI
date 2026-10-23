import React, { useState, useEffect, useCallback } from 'react';
import { 
  FileText, 
  Download, 
  Plus, 
  RefreshCw, 
  CheckCircle2, 
  FileCode, 
  Table, 
  Calendar,
  Layers,
  ExternalLink,
  Printer,
  Copy,
  Check
} from 'lucide-react';
import { dashboardApi } from '../services/dashboardApi';
import SkeletonLoader from '../components/common/SkeletonLoader';
import EmptyState from '../components/common/EmptyState';

export default function ReportsPage() {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportType, setReportType] = useState('incident_lifecycle');
  const [reportTitle, setReportTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [copied, setCopied] = useState(false);

  const loadReports = useCallback(async () => {
    setLoading(true);
    try {
      const data = await dashboardApi.listReports();
      setReports(data.reports || []);
      if (data.reports?.length > 0 && !selectedReport) {
        setSelectedReport(data.reports[0]);
      }
    } catch (err) {
      console.error("Error loading reports:", err);
    } finally {
      setLoading(false);
    }
  }, [selectedReport]);

  useEffect(() => {
    loadReports();
  }, [loadReports]);

  const handleGenerate = async () => {
    setGenerating(true);
    setStatusMessage(null);
    try {
      const rep = await dashboardApi.generateReport({
        report_type: reportType,
        report_title: reportTitle.trim() || undefined,
        data_source: 'simulated',
        report_format: 'markdown'
      });
      setStatusMessage(`Report '${rep.report_title}' generated successfully!`);
      setSelectedReport(rep);
      await loadReports();
    } catch (err) {
      setStatusMessage(`Failed to generate report: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleExportCsv = async (reportId) => {
    try {
      const csvData = await dashboardApi.exportReportCsv(reportId);
      const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `cascadeshield-report-${reportId.substring(0, 8)}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      alert(`CSV Export error: ${err.message}`);
    }
  };

  const handleExportJson = async (reportId) => {
    try {
      const jsonData = await dashboardApi.exportReportJson(reportId);
      const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `cascadeshield-report-${reportId.substring(0, 8)}.json`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      alert(`JSON Export error: ${err.message}`);
    }
  };

  const handleCopyMarkdown = () => {
    if (!selectedReport?.content) return;
    navigator.clipboard.writeText(selectedReport.content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2200);
    });
  };

  const handlePrintPdf = () => {
    window.print();
  };

  return (
    <div className="reports-page">
      {/* Header */}
      <div className="db-header">
        <div className="db-title-group">
          <h2>
            <FileText size={24} color="#38bdf8" />
            <span>Unified Reports Center & Export Engine</span>
          </h2>
          <p>
            Synthesize audit documentation across all 10 modules: service health, causal evidence, simulated recoveries, and benchmark evaluations.
          </p>
        </div>

        <div className="db-header-actions">
          <button 
            className="btn btn-secondary" 
            onClick={loadReports} 
            disabled={loading}
            title="Refresh reports catalog"
          >
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {statusMessage && (
        <div style={{ background: 'rgba(56, 189, 248, 0.15)', border: '1px solid rgba(56, 189, 248, 0.3)', borderRadius: '8px', padding: '0.75rem 1rem', color: '#7dd3fc', fontSize: '0.88rem' }}>
          {statusMessage}
        </div>
      )}

      {/* Generator Controls */}
      <div className="report-generator-card">
        <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)' }}>
          Generate New System Report
        </div>
        <div className="generator-controls-row">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Report Type</label>
            <select 
              className="db-select"
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
            >
              <option value="incident_lifecycle">Full-Stack Incident Lifecycle Audit (Modules 1-8)</option>
              <option value="service_health">Cloud Digital Twin Service Health (Module 1)</option>
              <option value="anomaly_detection">AI Anomaly Detection & Early Warnings (Module 2)</option>
              <option value="benchmarking">Resilience Benchmark & Evaluation Report (Module 9)</option>
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', flex: 1, minWidth: '220px' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Custom Title (Optional)</label>
            <input 
              type="text"
              className="db-select"
              placeholder="e.g. Q4 Cloud Resilience Post-Mortem"
              value={reportTitle}
              onChange={(e) => setReportTitle(e.target.value)}
            />
          </div>

          <div style={{ alignSelf: 'flex-end' }}>
            <button 
              className="btn-db-primary" 
              onClick={handleGenerate}
              disabled={generating}
            >
              <Plus size={15} />
              <span>{generating ? 'Generating...' : 'Generate Report'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Reports Split View: List on Left, Preview on Right */}
      <div className="db-columns-layout">
        {/* Left: Reports Catalog */}
        <div className="db-panel reports-sidebar">
          <div className="db-panel-header">
            <div className="db-panel-title">
              <Table size={18} color="#38bdf8" />
              <span>Generated Reports ({reports.length})</span>
            </div>
          </div>

          {loading && reports.length === 0 ? (
            <SkeletonLoader variant="card" count={3} height="80px" />
          ) : reports.length === 0 ? (
            <EmptyState
              icon={FileText}
              title="No Reports Generated"
              description="Click 'Generate Report' above to synthesize audit and incident post-mortems."
            />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', maxHeight: '550px', overflowY: 'auto' }}>
              {reports.map((rep) => {
                const isSelected = selectedReport?.id === rep.id;
                return (
                  <div 
                    key={rep.id}
                    onClick={() => setSelectedReport(rep)}
                    style={{
                      padding: '0.85rem 1rem',
                      borderRadius: '8px',
                      background: isSelected ? 'rgba(56, 189, 248, 0.15)' : 'var(--bg-card)',
                      border: isSelected ? '1px solid #38bdf8' : '1px solid var(--border-color)',
                      cursor: 'pointer',
                      transition: 'all 0.15s'
                    }}
                  >
                    <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.9rem' }}>
                      {rep.report_title}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.35rem', fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                      <span>Type: <code>{rep.report_type}</code></span>
                      <span>{new Date(rep.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right: Report Viewer & Exporter */}
        <div className="db-panel reports-preview-card">
          <div className="db-panel-header">
            <div className="db-panel-title">
              <FileCode size={18} color="#38bdf8" />
              <span>Report Preview & Export</span>
            </div>

            {selectedReport && (
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                <button 
                  className="btn-db-secondary" 
                  style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
                  onClick={handleCopyMarkdown}
                  title="Copy Raw Markdown to Clipboard"
                >
                  {copied ? <Check size={13} color="#10b981" /> : <Copy size={13} />}
                  <span>{copied ? 'Copied' : 'Copy MD'}</span>
                </button>

                <button 
                  className="btn-db-secondary" 
                  style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
                  onClick={handlePrintPdf}
                  title="Print / Save Executive PDF"
                >
                  <Printer size={13} />
                  <span>Print PDF</span>
                </button>

                <button 
                  className="btn-db-secondary" 
                  style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
                  onClick={() => handleExportCsv(selectedReport.id)}
                  title="Download as CSV"
                >
                  <Download size={13} />
                  <span>CSV</span>
                </button>

                <button 
                  className="btn-db-secondary" 
                  style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
                  onClick={() => handleExportJson(selectedReport.id)}
                  title="Download as JSON"
                >
                  <Download size={13} />
                  <span>JSON</span>
                </button>
              </div>
            )}
          </div>

          {selectedReport ? (
            <div>
              <div style={{ marginBottom: '0.75rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                ID: <code>{selectedReport.id}</code> | Format: <code>{selectedReport.report_format}</code> | Source: <code>{selectedReport.data_source}</code>
              </div>
              <div className="report-preview-pane">
                {selectedReport.content}
              </div>
            </div>
          ) : (
            <EmptyState
              icon={FileText}
              title="No Report Selected"
              description="Select a report from the catalog to preview its audit evidence, markdown, and export options."
            />
          )}
        </div>
      </div>
    </div>
  );
}
