import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL } from '../config';

function AddSpoolPage() {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [formData, setFormData] = useState({
    product_id: '',
    vendor: '',
    price: '',
    purchase_date: '',
    storage_location: '',
    status: 'in_stock',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/products`);
      if (!response.ok) throw new Error('Failed to fetch products');
      const data = await response.json();
      setProducts(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleChange = (e) => {
    const value = e.target.type === 'number' ? parseFloat(e.target.value) : e.target.value;
    setFormData({
      ...formData,
      [e.target.name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Clean up empty fields
      const payload = {
        product_id: parseInt(formData.product_id),
        status: formData.status,
      };

      if (formData.vendor) payload.vendor = formData.vendor;
      if (formData.price) payload.price = parseFloat(formData.price);
      if (formData.purchase_date) payload.purchase_date = formData.purchase_date;
      if (formData.storage_location) payload.storage_location = formData.storage_location;

      const response = await fetch(`${API_URL}/api/v1/spools`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create spool');
      }

      const spool = await response.json();
      // Navigate to the product detail page
      navigate(`/products/${spool.product_id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="add-spool-page">
      <h1>Add New Spool</h1>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="product_id">Product *</label>
          <select
            id="product_id"
            name="product_id"
            value={formData.product_id}
            onChange={handleChange}
            required
          >
            <option value="">Select a product</option>
            {products.map((product) => (
              <option key={product.id} value={product.id}>
                {product.brand} {product.line || ''} - {product.material} - {product.color_name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="vendor">Vendor</label>
          <input
            type="text"
            id="vendor"
            name="vendor"
            value={formData.vendor}
            onChange={handleChange}
            placeholder="Amazon, Bambu, Micro Center, etc."
          />
        </div>

        <div className="form-group">
          <label htmlFor="price">Price</label>
          <input
            type="number"
            id="price"
            name="price"
            value={formData.price}
            onChange={handleChange}
            step="0.01"
            min="0"
            placeholder="25.99"
          />
        </div>

        <div className="form-group">
          <label htmlFor="purchase_date">Purchase Date</label>
          <input
            type="date"
            id="purchase_date"
            name="purchase_date"
            value={formData.purchase_date}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label htmlFor="storage_location">Storage Location</label>
          <input
            type="text"
            id="storage_location"
            name="storage_location"
            value={formData.storage_location}
            onChange={handleChange}
            placeholder="Shelf A2, Drybox 1, etc."
          />
        </div>

        <div className="form-group">
          <label htmlFor="status">Status *</label>
          <select
            id="status"
            name="status"
            value={formData.status}
            onChange={handleChange}
            required
          >
            <option value="in_stock">In Stock</option>
            <option value="used_up">Used Up</option>
            <option value="donated">Donated</option>
            <option value="lost">Lost</option>
          </select>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Spool'}
          </button>
          <button type="button" onClick={() => navigate('/spools')} className="button-secondary">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

export default AddSpoolPage;
