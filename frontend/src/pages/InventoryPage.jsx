import { useState, useEffect } from 'react';

function InventoryPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    brand: '',
    material: '',
    color_name: '',
  });

  useEffect(() => {
    fetchProducts();
  }, [filters]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.brand) params.append('brand', filters.brand);
      if (filters.material) params.append('material', filters.material);
      if (filters.color_name) params.append('color_name', filters.color_name);

      const response = await fetch(`http://localhost:8000/api/v1/products?${params}`);
      if (!response.ok) throw new Error('Failed to fetch products');

      const data = await response.json();
      setProducts(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value,
    });
  };

  const clearFilters = () => {
    setFilters({ brand: '', material: '', color_name: '' });
  };

  if (loading) return <div className="loading">Loading products...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="inventory-page">
      <h1>Filament Inventory</h1>

      <div className="filters">
        <input
          type="text"
          name="brand"
          placeholder="Filter by brand"
          value={filters.brand}
          onChange={handleFilterChange}
        />
        <input
          type="text"
          name="material"
          placeholder="Filter by material"
          value={filters.material}
          onChange={handleFilterChange}
        />
        <input
          type="text"
          name="color_name"
          placeholder="Filter by color"
          value={filters.color_name}
          onChange={handleFilterChange}
        />
        <button onClick={clearFilters}>Clear Filters</button>
      </div>

      <div className="products-grid">
        {products.length === 0 ? (
          <p>No products found</p>
        ) : (
          products.map((product) => (
            <div key={product.id} className="product-card">
              <h3>{product.brand} {product.line || ''}</h3>
              <p><strong>Material:</strong> {product.material}</p>
              <p><strong>Color:</strong> {product.color_name}</p>
              <p><strong>Diameter:</strong> {product.diameter_mm}mm</p>
              {product.notes && <p><small>{product.notes}</small></p>}
              <a href={`/products/${product.id}`}>View Details</a>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default InventoryPage;
