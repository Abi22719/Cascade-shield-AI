import React, { useEffect, useRef, useState, useCallback } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, Loader2 } from 'lucide-react';

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

export default function CascadeGraphViewer({
  graphData,
  prediction,
  currentStep = null,
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

  // Layout runner
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

  // 1. Initialize Cytoscape Instance
  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      boxSelectionEnabled: false,
      autounselectify: false,
      minZoom: 0.2,
      maxZoom: 3.0,
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
        // Root Failure Node Style
        {
          selector: '.node-root-failure',
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
        // Direct Impact Node Style (Hop 1)
        {
          selector: '.node-direct-impact',
          style: {
            'background-color': '#2e1810',
            'border-color': '#f97316',
            'border-width': 3,
            'color': '#ffffff',
            'underlay-color': '#f97316',
            'underlay-padding': 5,
            'underlay-opacity': 0.45,
            'underlay-shape': 'round-rectangle'
          }
        },
        // Indirect Impact Node Style (Hop 2+)
        {
          selector: '.node-indirect-impact',
          style: {
            'background-color': '#2a2012',
            'border-color': '#eab308',
            'border-width': 2.5,
            'color': '#ffffff',
            'underlay-color': '#eab308',
            'underlay-padding': 4,
            'underlay-opacity': 0.35,
            'underlay-shape': 'round-rectangle'
          }
        },
        // Safe / Unaffected Node Style
        {
          selector: '.node-safe',
          style: {
            'background-color': '#0f2427',
            'border-color': '#10b981',
            'border-width': 2,
            'color': '#f8fafc',
            'underlay-color': '#10b981',
            'underlay-padding': 3,
            'underlay-opacity': 0.2,
            'underlay-shape': 'round-rectangle'
          }
        },
        // Propagation Edge Style
        {
          selector: '.edge-propagation-path',
          style: {
            'width': 3.5,
            'line-color': '#f97316',
            'target-arrow-color': '#f97316',
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

    // ResizeObserver on container
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

  // 2. Load Elements when graphData arrives
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

  // 3. Update Visual States whenever prediction or currentStep changes
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy || cy.elements().length === 0) return;

    cy.batch(() => {
      cy.nodes().removeClass('node-root-failure node-direct-impact node-indirect-impact node-safe is-selected');
      cy.edges().removeClass('edge-propagation-path');

      if (!prediction) {
        cy.nodes().addClass('node-safe');
        return;
      }

      const rootId = prediction.initial_service_id;
      const impactedList = prediction.impacted_services || [];

      // Determine active impacted services based on current step
      let activeImpacted = impactedList;
      if (currentStep !== null && currentStep !== undefined && prediction.timeline) {
        const stepEntry = prediction.timeline.find(t => t.step === currentStep);
        if (stepEntry && stepEntry.active_failed_services) {
          activeImpacted = impactedList.filter(s => stepEntry.active_failed_services.includes(s.service_id));
        }
      }

      const impactedMap = new Map();
      activeImpacted.forEach(item => {
        impactedMap.set(item.service_id, item);
      });

      cy.nodes().forEach(node => {
        const id = node.id();
        if (id === rootId) {
          node.addClass('node-root-failure');
        } else if (impactedMap.has(id)) {
          const item = impactedMap.get(id);
          if (item.hop_level === 1) {
            node.addClass('node-direct-impact');
          } else {
            node.addClass('node-indirect-impact');
          }
        } else {
          node.addClass('node-safe');
        }

        if (id === selectedServiceId) {
          node.addClass('is-selected');
        }
      });

      // Highlight propagation edges
      cy.edges().forEach(edge => {
        const src = edge.data('source');
        const tgt = edge.data('target');
        const srcImpacted = (src === rootId || impactedMap.has(src));
        const tgtImpacted = impactedMap.has(tgt);

        if (srcImpacted && tgtImpacted) {
          edge.addClass('edge-propagation-path');
        }
      });
    });
  }, [prediction, currentStep, selectedServiceId]);

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
    <div className="cascade-graph-wrapper" style={{ height: '520px', minHeight: '480px' }}>
      <div className="graph-top-bar">
        <div className="graph-legend-group">
          <div className="legend-item">
            <span className="legend-dot root" style={{ background: '#ef4444', boxShadow: '0 0 6px #ef4444' }} />
            <span>Root Failure</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot direct" style={{ background: '#f97316', boxShadow: '0 0 6px #f97316' }} />
            <span>Direct (Hop 1)</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot indirect" style={{ background: '#eab308', boxShadow: '0 0 6px #eab308' }} />
            <span>Indirect (Hop 2+)</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot safe" style={{ background: '#10b981', boxShadow: '0 0 6px #10b981' }} />
            <span>Safe</span>
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

      <div style={{ position: 'relative', flex: 1, width: '100%', height: 'calc(100% - 48px)', minHeight: '430px' }}>
        <div ref={containerRef} className="graph-viewport-canvas" style={{ width: '100%', height: '100%', minHeight: '430px' }} />

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
            <Loader2 size={24} className="animate-spin" color="#f97316" />
            <span style={{ fontSize: '0.85rem' }}>Loading Dependency Graph...</span>
          </div>
        )}
      </div>
    </div>
  );
}
