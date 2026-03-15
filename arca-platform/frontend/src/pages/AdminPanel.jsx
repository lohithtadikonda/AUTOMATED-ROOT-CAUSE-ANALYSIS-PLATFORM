import React, { useState, useEffect } from 'react';
import { useUser } from '@clerk/clerk-react';
import { getStatistics, getAnomalies, getAlerts } from '../services/api';
import './AdminPanel.css';

function AdminPanel() {
  const { user } = useUser();
  const isAdmin = user?.publicMetadata?.role === 'admin';

  const [stats, setStats] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isAdmin) return;
    async function load() {
      try {
        setLoading(true);
        const [statsRes, anomaliesRes, alertsRes] = await Promise.all([
          getStatistics(),
          getAnomalies({ limit: 50 }),
          getAlerts(),
        ]);
        setStats(statsRes.data);
        setAnomalies(anomaliesRes.data.anomalies || []);
        setAlerts(alertsRes.data.alerts || []);
      } catch (err) {
        setError('Failed to load admin data');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [isAdmin]);

  if (!isAdmin) {
    return (
      <div className="admin-panel">
        <div className="access-denied">
          <div className="denied-icon">🚫</div>
          <h2>Access Denied</h2>
          <p>You need admin privileges to view this page.</p>
          <p className="muted-text">Contact your administrator to request access.</p>
        </div>
      </div>
    );
  }

  if (loading) return <div className="admin-panel"><div className="loading">Loading admin data...</div></div>;
  if (error) return <div className="admin-panel"><div className="error-message">{error}</div></div>;

  const criticalCount = anomalies.filter(a => a.severity === 'CRITICAL').length;
  const unacknowledgedAlerts = alerts.filter(a => !a.acknowledged).length;

  return (
    <div className="admin-panel">
      <div className="page-header-row">
        <div>
          <h1>Admin Panel</h1>
          <p className="muted-text">Logged in as <strong>{user.firstName || user.emailAddresses?.[0]?.emailAddress}</strong></p>
        </div>
        <span className="role-badge-large">Administrator</span>
      </div>

      {/* Platform Overview */}
      <h2 className="section-title">Platform Overview</h2>
      <div className="admin-stats-grid">
        <div className="admin-stat-card">
          <div className="stat-number">{stats?.total_anomalies ?? 0}</div>
          <div className="stat-label">Total Anomalies</div>
        </div>
        <div className="admin-stat-card critical">
          <div className="stat-number">{stats?.critical_anomalies ?? 0}</div>
          <div className="stat-label">Critical</div>
        </div>
        <div className="admin-stat-card high">
          <div className="stat-number">{stats?.high_anomalies ?? 0}</div>
          <div className="stat-label">High Severity</div>
        </div>
        <div className="admin-stat-card">
          <div className="stat-number">{stats?.total_rca_reports ?? 0}</div>
          <div className="stat-label">RCA Reports</div>
        </div>
        <div className="admin-stat-card warn">
          <div className="stat-number">{unacknowledgedAlerts}</div>
          <div className="stat-label">Unacknowledged Alerts</div>
        </div>
        <div className="admin-stat-card">
          <div className="stat-number">{stats?.total_alerts ?? 0}</div>
          <div className="stat-label">Total Alerts</div>
        </div>
      </div>

      {/* How to Set User as Admin */}
      <h2 className="section-title">User Role Management</h2>
      <div className="admin-info-card">
        <h3>How to promote a user to Admin</h3>
        <ol className="steps-list">
          <li>Go to <strong>Clerk Dashboard</strong> → Users</li>
          <li>Click on a user</li>
          <li>Scroll to <strong>Public Metadata</strong></li>
          <li>Set: <code className="code-inline">{"{ \"role\": \"admin\" }"}</code></li>
          <li>Save — the user immediately gains admin access</li>
        </ol>
        <p className="muted-text">Regular users have no <code className="code-inline">role</code> field (or <code className="code-inline">role: "user"</code>).</p>
      </div>

      {/* All Anomalies Table */}
      <h2 className="section-title">All Anomalies ({anomalies.length})</h2>
      <div className="admin-table-wrapper">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Metric</th>
              <th>Type</th>
              <th>Severity</th>
              <th>Value</th>
              <th>Threshold</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {anomalies.length === 0 ? (
              <tr><td colSpan="6" className="no-data">No anomalies found</td></tr>
            ) : (
              anomalies.map((a, i) => (
                <tr key={a._id || i}>
                  <td>{a.metric}</td>
                  <td>{a.anomaly_type || a.type || '-'}</td>
                  <td><span className={`severity-badge ${(a.severity || '').toLowerCase()}`}>{a.severity}</span></td>
                  <td>{typeof a.value === 'number' ? a.value.toFixed(2) : a.value}</td>
                  <td>{a.threshold ?? '-'}</td>
                  <td className="muted-text">{a.timestamp ? new Date(a.timestamp).toLocaleString() : '-'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* All Alerts Table */}
      <h2 className="section-title">All Alerts ({alerts.length})</h2>
      <div className="admin-table-wrapper">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Alert ID</th>
              <th>Severity</th>
              <th>Message</th>
              <th>Status</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {alerts.length === 0 ? (
              <tr><td colSpan="5" className="no-data">No alerts found</td></tr>
            ) : (
              alerts.map((a, i) => (
                <tr key={a._id || i}>
                  <td className="muted-text">{a.id || a._id?.slice(-6)}</td>
                  <td><span className={`severity-badge ${(a.severity || '').toLowerCase()}`}>{a.severity}</span></td>
                  <td>{a.message}</td>
                  <td>
                    {a.acknowledged
                      ? <span className="status-ok">Acknowledged</span>
                      : <span className="status-warn">Pending</span>}
                  </td>
                  <td className="muted-text">{a.timestamp ? new Date(a.timestamp).toLocaleString() : '-'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AdminPanel;
