import { Link, Outlet } from 'react-router-dom';

function Layout() {
  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="container">
          <h1 className="app-title">3D Filament Scanner</h1>
          <nav className="app-nav">
            <Link to="/">Inventory</Link>
            <Link to="/spools">Spools</Link>
            <Link to="/spools/add">Add Spool</Link>
          </nav>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          <Outlet />
        </div>
      </main>

      <footer className="app-footer">
        <div className="container">
          <p>&copy; 2024 3D Filament Scanner - Local Inventory Management</p>
        </div>
      </footer>
    </div>
  );
}

export default Layout;
