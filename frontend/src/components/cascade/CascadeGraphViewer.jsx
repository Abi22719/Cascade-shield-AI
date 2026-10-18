import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw } from 'lucide-react';

try {
  cytoscape.use(dagre);
} catch (e) {
  // Already registered
}

export default function CascadeGraphViewer({
  graphData,
  prediction,
  currentStep = null,
  selectedServiceId = null,
  onSelectService
}) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  // Initialize Cytoscape
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
            'height': 52,
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
            'arrow-scale': 0.8,
            'transition-property': 'line-color, target-arrow-color, width',
            'transition-duration': '0.3s'
          }
        },
        // Root Failure Node Style
        {
          selector: '.node-root-failure',
          style: {
            'background-color': '#ef4444',
            'border-color': '#fca5a5',
            'border-width': 4,
            'width': 125,
            'height': 60,
            'color': '#ffffff',
            'font-weight': 700
          }
        },
        // Direct Impact Node Style (Hop 1)
        {
          selector: '.node-direct-impact',
          style: {
            'background-color': '#f97316',
            'border-color': '#fdba74',
            'border-width': 3,
            'color': '#ffffff'
          }
        },
        // Indirect Impact Node Style (Hop 2+)
        {
          selector: '.node-indirect-impact',
          style: {
            'background-color': '#ca8a04',
            'border-color': '#fde047',
            'border-width': 2.5,
            'color': '#ffffff'
          }
        },
        // Safe / Unaffected Node Style
        {
          selector: '.node-safe',
          style: {
            'background-color': '#064e3b',
            'border-color': '#10b981',
            'border-width': 1.5,
            'color': '#a7f3d0'
          }
        },
        // Propagation Edge Style (Dashed animated line)
        {
          selector: '.edge-propagation-path',
          style: {
            'width': 3,
            'line-color': '#f97316',
            'target-arrow-color': '#f97316',
            'line-style': 'dashed',
            'target-arrow-shape': 'triangle'
          }
        },
        // Selected node border
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

  // Update visual states whenever prediction, currentStep, or selection changes
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    // Reset classes
    cy.nodes().removeClass('node-root-failure node-direct-impact node-indirect-impact node-safe');
    cy.edges().removeClass('edge-propagation-path');

    if (!prediction) {
      return;
    }

    const rootId = prediction.initial_service_id;
    const impactedMap = new Map();
    prediction.impacted_services?.forEach(s => {
      impactedMap.set(s.service_id, s);
    });

    // Check step constraint if scrubber is active
    cy.nodes().forEach(node => {
      const id = node.id();
      const impact = impactedMap.get(id);

      if (id === rootId) {
        node.addClass('node-root-failure');
      } else if (impact) {
        // If currentStep is specified, only highlight if onset <= currentStep
        if (currentStep === null || impact.estimated_step_onset <= currentStep) {
          if (impact.impact_type === 'Direct') {
            node.addClass('node-direct-impact');
          } else {
            node.addClass('node-indirect-impact');
          }
        } else {
          node.addClass('node-safe');
        }
      } else {
        node.addClass('node-safe');
      }
    });

    // Highlight propagation edges
    // In digital twin: u -> v means u depends on v.
    // In failure propagation: failure travels from v to u (callee to caller).
    // An edge in graphData has source = caller (u), target = callee (v).
    // If v is failing and u is impacted, edge (u -> v) is an affected communication channel!
    cy.edges().forEach(edge => {
      const callerId = edge.data('source');
      const calleeId = edge.data('target');

      const calleeImpacted = impactedMap.has(calleeId);
      const callerImpacted = impactedMap.has(callerId);

      if (calleeImpacted && callerImpacted) {
        edge.addClass('edge-propagation-path');
      }
    });

    // Handle service selection focus
    if (selectedServiceId) {
      const targetNode = cy.getElementById(selectedServiceId);
      if (targetNode && targetNode.length) {
        cy.nodes().unselect();
        targetNode.select();
      }
    }
  }, [prediction, currentStep, selectedServiceId]);

  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.25);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() * 0.8);
  const handleFit = () => cyRef.current?.fit(undefined, 30);
  const handleReset = () => {
    const cy = cyRef.current;
    if (!cy) return;
    cy.layout({
      name: 'dagre',
      rankDir: 'LR',
      nodeSep: 45,
      rankSep: 65,
      padding: 25
    }).run();
  };

  return (
    <div className="cascade-graph-wrapper">
      <div className="graph-top-bar">
        <div className="graph-legend-group">
          <div className="legend-item">
            <span className="legend-dot root" /> Root Incident
          </div>
          <div className="legend-item">
            <span className="legend-dot direct" /> Direct Caller (Hop 1)
          </div>
          <div className="legend-item">
            <span className="legend-dot indirect" /> Indirect Caller (Hop 2+)
          </div>
          <div className="legend-item">
            <span className="legend-dot safe" /> Unaffected
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
