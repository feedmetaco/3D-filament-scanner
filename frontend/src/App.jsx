import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import InventoryPage from './pages/InventoryPage';
import SpoolListPage from './pages/SpoolListPage';
import ProductDetailPage from './pages/ProductDetailPage';
import AddSpoolPage from './pages/AddSpoolPage';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<InventoryPage />} />
          <Route path="inventory" element={<InventoryPage />} />
          <Route path="spools" element={<SpoolListPage />} />
          <Route path="spools/add" element={<AddSpoolPage />} />
          <Route path="products/:id" element={<ProductDetailPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
