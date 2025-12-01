import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_URL } from '../config';

function ProductDetailPage() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [spools, setSpools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProductAndSpools();
  }, [id]);

  const fetchProductAndSpools = async () => {
    try {
      setLoading(true);

      // Fetch product details
      const productResponse = await fetch(`${API_URL}/api/v1/products/${id}`);
      if (!productResponse.ok) throw new Error('Product not found');
      const productData = await productResponse.json();
      setProduct(productData);

      // Fetch spools for this product
      const spoolsResponse = await fetch(`${API_URL}/api/v1/spools?product_id=${id}`);
      if (!spoolsResponse.ok) throw new Error('Failed to fetch spools');
      const spoolsData = await spoolsResponse.json();
      setSpools(spoolsData);

      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!product) return <div>Product not found</div>;

  const inStockCount = spools.filter(s => s.status === 'in_stock').length;

  return (
    <div className="product-detail-page">
      <h1>Product Details</h1>

      <div className="product-info">
        <h2>{product.brand} {product.line || ''}</h2>
        <dl>
          <dt>Material:</dt>
          <dd>{product.material}</dd>

          <dt>Color:</dt>
          <dd>{product.color_name}</dd>

          <dt>Diameter:</dt>
          <dd>{product.diameter_mm}mm</dd>

          {product.barcode && (
            <>
              <dt>Barcode:</dt>
              <dd>{product.barcode}</dd>
            </>
          )}

          {product.sku && (
            <>
              <dt>SKU:</dt>
              <dd>{product.sku}</dd>
            </>
          )}

          {product.notes && (
            <>
              <dt>Notes:</dt>
              <dd>{product.notes}</dd>
            </>
          )}
        </dl>
      </div>

      <div className="spools-section">
        <h3>Spools ({inStockCount} in stock, {spools.length} total)</h3>

        {spools.length === 0 ? (
          <p>No spools for this product yet</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Vendor</th>
                <th>Price</th>
                <th>Purchase Date</th>
                <th>Location</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {spools.map((spool) => (
                <tr key={spool.id}>
                  <td>{spool.id}</td>
                  <td>{spool.vendor || '-'}</td>
                  <td>{spool.price ? `$${spool.price}` : '-'}</td>
                  <td>{spool.purchase_date || '-'}</td>
                  <td>{spool.storage_location || '-'}</td>
                  <td><span className={`status-${spool.status}`}>{spool.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="actions">
        <a href="/spools/add" className="button">Add New Spool</a>
        <a href="/inventory" className="button-secondary">Back to Inventory</a>
      </div>
    </div>
  );
}

export default ProductDetailPage;
