import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Scanner from './pages/Scanner';
import Inventory from './pages/Inventory';
import ProductForm from './pages/ProductForm';
import SpoolForm from './pages/SpoolForm';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/scanner" replace />} />
          <Route path="/scanner" element={<Scanner />} />
          <Route path="/inventory" element={<Inventory />} />
          <Route path="/products/new" element={<ProductForm />} />
          <Route path="/products/:id/edit" element={<ProductForm />} />
          <Route path="/spools/new" element={<SpoolForm />} />
          <Route path="/spools/:id/edit" element={<SpoolForm />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
