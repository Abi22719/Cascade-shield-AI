import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, Target } from 'lucide-react';

try {
  cytoscape.use(dagre);
} catch (e) {
  // Already registered
}

export default function DependencyImpactGraph({
  graphData,
  primaryRootCauseId,
  candidateIds = [],
  affectedServiceIds = [],
  selectedServiceId = null,
  onSelectService
}) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      boxSelectionEnabled: false,
      wheelSensitivity: 0.25,
      style: [
        {
          selector: 'node',
          style: {
            'content': 'data(name)',
            'color': '#f8fafc',
            'font-family': 'Inter, sans-serif',
            'font-size': '11px',
            'font-weight': 600,
            'text-valign': 'center',
            'text-halign': 'center',
            'text-wrap': 'wrap',
            'text-max-width': '90px',
            'width': 110,
            'height': 50,
            'shape': 'round-rectangle',
            'background-color': '#1e293b',
            'border-width': 2,
            'border-color': '#475569',
            'transition-property': 'background-color, border-color, border-width, width, height',
            'transition-duration': '0.3s'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 1.5,
            'line-color': '#334155',
            'target-arrow-color': '#334155',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 0.8
          }
        },
        // Primary Root Cause Node
        {
          selector: '.node-primary-rca',
          style: {
            'background-color': '#dc2626',
            'border-color': '#fca5a5',
            'border-width': 4,
            'width': 125,
            'height': 58,
            'color': '#ffffff',
            'font-weight': 700
          }
        },
        // Secondary Candidate Node
        {
          selector: '.node-candidate',
          style: {
            'background-color': '#c026d3',
            'border-color': '#f0abfc',
            'border-width': 3,
            'color': '#ffffff'
          }
        },
        // Affected Caller Node
        {
          selector: '.node-affected',
          style: {
            'background-color': '#d97706',
            'border-color': '#fde68a',
            'border-width': 2.5,
            'color': '#ffffff'
          }
        },
        // Propagation Edge
        {
          selector: '.edge-rca-path',
          style: {
            'width': 3,
            'line-color': '#ef4444',
            'target-arrow-color': '#ef4444',
            'line-style': 'dashed',
            'target-arrow-shape': 'triangle'
          }
        },
        {
          selector: ':selected',
          style: {
            'border-color': '#38bdf8',
            'border-width': 4
          }
        }
      ],
      elements: graphData?.elements || { nodes: [], edges: [] },
      layout: {
        name: 'dagre',
        rankDir: 'LR',
        nodeSep: 45,
        rankSep: 65,
        padding: 25
      }
    });

    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      if (onSelectService) {
        onSelectService(node.id());
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [graphData]);

  // Update styles on data change
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.nodes().removeClass('node-primary-rca node-candidate node-affected');
    cy.edges().removeClass('edge-rca-path');

    cy.nodes().forEach(node => {
      const id = node.id();
      if (id === primaryRootCauseId) {
        node.addClass('node-primary-rca');
      } else if (candidateIds.includes(id)) {
        node.addClass('node-candidate');
      } else if (affectedServiceIds.includes(id)) {
        node.addClass('node-affected');
      }
    });

    // Highlight paths connected to primary root cause or affected services
    cy.edges().forEach(edge => {
      const src = edge.data('source');
      const tgt = edge.data('target');
      // If either end is root cause or candidate and connected to affected caller
      if (
        (src === primaryRootCauseId || tgt === primaryRootCauseId) ||
        (affectedServiceIds.includes(src) && affectedServiceIds.includes(tgt))
      ) {
        edge.addClass('edge-rca-path');
      }
    });

    if (selectedServiceId) {
      const target = cy.getElementById(selectedServiceId);
      if (target && target.length) {
        cy.nodes().unselect();
        target.select();
      }
    }
  }, [primaryRootCauseId, candidateIds, affectedServiceIds, selectedServiceId]);

  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.25);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() * 0.8);
  const handleFit = () => cyRef.current?.fit(undefined, 25);
  const handleReset = () => {
    cyRef.current?.layout({
      name: 'dagre',
      rankDir: 'LR',
      nodeSep: 45,
      rankSep: 65,
      padding: 25
    }).run();
  };

  return (
    <div className="cascade-graph-wrapper" style={{ height: '480px' }}>
      <div className="graph-top-bar">
        <div className="graph-legend-group">
          <div className="legend-item">
            <span className="legend-dot root" style={{ background: '#dc2626' }} /> Primary Root Cause
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ background: '#c026d3' }} /> Alternate Candidate
          </div>
          <div className="legend-item">
            <span className="legend-dot direct" style={{ background: '#d97706' }} /> Affected Caller
          </div>
        </div>

        <div style={{ display: 'flex', gap: '6px' }}>
          <button className="timeline-btn" onClick={handleZoomIn} title="Zoom In">
            <ZoomIn size={14} />
          </button>
          <button className="timeline-btn" onClick={handleZoomOut} title="Zoom Out">
            <ZoomOut size={14} />
          </button>
          <button className="timeline-btn" onClick={handleFit} title="Fit Graph">
            <Maximize2 size={14} />
          </button>
          <button className="timeline-btn" onClick={handleReset} title="Reset Layout">
            <RotateCcw size={14} />
          </button>
        </div>
      </div>

      <div ref={containerRef} className="graph-viewport-canvas" />
    </div>
  );
}
