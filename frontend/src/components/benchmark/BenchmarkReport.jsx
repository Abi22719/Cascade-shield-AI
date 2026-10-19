import React, { useState, useEffect } from 'react';
import { benchmarkApi } from '../../services/benchmarkApi';

export default function BenchmarkReport({ experimentId }) {
  const [reportMarkdown, setReportMarkdown] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!experimentId) return;
    setLoading(true);
    benchmarkApi
      .getReport(experimentId, 'markdown')
      .then((data) => {
        setReportMarkdown(typeof data === 'string' ? data : JSON.stringify(data, null, 2));
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [experimentId]);

  if (!experimentId) {
    return (
      <div className="bm-card">
        <div className="bm-card-header">
          <h3><span>📄</span> Benchmark Evaluation Report</h3>
        </div>
        <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
          Select or run an experiment to generate a detailed benchmark evaluation report.
        </p>
      </div>
    );
  }

  const handleDownloadCsv = () => {
    window.open(benchmarkApi.getExportCsvUrl(experimentId), '_blank');
  };

  const handleDownloadJson = async () => {
    try {
      const data = await benchmarkApi.getExportJson(experimentId);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `benchmark_experiment_${experimentId}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(`Export failed: ${err.message}`);
    }
  };

  return (
    <div className="bm-card">
      <div className="bm-card-header">
        <h3><span>📄</span> Benchmark Evaluation Report & Data Exports</h3>
        <div style={{ display: 'flex', gap: '0.6rem' }}>
          <button className="btn-bm-secondary" onClick={handleDownloadCsv}>
            📥 Export CSV
          </button>
          <button className="btn-bm-secondary" onClick={handleDownloadJson}>
            📥 Export JSON
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ color: '#94a3b8', padding: '1rem', textAlign: 'center' }}>
          Generating formatted report...
        </div>
      ) : error ? (
        <div style={{ color: '#f87171', padding: '1rem' }}>{error}</div>
      ) : (
        <pre className="bm-report-pre">{reportMarkdown}</pre>
      )}
    </div>
  );
}
