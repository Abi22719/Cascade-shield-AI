import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import MetricsSummaryBar from './components/MetricsSummaryBar';
import FilterBar from './components/FilterBar';
import GraphViewer from './components/GraphViewer';
import ServiceDrawer from './components/ServiceDrawer';
import ServiceModal from './components/ServiceModal';
import DependencyModal from './components/DependencyModal';
import ConfirmModal from './components/ConfirmModal';
import NotificationToast from './components/NotificationToast';
import AnomalyDashboard from './pages/AnomalyDashboard';
import { api } from './services/api';
import { anomalyApi } from './services/anomalyApi';
import './styles/App.css';

export default function App() {
  const [activeModule, setActiveModule] = useState('digital-twin'); // 'digital-twin' | 'anomaly-detection'
  const [unacknowledgedCount, setUnacknowledgedCount] = useState(0);

  const [graphData, setGraphData] = useState({ nodes: [], edges: [], summary: {}, cycles: [] });
  const [metricsSummary, setMetricsSummary] = useState(null);
  const [servicesList, setServicesList] = useState([]);
  
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterHealth, setFilterHealth] = useState('');
  const [currentLayout, setCurrentLayout] = useState('dagre-lr');

  const [impactData, setImpactData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Modals
  const [isAddServiceOpen, setIsAddServiceOpen] = useState(false);
  const [isAddDependencyOpen, setIsAddDependencyOpen] = useState(false);
  const [confirmConfig, setConfirmConfig] = useState(null);

  // Toasts
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info', title = null) => {
    const id = Date.now() + Math.random().toString(36).substring(2, 6);
    setToasts(prev => [...prev, { id, message, type, title }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4500);
  }, []);

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  // Fetch full digital twin state
  const loadDigitalTwin = useCallback(async () => {
    setLoading(true);
    try {
      const [graph, metrics, services, anomalySum] = await Promise.all([
        api.getGraph(),
        api.getMetricsSummary(),
        api.getServices(),
        anomalyApi.getSummary().catch(() => ({ unacknowledged_alerts: 0 }))
      ]);

      setGraphData(graph);
      setMetricsSummary(metrics);
      setServicesList(services);
      if (anomalySum && anomalySum.unacknowledged_alerts !== undefined) {
        setUnacknowledgedCount(anomalySum.unacknowledged_alerts);
      }

      // Refresh selectedNode if it is currently open
      if (selectedNode) {
        const updatedNode = graph.nodes?.find(n => n.data.id === selectedNode.id);
        if (updatedNode) {
          setSelectedNode(updatedNode.data);
        }
      }
    } catch (err) {
      console.error('Error loading digital twin state:', err);
      addToast(err.message || 'Failed to connect to backend digital twin engine', 'error', 'Connection Error');
    } finally {
      setLoading(false);
    }
  }, [selectedNode?.id, addToast]);

  useEffect(() => {
    loadDigitalTwin();
  }, [loadDigitalTwin]);

  // Selection handlers
  const handleSelectNode = (nodeData) => {
    setSelectedNode(nodeData);
    setSelectedEdge(null);
  };

  const handleSelectEdge = (edgeData) => {
    setSelectedEdge(edgeData);
    setSelectedNode(null);
  };

  const handleClearSelection = () => {
    setSelectedNode(null);
    setSelectedEdge(null);
  };

  // Service CRUD handlers
  const handleCreateService = async (serviceData) => {
    try {
      const created = await api.createService(serviceData);
      setIsAddServiceOpen(false);
      addToast(`Service '${created.name}' (${created.id}) created successfully.`, 'success', 'Service Created');
      await loadDigitalTwin();
      setSelectedNode(created);
    } catch (err) {
      addToast(err.message, 'error', 'Failed to Create Service');
    }
  };

  const handleUpdateService = async (serviceId, updateData) => {
    try {
      const updated = await api.updateService(serviceId, updateData);
      addToast(`Service '${updated.name}' telemetry and state updated. Health: ${updated.health_status}`, 'success', 'Telemetry Applied');
      await loadDigitalTwin();
      setSelectedNode(updated);
    } catch (err) {
      addToast(err.message, 'error', 'Update Failed');
    }
  };

  const handleDeleteServiceConfirm = (serviceId, serviceName) => {
    setConfirmConfig({
      title: `Delete Service: ${serviceName}`,
      message: `Are you sure you want to delete '${serviceName}' (${serviceId})? This will permanently remove the service node and all its incoming and outgoing dependency connections from the digital twin.`,
      confirmLabel: 'Delete Service',
      confirmVariant: 'danger',
      onConfirm: async () => {
        try {
          const res = await api.deleteService(serviceId);
          handleClearSelection();
          if (impactData?.service_id === serviceId) {
            setImpactData(null);
          }
          addToast(res.message, 'success', 'Service Deleted');
          await loadDigitalTwin();
        } catch (err) {
          addToast(err.message, 'error', 'Delete Failed');
        }
      }
    });
  };

  // Dependency CRUD handlers
  const handleCreateDependency = async (depData) => {
    try {
      const created = await api.createDependency(depData);
      setIsAddDependencyOpen(false);
      
      if (created.has_cycle) {
        addToast(
          created.cycle_warning || 'Circular dependency detected in graph!', 
          'warning', 
          'Circular Dependency Warning'
        );
      } else {
        addToast(
          `Connected ${created.source_service_id} -> ${created.target_service_id}`, 
          'success', 
          'Dependency Added'
        );
      }
      await loadDigitalTwin();
    } catch (err) {
      addToast(err.message, 'error', 'Failed to Add Dependency');
    }
  };

  const handleDeleteDependencyConfirm = (dependencyId) => {
    setConfirmConfig({
      title: 'Remove Dependency',
      message: `Are you sure you want to disconnect dependency '${dependencyId}'? Downstream routing and data flows will be unlinked.`,
      confirmLabel: 'Disconnect',
      confirmVariant: 'danger',
      onConfirm: async () => {
        try {
          const res = await api.deleteDependency(dependencyId);
          setSelectedEdge(null);
          addToast(res.message, 'success', 'Dependency Removed');
          await loadDigitalTwin();
        } catch (err) {
          addToast(err.message, 'error', 'Removal Failed');
        }
      }
    });
  };

  // Reset topology
  const handleResetTopologyConfirm = () => {
    setConfirmConfig({
      title: 'Reset Digital Twin Topology',
      message: 'This will reset the cloud infrastructure model back to the default 9 synthetic services and standard dependency architecture. Any custom modifications will be cleared.',
      confirmLabel: 'Reset Default Baseline',
      confirmVariant: 'warning',
      onConfirm: async () => {
        try {
          const res = await api.resetTopology();
          handleClearSelection();
          setImpactData(null);
          addToast(res.message, 'success', 'Topology Reset');
          await loadDigitalTwin();
        } catch (err) {
          addToast(err.message, 'error', 'Reset Failed');
        }
      }
    });
  };

  // Downstream Impact Analysis
  const handleAnalyzeImpact = async (serviceId) => {
    try {
      const impact = await api.getDownstreamImpact(serviceId);
      setImpactData(impact);
      addToast(
        `Blast radius analyzed: ${impact.reachable_count} downstream services reachable from ${impact.service_name || serviceId}.`,
        'info',
        'Blast Radius Analysis'
      );
    } catch (err) {
      addToast(err.message, 'error', 'Impact Analysis Failed');
    }
  };

  const handleClearImpact = () => {
    setImpactData(null);
  };

  // Filter matching count
  const matchingNodesCount = graphData.nodes?.filter(node => {
    const data = node.data;
    const matchType = !filterType || data.service_type === filterType;
    const matchHealth = !filterHealth || data.health_status === filterHealth;
    const matchSearch = !searchQuery || 
      data.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
      data.id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchType && matchHealth && matchSearch;
  }).length || 0;

  return (
    <div className="app-container">
      {/* Header */}
      <Navbar
        activeModule={activeModule}
        onSelectModule={setActiveModule}
        unacknowledgedAlertsCount={unacknowledgedCount}
        onAddService={() => setIsAddServiceOpen(true)}
        onAddDependency={() => setIsAddDependencyOpen(true)}
        onResetTopology={handleResetTopologyConfirm}
        onRefresh={loadDigitalTwin}
        loading={loading}
      />

      {/* MODULE 1 VIEW: DIGITAL TWIN & DEPENDENCY GRAPH */}
      {activeModule === 'digital-twin' && (
        <>
          {/* Metrics Summary Top Bar */}
          <MetricsSummaryBar summary={metricsSummary} />

          {/* Toolbar / Search / Filters */}
          <FilterBar
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            selectedType={filterType}
            onTypeChange={setFilterType}
            selectedHealth={filterHealth}
            onHealthChange={setFilterHealth}
            currentLayout={currentLayout}
            onLayoutChange={setCurrentLayout}
            impactActive={Boolean(impactData)}
            onClearImpact={handleClearImpact}
            matchingCount={matchingNodesCount}
            totalCount={graphData.nodes?.length || 0}
          />

          {/* Main Digital Twin Canvas + Side Drawer */}
          <main className="main-workspace">
            <GraphViewer
              graphData={graphData}
              selectedNodeId={selectedNode?.id}
              selectedEdgeId={selectedEdge?.id}
              onSelectNode={handleSelectNode}
              onSelectEdge={handleSelectEdge}
              onClearSelection={handleClearSelection}
              searchQuery={searchQuery}
              filterType={filterType}
              filterHealth={filterHealth}
              layoutName={currentLayout}
              impactData={impactData}
            />

            {/* Side Panel Inspector */}
            <ServiceDrawer
              selectedNode={selectedNode}
              selectedEdge={selectedEdge}
              onClose={handleClearSelection}
              onUpdateService={handleUpdateService}
              onDeleteService={handleDeleteServiceConfirm}
              onDeleteDependency={handleDeleteDependencyConfirm}
              onAnalyzeImpact={handleAnalyzeImpact}
              impactData={impactData}
              onClearImpact={handleClearImpact}
            />
          </main>
        </>
      )}

      {/* MODULE 2 VIEW: AI ANOMALY DETECTION & EARLY WARNING */}
      {activeModule === 'anomaly-detection' && (
        <AnomalyDashboard onAddToast={addToast} />
      )}

      {/* Modals */}
      <ServiceModal
        isOpen={isAddServiceOpen}
        onClose={() => setIsAddServiceOpen(false)}
        onSubmit={handleCreateService}
      />

      <DependencyModal
        isOpen={isAddDependencyOpen}
        onClose={() => setIsAddDependencyOpen(false)}
        onSubmit={handleCreateDependency}
        services={servicesList}
        existingEdges={graphData.edges || []}
      />

      <ConfirmModal
        isOpen={Boolean(confirmConfig)}
        title={confirmConfig?.title}
        message={confirmConfig?.message}
        confirmLabel={confirmConfig?.confirmLabel}
        confirmVariant={confirmConfig?.confirmVariant}
        onConfirm={confirmConfig?.onConfirm || (() => {})}
        onClose={() => setConfirmConfig(null)}
      />

      {/* Notifications */}
      <NotificationToast
        toasts={toasts}
        onDismiss={removeToast}
      />
    </div>
  );
}
