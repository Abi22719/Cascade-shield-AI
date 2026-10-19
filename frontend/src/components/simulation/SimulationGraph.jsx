import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';

try {
  cytoscape.use(dagre);
} catch (e) {
  // Already registered
}

export default function SimulationGraph({
  topologyGraph,
  stepServices = {},
  activeEvents = [],
  selectedServiceId,
  onSelectService
}) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  // Initialize Cytoscape Instance
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
            'content': 'data(label)',
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
            'transition-property': 'background-color, border-color, border-width',
            'transition-duration': '0.3s'
          }
        },
        {
          selector: 'node.HEALTHY',
          style: {
            'border-color': '#10b981',
            'background-color': '#064e3b'
          }
        },
        {
          selector: 'node.DEGRADED',
          style: {
            'border-color': '#f59e0b',
            'background-color': '#78350f'
          }
        },
        {
          selector: 'node.CRITICAL',
          style: {
            'border-color': '#ef4444',
            'background-color': '#7f1d1d',
            'border-width': 3
          }
        },
        {
          selector: 'node.RECOVERING',
          style: {
            'border-color': '#06b6d4',
            'background-color': '#164e63',
            'border-style': 'dashed'
          }
        },
        {
          selector: 'node.RECOVERED',
          style: {
            'border-color': '#3b82f6',
            'background-color': '#1e3a8a'
          }
        },
        {
          selector: 'node.initial-failure',
          style: {
            'border-width': 4,
            'border-color': '#ff0033'
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-color': '#c084fc',
            'border-width': 4
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#475569',
            'target-arrow-color': '#475569',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 0.8
          }
        },
        {
          selector: 'edge.propagation-active',
          style: {
            'width': 3.5,
            'line-color': '#f59e0b',
            'target-arrow-color': '#f59e0b',
            'line-style': 'dashed'
          }
        }
      ]
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
  }, [onSelectService]);

  // Update Elements & Layout when topologyGraph changes
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy || !topologyGraph?.nodes?.length) return;

    cy.elements().remove();

    const elements = [];
    (topologyGraph.nodes || []).forEach(n => {
      elements.push({
        group: 'nodes',
        data: {
          id: n.data.id,
          name: n.data.name || n.data.id,
          label: n.data.name || n.data.id
        }
      });
    });

    (topologyGraph.edges || []).forEach(e => {
      elements.push({
        group: 'edges',
        data: {
          id: e.data.id,
          source: e.data.source,
          target: e.data.target,
          protocol: e.data.protocol || 'sync_http'
        }
      });
    });

    cy.add(elements);

    // Apply dagre LR layout
    try {
      const layout = cy.layout({
        name: 'dagre',
        rankDir: 'LR',
        nodeSep: 40,
        rankSep: 80,
        animate: false
      });
      layout.run();
      cy.fit(undefined, 30);
    } catch (err) {
      console.warn('Dagre layout failed, fallback to grid:', err);
      cy.layout({ name: 'grid' }).run();
    }
  }, [topologyGraph]);

  // Update Node and Edge Styles dynamically at current step
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.batch(() => {
      cy.nodes().forEach(node => {
        const sid = node.id();
        const state = stepServices[sid];
        const status = state?.health_status || 'HEALTHY';
        const isInitial = state?.is_initial_failure;

        node.removeClass('HEALTHY DEGRADED CRITICAL RECOVERING RECOVERED initial-failure');
        node.addClass(status);
        if (isInitial) {
          node.addClass('initial-failure');
        }

        const baseName = node.data('name') || sid;
        const risk = state?.risk_score !== undefined ? ` (${Math.round(state.risk_score)})` : '';
        node.data('label', `${baseName}${risk}`);
      });

      // Highlight active propagation edges in this step
      const propagationServiceIds = new Set(
        activeEvents
          .filter(e => e.event_type === 'PROPAGATION_WAVE')
          .map(e => e.service_id)
      );

      cy.edges().forEach(edge => {
        const targetId = edge.data('target');
        const sourceId = edge.data('source');
        if (propagationServiceIds.has(sourceId) || propagationServiceIds.has(targetId)) {
          edge.addClass('propagation-active');
        } else {
          edge.removeClass('propagation-active');
        }
      });
    });
  }, [stepServices, activeEvents]);

  // Handle selected service highlight
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.nodes().unselect();
    if (selectedServiceId) {
      const target = cy.getElementById(selectedServiceId);
      if (target && target.length > 0) {
        target.select();
      }
    }
  }, [selectedServiceId]);

  return (
    <div className="sim-graph-canvas-wrapper">
      <div ref={containerRef} className="sim-graph-canvas" />

      {/* Control Buttons Overlay */}
      <div style={{ position: 'absolute', top: 10, right: 10, display: 'flex', gap: '0.35rem', zIndex: 10 }}>
        <button
          className="btn-sim-secondary"
          style={{ padding: '0.3rem 0.5rem' }}
          onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 1.25)}
          title="Zoom In"
        >
          <ZoomIn size={14} />
        </button>
        <button
          className="btn-sim-secondary"
          style={{ padding: '0.3rem 0.5rem' }}
          onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 0.8)}
          title="Zoom Out"
        >
          <ZoomOut size={14} />
        </button>
        <button
          className="btn-sim-secondary"
          style={{ padding: '0.3rem 0.5rem' }}
          onClick={() => cyRef.current?.fit(undefined, 30)}
          title="Fit Canvas"
        >
          <Maximize2 size={14} />
        </button>
      </div>

      {/* Legend */}
      <div className="sim-graph-legend">
        <div className="legend-item">
          <div className="legend-color-dot dot-initial"></div>
          <span>Initial Failure</span>
        </div>
        <div className="legend-item">
          <div className="legend-color-dot dot-propagated"></div>
          <span>Propagated Impact</span>
        </div>
        <div className="legend-item">
          <div className="legend-color-dot dot-recovering"></div>
          <span>Recovering</span>
        </div>
        <div className="legend-item">
          <div className="legend-color-dot dot-healthy"></div>
          <span>Healthy</span>
        </div>
      </div>
    </div>
  );
}
