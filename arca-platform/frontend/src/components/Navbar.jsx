import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { UserButton, useUser } from '@clerk/clerk-react';
import './Navbar.css';

function Navbar() {
  const location = useLocation();
  const { user } = useUser();
  const isAdmin = user?.publicMetadata?.role === 'admin';

  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <span className="brand-icon">🔍</span>
          <span className="brand-text">ARCA Platform</span>
        </Link>
        
        <ul className="navbar-menu">
          <li>
            <Link to="/" className={`nav-link ${isActive('/')}`}>
              Dashboard
            </Link>
          </li>
          <li>
            <Link to="/system-health" className={`nav-link ${isActive('/system-health')}`}>
              System Health
            </Link>
          </li>
          <li>
            <Link to="/anomalies" className={`nav-link ${isActive('/anomalies')}`}>
              Anomalies
            </Link>
          </li>
          <li>
            <Link to="/rca-reports" className={`nav-link ${isActive('/rca-reports')}`}>
              RCA Reports
            </Link>
          </li>
          <li>
            <Link to="/alerts" className={`nav-link ${isActive('/alerts')}`}>
              Alerts
            </Link>
          </li>
          {isAdmin && (
            <li>
              <Link to="/admin" className={`nav-link admin-link ${isActive('/admin')}`}>
                Admin Panel
              </Link>
            </li>
          )}
        </ul>

        <div className="navbar-user">
          {isAdmin && <span className="role-badge admin">Admin</span>}
          {user && !isAdmin && <span className="role-badge user">User</span>}
          <UserButton afterSignOutUrl="/" />
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
