import React, { useEffect, useRef, useState, useCallback } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import { 
  ZoomIn, 
  ZoomOut, 
  Maximize2, 
  RotateCcw, 
  AlertTriangle,
  Play,
  Crosshair,
  Loader2
} from 'lucide-react';

// Register dagre layout once
if (!cytoscape.prototype._dagreRegistered) {
  cytoscape.use(dagre);
  cytoscape.prototype._dagreRegistered = true;
}

export default function GraphViewer({
  graphData,
  selectedNodeId,
  selectedEdgeId,
  onSelectNode,
  onSelectEdge,
  onClearSelection,
  searchQuery,
  filterType,
  filterHealth,
  layoutName = 'dagre-lr',
  impactData = null
}) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const [highlightedCycle, setHighlightedCycle] = useState(null);
  const [isRendered, setIsRendered] = useState(false);

  // Helper to run layout reliably with viewport fitting
  const runLayout = useCallback((layoutType = layoutName) => {
    const cy = cyRef.current;
    if (!cy || cy.elements().length === 0) return;

    cy.resize();

    let layoutConfig = {
      animate: true,
      animationDuration: 350,
      fit: true,
      padding: 60
    };

    if (layoutType === 'dagre-lr') {
      layoutConfig = {
        name: 'dagre',
        rankDir: 'LR',
        nodeSep: 60,
        rankSep: 110,
        ...layoutConfig
      };
    } else if (layoutType === 'dagre-tb') {
      layoutConfig = {
        name: 'dagre',
        rankDir: 'TB',
        nodeSep: 60,
        rankSep: 90,
        ...layoutConfig
      };
    } else if (layoutType === 'breadthfirst') {
      layoutConfig = {
        name: 'breadthfirst',
        directed: true,
        spacingFactor: 1.4,
        ...layoutConfig
      };
    } else if (layoutType === 'cose') {
      layoutConfig = {
        name: 'cose',
        idealEdgeLength: 120,
        nodeOverlap: 20,
        ...layoutConfig
      };
    } else {
      layoutConfig = {
        name: 'circle',
        ...layoutConfig
      };
    }

    try {
      const layout = cy.layout(layoutConfig);
      layout.one('layoutstop', () => {
        cy.resize();
        cy.fit(undefined, 60);
      });
      layout.run();
    } catch (err) {
      console.warn('Layout execution failed, using fallback:', err);
      const fallback = cy.layout({ name: 'breadthfirst', directed: true, padding: 50, fit: true });
      fallback.one('layoutstop', () => {
        cy.resize();
        cy.fit(undefined, 50);
      });
      fallback.run();
    }
  }, [layoutName]);

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
        // Default Node Style
        {
          selector: 'node',
          style: {
            'content': 'data(name)',
            'color': '#f8fafc',
            'font-family': 'Inter, sans-serif',
            'font-size': '12px',
            'font-weight': 600,
            'text-valign': 'center',
            'text-halign': 'center',
            'text-wrap': 'wrap',
            'text-max-width': '100px',
            'width': 130,
            'height': 58,
            'shape': 'round-rectangle',
            'background-color': '#141e33',
            'border-width': 2,
            'border-color': '#334155',
            'transition-property': 'background-color, border-color, border-width, opacity, line-color, width, height',
            'transition-duration': '0.2s',
            'text-margin-y': 0,
            'overlay-opacity': 0
          }
        },
        // Health: HEALTHY
        {
          selector: 'node[health_status = "HEALTHY"]',
          style: {
            'border-color': '#10b981',
            'border-width': 2.5,
            'background-color': '#0f2427',
            'underlay-color': '#10b981',
            'underlay-padding': 3,
            'underlay-opacity': 0.25,
            'underlay-shape': 'round-rectangle'
          }
        },
        // Health: WARNING
        {
          selector: 'node[health_status = "WARNING"]',
          style: {
            'border-color': '#f59e0b',
            'border-width': 3,
            'background-color': '#2a2012',
            'underlay-color': '#f59e0b',
            'underlay-padding': 4,
            'underlay-opacity': 0.35,
            'underlay-shape': 'round-rectangle'
          }
        },
        // Health: CRITICAL
        {
          selector: 'node[health_status = "CRITICAL"]',
          style: {
            'border-color': '#ef4444',
            'border-width': 3.5,
            'background-color': '#2d1418',
            'underlay-color': '#ef4444',
            'underlay-padding': 6,
            'underlay-opacity': 0.5,
            'underlay-shape': 'round-rectangle'
          }
        },
        // Selected Node
        {
          selector: 'node:selected, node.is-selected',
          style: {
            'border-color': '#38bdf8',
            'border-width': 4,
            'border-style': 'solid',
            'underlay-color': '#0ea5e9',
            'underlay-padding': 5,
            'underlay-opacity': 0.5,
            'underlay-shape': 'round-rectangle'
          }
        },
        // Downstream Impacted Node
        {
          selector: 'node.is-impacted',
          style: {
            'border-color': '#f43f5e',
            'border-width': 3.5,
            'border-style': 'double',
            'underlay-color': '#f43f5e',
            'underlay-padding': 5,
            'underlay-opacity': 0.45,
            'underlay-shape': 'round-rectangle'
          }
        },
        // Root Service in Impact Analysis
        {
          selector: 'node.is-impact-source',
          style: {
            'border-color': '#a855f7',
            'border-width': 4,
            'underlay-color': '#a855f7',
            'underlay-padding': 6,
            'underlay-opacity': 0.55,
            'underlay-shape': 'round-rectangle'
          }
        },
        // Filter Dimmed
        {
          selector: 'node.is-dimmed, edge.is-dimmed',
          style: {
            'opacity': 0.18
          }
        },
        // Search Highlighted
        {
          selector: 'node.search-match',
          style: {
            'border-color': '#fbbf24',
            'border-width': 4,
            'underlay-color': '#fbbf24',
            'underlay-padding': 5,
            'underlay-opacity': 0.5,
            'underlay-shape': 'round-rectangle'
          }
        },
        // Cycle Node Highlight
        {
          selector: 'node.cycle-member',
          style: {
            'border-color': '#f97316',
            'border-width': 4,
            'border-style': 'dashed'
          }
        },
        // Default Edge Style
        {
          selector: 'edge',
          style: {
            'width': 2.2,
            'line-color': '#334155',
            'target-arrow-color': '#64748b',
            'target-arrow-shape': 'triangle',
            'arrow-scale': 1.2,
            'curve-style': 'bezier',
            'opacity': 0.85,
            'overlay-opacity': 0,
            'transition-property': 'line-color, target-arrow-color, width, opacity',
            'transition-duration': '0.2s'
          }
        },
        // Edge: sync_http
        {
          selector: 'edge[dependency_type = "sync_http"]',
          style: {
            'line-color': '#38bdf8',
            'target-arrow-color': '#38bdf8'
          }
        },
        // Edge: async_message
        {
          selector: 'edge[dependency_type = "async_message"]',
          style: {
            'line-color': '#a855f7',
            'target-arrow-color': '#a855f7',
            'line-style': 'dashed'
          }
        },
        // Edge: database_read_write
        {
          selector: 'edge[dependency_type = "database_read_write"]',
          style: {
            'line-color': '#10b981',
            'target-arrow-color': '#10b981'
          }
        },
        // Edge: cache_lookup
        {
          selector: 'edge[dependency_type = "cache_lookup"]',
          style: {
            'line-color': '#f59e0b',
            'target-arrow-color': '#f59e0b',
            'line-style': 'dotted'
          }
        },
        // Edge: Selected
        {
          selector: 'edge:selected, edge.is-selected',
          style: {
            'width': 4,
            'line-color': '#0ea5e9',
            'target-arrow-color': '#0ea5e9',
            'opacity': 1.0
          }
        },
        // Edge: Downstream Impact Path
        {
          selector: 'edge.is-impact-path',
          style: {
            'width': 3.5,
            'line-color': '#f43f5e',
            'target-arrow-color': '#f43f5e',
            'opacity': 1.0
          }
        },
        // Edge: Cycle Path
        {
          selector: 'edge.cycle-edge',
          style: {
            'width': 3.5,
            'line-color': '#f97316',
            'target-arrow-color': '#f97316',
            'line-style': 'dashed'
          }
        }
      ]
    });

    // Event listeners
    cy.on('tap', 'node', (e) => {
      const node = e.target;
      onSelectNode(node.data());
    });

    cy.on('tap', 'edge', (e) => {
      const edge = e.target;
      onSelectEdge(edge.data());
    });

    cy.on('tap', (e) => {
      if (e.target === cy) {
        onClearSelection();
      }
    });

    cyRef.current = cy;

    // ResizeObserver to handle container layout changes, tab switches, and window resizes
    let resizeTimer = null;
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.contentRect.width > 0 && entry.contentRect.height > 0) {
          clearTimeout(resizeTimer);
          resizeTimer = setTimeout(() => {
            if (cy && !cy.destroyed() && cy.elements().length > 0) {
              cy.resize();
              cy.fit(undefined, 60);
            }
          }, 80);
        }
      }
    });

    resizeObserver.observe(containerRef.current);

    return () => {
      clearTimeout(resizeTimer);
      resizeObserver.disconnect();
      cy.destroy();
      cyRef.current = null;
    };
  }, []);

  // 2. Update elements when graphData changes
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy || !graphData) return;

    cy.batch(() => {
      cy.elements().remove();
      
      if (graphData.nodes && graphData.nodes.length > 0) {
        cy.add(graphData.nodes);
      }
      if (graphData.edges && graphData.edges.length > 0) {
        cy.add(graphData.edges);
      }
    });

    if (graphData.nodes && graphData.nodes.length > 0) {
      setIsRendered(true);
      // Defer layout until container DOM measurement is ready
      requestAnimationFrame(() => {
        setTimeout(() => {
          if (cy && !cy.destroyed() && cy.elements().length > 0) {
            runLayout();
          }
        }, 50);
      });
    } else {
      setIsRendered(false);
    }
  }, [graphData, runLayout]);

  // 3. Re-run layout when layoutName changes
  useEffect(() => {
    runLayout(layoutName);
  }, [layoutName, runLayout]);

  // 4. Handle Filtering & Search
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.batch(() => {
      cy.elements().removeClass('is-dimmed search-match');

      const hasFilter = Boolean(filterType || filterHealth || searchQuery);

      if (hasFilter) {
        cy.nodes().forEach(node => {
          const data = node.data();
          const matchType = !filterType || data.service_type === filterType;
          const matchHealth = !filterHealth || data.health_status === filterHealth;
          const matchSearch = !searchQuery || 
            (data.name && data.name.toLowerCase().includes(searchQuery.toLowerCase())) || 
            (data.id && data.id.toLowerCase().includes(searchQuery.toLowerCase()));

          if (matchType && matchHealth && matchSearch) {
            if (searchQuery && matchSearch) {
              node.addClass('search-match');
            }
          } else {
            node.addClass('is-dimmed');
          }
        });

        // Dim edges connected to dimmed nodes
        cy.edges().forEach(edge => {
          const source = edge.source();
          const target = edge.target();
          if (source.hasClass('is-dimmed') || target.hasClass('is-dimmed')) {
            edge.addClass('is-dimmed');
          }
        });
      }
    });

    // If there is an exact search match, center on it
    if (searchQuery && cy) {
      const match = cy.nodes('.search-match').first();
      if (match && match.length > 0) {
        cy.animate({
          center: { eles: match },
          zoom: 1.2,
          duration: 350
        });
      }
    }
  }, [filterType, filterHealth, searchQuery]);

  // 5. Handle Selection Highlighting
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.batch(() => {
      cy.elements().removeClass('is-selected');

      if (selectedNodeId) {
        const node = cy.$id(selectedNodeId);
        if (node.length > 0) {
          node.addClass('is-selected');
        }
      }

      if (selectedEdgeId) {
        const edge = cy.$id(selectedEdgeId);
        if (edge.length > 0) {
          edge.addClass('is-selected');
        }
      }
    });
  }, [selectedNodeId, selectedEdgeId]);

  // 6. Handle Downstream Impact Highlighting
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.batch(() => {
      cy.elements().removeClass('is-impacted is-impact-source is-impact-path');

      if (impactData && impactData.service_id) {
        // Highlight root source
        const rootNode = cy.$id(impactData.service_id);
        if (rootNode.length > 0) {
          rootNode.addClass('is-impact-source');
        }

        // Highlight reachable downstream services
        const reachableIds = impactData.reachable_services?.map(s => s.id) || [];
        reachableIds.forEach(id => {
          const n = cy.$id(id);
          if (n.length > 0) {
            n.addClass('is-impacted');
          }
        });

        // Highlight impact edges in paths
        if (impactData.paths) {
          Object.values(impactData.paths).forEach(pathList => {
            for (let i = 0; i < pathList.length - 1; i++) {
              const u = pathList[i];
              const v = pathList[i + 1];
              const edgesBetween = cy.edges(`[source = "${u}"][target = "${v}"]`);
              edgesBetween.addClass('is-impact-path');
            }
          });
        }
      }
    });
  }, [impactData]);

  // Highlight Cycles if requested
  const handleHighlightCycle = (cycle) => {
    const cy = cyRef.current;
    if (!cy) return;

    setHighlightedCycle(cycle);

    cy.batch(() => {
      cy.elements().removeClass('cycle-member cycle-edge');
      for (let i = 0; i < cycle.length; i++) {
        const u = cycle[i];
        const v = cycle[(i + 1) % cycle.length];
        
        cy.$id(u).addClass('cycle-member');
        cy.edges(`[source = "${u}"][target = "${v}"]`).addClass('cycle-edge');
      }
    });
  };

  const handleClearCycleHighlight = () => {
    const cy = cyRef.current;
    if (!cy) return;
    setHighlightedCycle(null);
    cy.batch(() => {
      cy.elements().removeClass('cycle-member cycle-edge');
    });
  };

  // Zoom / Fit Controls
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
      cyRef.current.fit(undefined, 60);
    }
  };

  const handleCenter = () => {
    if (cyRef.current) {
      cyRef.current.center();
    }
  };

  const cycles = graphData?.cycles || [];
  const hasNodes = graphData?.nodes && graphData.nodes.length > 0;

  return (
    <div className="cytoscape-container">
      {/* Cytoscape Canvas */}
      <div id="cy" ref={containerRef}></div>

      {/* Loading / Empty State Indicator */}
      {!hasNodes && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '12px',
          color: '#94a3b8',
          zIndex: 5
        }}>
          <Loader2 size={32} className="animate-spin" color="#0ea5e9" />
          <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>
            Loading Cloud Digital Twin Topology...
          </span>
        </div>
      )}

      {/* Floating Canvas Controls */}
      <div className="graph-controls-overlay">
        <button className="graph-control-btn" onClick={handleZoomIn} title="Zoom In">
          <ZoomIn size={16} />
        </button>
        <button className="graph-control-btn" onClick={handleZoomOut} title="Zoom Out">
          <ZoomOut size={16} />
        </button>
        <button className="graph-control-btn" onClick={handleFit} title="Fit to Viewport">
          <Maximize2 size={16} />
        </button>
        <button className="graph-control-btn" onClick={handleCenter} title="Center Graph">
          <Crosshair size={16} />
        </button>
        <button className="graph-control-btn" onClick={() => runLayout(layoutName)} title="Re-run Layout">
          <Play size={16} />
        </button>
      </div>

      {/* Circular Dependency Warning Banner */}
      {cycles.length > 0 && (
        <div className="cycle-warning-banner">
          <AlertTriangle size={18} color="#f59e0b" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div className="cycle-warning-content">
            <div className="cycle-warning-title">
              Circular Dependency Detected ({cycles.length})
            </div>
            <p>
              Cycles may cause infinite failover loops or cascading deadlocks during outages.
            </p>
            <div style={{ marginTop: '6px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {cycles.map((c, idx) => (
                <button
                  key={idx}
                  className="btn btn-secondary"
                  style={{ fontSize: '0.7rem', padding: '2px 8px' }}
                  onClick={() => handleHighlightCycle(c)}
                >
                  Highlight Cycle #{idx + 1} ({c.length} nodes)
                </button>
              ))}
              {highlightedCycle && (
                <button
                  className="btn btn-secondary"
                  style={{ fontSize: '0.7rem', padding: '2px 8px' }}
                  onClick={handleClearCycleHighlight}
                >
                  Clear Highlight
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Downstream Blast Radius Indicator Banner */}
      {impactData && impactData.service_name && (
        <div className="impact-active-banner">
          <span style={{ color: '#94a3b8' }}>Blast Radius:</span>
          <strong>{impactData.service_name}</strong>
          <span className="impact-badge-count">
            {impactData.reachable_count} Downstream Dependents
          </span>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
            (Direct: {impactData.direct_dependents_count}, Transitive: {impactData.indirect_dependents_count})
          </span>
        </div>
      )}

      {/* Floating Canvas Legend */}
      <div className="graph-legend">
        <span className="legend-title">Topology Legend</span>
        <div className="legend-row">
          <div className="legend-item">
            <span className="legend-dot healthy"></span>
            <span>Healthy</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot warning"></span>
            <span>Warning</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot critical"></span>
            <span>Critical</span>
          </div>
        </div>
        <div className="legend-row" style={{ marginTop: '2px' }}>
          <div className="legend-item">
            <span className="legend-line sync"></span>
            <span>Sync HTTP</span>
          </div>
          <div className="legend-item">
            <span className="legend-line async"></span>
            <span>Async Queue</span>
          </div>
          <div className="legend-item">
            <span className="legend-line db"></span>
            <span>Database</span>
          </div>
        </div>
      </div>
    </div>
  );
}
