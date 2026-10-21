import React, { useEffect, useRef, useState, useCallback } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, Target, Loader2 } from 'lucide-react';

// Register dagre layout once
if (!cytoscape.prototype._dagreRegistered) {
  cytoscape.use(dagre);
  cytoscape.prototype._dagreRegistered = true;
}

// Helper to extract Cytoscape elements from any graphData shape
function extractElements(graphData) {
  if (!graphData) return [];
  if (Array.isArray(graphData)) return graphData;
  if (graphData.elements) {
    if (Array.isArray(graphData.elements)) return graphData.elements;
    return [
      ...(graphData.elements.nodes || []),
      ...(graphData.elements.edges || [])
    ];
  }

  const nodes = (graphData.nodes || []).map(n => ({
    group: 'nodes',
    data: {
      id: n.data?.id || n.id,
      name: n.data?.name || n.name || n.data?.id || n.id,
      health_status: n.data?.health_status || n.health_status || 'HEALTHY',
      service_type: n.data?.service_type || n.service_type || 'compute',
      ...n.data
    }
  }));

  const edges = (graphData.edges || []).map(e => ({
    group: 'edges',
    data: {
      id: e.data?.id || e.id || `${e.data?.source || e.source}->${e.data?.target || e.target}`,
      source: e.data?.source || e.source,
      target: e.data?.target || e.target,
      dependency_type: e.data?.dependency_type || e.dependency_type || 'sync_http',
      ...e.data
    }
  }));

  return [...nodes, ...edges];
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
  const onSelectServiceRef = useRef(onSelectService);
  const [hasElements, setHasElements] = useState(false);

  useEffect(() => {
    onSelectServiceRef.current = onSelectService;
  }, [onSelectService]);

  // Layout Runner
  const runLayout = useCallback(() => {
    const cy = cyRef.current;
    if (!cy || cy.elements().length === 0) return;

    cy.resize();

    try {
      const layout = cy.layout({
        name: 'dagre',
        rankDir: 'LR',
        nodeSep: 45,
        rankSep: 80,
        padding: 40,
        fit: true,
        animate: false
      });

      layout.one('layoutstop', () => {
        cy.resize();
        cy.fit(undefined, 40);
      });

      layout.run();
    } catch (err) {
      console.warn('Dagre layout failed, using breadthfirst:', err);
      const fallback = cy.layout({ name: 'breadthfirst', directed: true, padding: 35, fit: true, animate: false });
      fallback.one('layoutstop', () => {
        cy.resize();
        cy.fit(undefined, 35);
      });
      fallback.run();
    }
  }, []);

  // 1. Initialize Cytoscape Instance (Runs ONCE on mount)
  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      boxSelectionEnabled: false,
      autounselectify: false,
      minZoom: 0.15,
      maxZoom: 3.5,
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
            'text-max-width': '95px',
            'width': 115,
            'height': 52,
            'shape': 'round-rectangle',
            'background-color': '#141e33',
            'border-width': 2,
            'border-color': '#334155',
            'transition-property': 'background-color, border-color, border-width, width, height',
            'transition-duration': '0.2s',
            'overlay-opacity': 0
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#334155',
            'target-arrow-color': '#475569',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 1.0,
            'opacity': 0.85,
            'overlay-opacity': 0
          }
        },
        // Primary Root Cause Node
        {
          selector: '.node-primary-rca',
          style: {
            'background-color': '#2d1418',
            'border-color': '#ef4444',
            'border-width': 3.5,
            'color': '#ffffff',
            'font-weight': 700,
            'width': 125,
            'height': 58,
            'underlay-color': '#ef4444',
            'underlay-padding': 6,
            'underlay-opacity': 0.5,
            'underlay-shape': 'round-rectangle'
          }
        },
        // Secondary Candidate Node
        {
          selector: '.node-candidate',
          style: {
            'background-color': '#27102e',
            'border-color': '#c026d3',
            'border-width': 3,
            'color': '#ffffff',
            'underlay-color': '#c026d3',
            'underlay-padding': 4,
            'underlay-opacity': 0.4,
            'underlay-shape': 'round-rectangle'
          }
        },
        // Affected Caller Node
        {
          selector: '.node-affected',
          style: {
            'background-color': '#2a2012',
            'border-color': '#f59e0b',
            'border-width': 2.5,
            'color': '#ffffff',
            'underlay-color': '#f59e0b',
            'underlay-padding': 4,
            'underlay-opacity': 0.35,
            'underlay-shape': 'round-rectangle'
          }
        },
        // Propagation Edge
        {
          selector: '.edge-rca-path',
          style: {
            'width': 3.5,
            'line-color': '#ef4444',
            'target-arrow-color': '#ef4444',
            'line-style': 'dashed',
            'target-arrow-shape': 'triangle',
            'opacity': 1.0
          }
        },
        {
          selector: ':selected, .is-selected',
          style: {
            'border-color': '#38bdf8',
            'border-width': 4,
            'underlay-color': '#0ea5e9',
            'underlay-padding': 5,
            'underlay-opacity': 0.5,
            'underlay-shape': 'round-rectangle'
          }
        }
      ]
    });

    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      if (onSelectServiceRef.current) {
        onSelectServiceRef.current(node.id());
      }
    });

    cyRef.current = cy;

    // ResizeObserver on the viewport container
    let resizeTimer = null;
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.contentRect.width > 0 && entry.contentRect.height > 0) {
          clearTimeout(resizeTimer);
          resizeTimer = setTimeout(() => {
            if (cy && !cy.destroyed() && cy.elements().length > 0) {
              cy.resize();
              cy.fit(undefined, 40);
            }
          }, 80);
        }
      }
    });

    resizeObserver.observe(containerRef.current);

    // Initial load if graphData was already present on mount
    if (graphData) {
      const elements = extractElements(graphData);
      if (elements.length > 0) {
        cy.add(elements);
        setHasElements(true);
        requestAnimationFrame(() => {
          setTimeout(() => {
            if (!cy.destroyed()) runLayout();
          }, 30);
        });
      }
    }

    return () => {
      clearTimeout(resizeTimer);
      resizeObserver.disconnect();
      cy.destroy();
      cyRef.current = null;
    };
  }, []);

  // 2. Load Elements when graphData arrives or updates
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy || !graphData) return;

    const elements = extractElements(graphData);

    cy.batch(() => {
      cy.elements().remove();
      if (elements.length > 0) {
        cy.add(elements);
      }
    });

    if (elements.length > 0) {
      setHasElements(true);
      requestAnimationFrame(() => {
        setTimeout(() => {
          if (cy && !cy.destroyed() && cy.elements().length > 0) {
            runLayout();
          }
        }, 40);
      });
    } else {
      setHasElements(false);
    }
  }, [graphData, runLayout]);

  // 3. Update Visual Highlight Styles
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy || cy.elements().length === 0) return;

    cy.batch(() => {
      cy.nodes().removeClass('node-primary-rca node-candidate node-affected is-selected');
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

        if (id === selectedServiceId) {
          node.addClass('is-selected');
        }
      });

      // Highlight edges connecting root cause, candidates, or affected callers
      cy.edges().forEach(edge => {
        const src = edge.data('source');
        const tgt = edge.data('target');
        const isRootConnected = (src === primaryRootCauseId || tgt === primaryRootCauseId);
        const isCandidateConnected = candidateIds.includes(src) || candidateIds.includes(tgt);
        const isAffectedConnected = affectedServiceIds.includes(src) || affectedServiceIds.includes(tgt);

        if (isRootConnected || (isCandidateConnected && isAffectedConnected)) {
          edge.addClass('edge-rca-path');
        }
      });
    });

    if (selectedServiceId && cy && cy.elements().length > 0) {
      const match = cy.$id(selectedServiceId);
      if (match.length > 0) {
        requestAnimationFrame(() => {
          if (!cy.destroyed() && cy.elements().length > 0) {
            cy.animate({
              center: { eles: match },
              duration: 250
            });
          }
        });
      }
    }
  }, [primaryRootCauseId, candidateIds, affectedServiceIds, selectedServiceId]);

  const handleZoomIn = () => {
    if (cyRef.current) {
      cyRef.current.zoom({
        level: cyRef.current.zoom() * 1.3,
        renderedPosition: { x: cyRef.current.width() / 2, y: cyRef.current.height() / 2 }
      });
    }
  };

  const handleZoomOut = () => {
    if (cyRef.current) {
      cyRef.current.zoom({
        level: cyRef.current.zoom() / 1.3,
        renderedPosition: { x: cyRef.current.width() / 2, y: cyRef.current.height() / 2 }
      });
    }
  };

  const handleFit = () => {
    if (cyRef.current) {
      cyRef.current.resize();
      cyRef.current.fit(undefined, 35);
    }
  };

  return (
    <div className="rca-graph-panel">
      <div className="graph-top-bar">
        <div className="graph-legend-group">
          <div className="legend-item">
            <span className="legend-dot root" style={{ background: '#ef4444', boxShadow: '0 0 6px #ef4444' }} />
            <span>Primary Root Cause</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ background: '#c026d3', boxShadow: '0 0 6px #c026d3' }} />
            <span>Alternate Candidate</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot direct" style={{ background: '#f59e0b', boxShadow: '0 0 6px #f59e0b' }} />
            <span>Affected Caller</span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '6px' }}>
          <button className="timeline-btn" onClick={handleZoomIn} title="Zoom In">
            <ZoomIn size={14} />
          </button>
          <button className="timeline-btn" onClick={handleZoomOut} title="Zoom Out">
            <ZoomOut size={14} />
          </button>
          <button className="timeline-btn" onClick={handleFit} title="Fit to Viewport">
            <Maximize2 size={14} />
          </button>
          <button className="timeline-btn" onClick={runLayout} title="Reset Layout">
            <RotateCcw size={14} />
          </button>
        </div>
      </div>

      <div className="rca-canvas-wrapper">
        <div ref={containerRef} className="graph-viewport-canvas" />

        {!hasElements && (
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '10px',
            color: '#94a3b8',
            pointerEvents: 'none'
          }}>
            <Loader2 size={24} className="animate-spin" color="#8b5cf6" />
            <span style={{ fontSize: '0.85rem' }}>Loading Dependency Graph...</span>
          </div>
        )}
      </div>
    </div>
  );
}
