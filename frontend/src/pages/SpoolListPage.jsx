import { useState, useEffect } from 'react';

function SpoolListPage() {
  const [spools, setSpools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    vendor: '',
    storage_location: '',
  });

  useEffect(() => {
    fetchSpools();
  }, [filters]);

  const fetchSpools = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.vendor) params.append('vendor', filters.vendor);
      if (filters.storage_location) params.append('storage_location', filters.storage_location);

      const response = await fetch(`http://localhost:8000/api/v1/spools?${params}`);
      if (!response.ok) throw new Error('Failed to fetch spools');

      const data = await response.json();
      setSpools(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const markSpoolUsed = async (spoolId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/spools/${spoolId}/mark-used`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to mark spool as used');

      // Refresh the spools list
      fetchSpools();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value,
    });
  };

  const clearFilters = () => {
    setFilters({ status: '', vendor: '', storage_location: '' });
  };

  if (loading) return <div className="loading">Loading spools...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="spool-list-page">
      <h1>Spool List</h1>

      <div className="filters">
        <select name="status" value={filters.status} onChange={handleFilterChange}>
          <option value="">All Statuses</option>
          <option value="in_stock">In Stock</option>
          <option value="used_up">Used Up</option>
          <option value="donated">Donated</option>
          <option value="lost">Lost</option>
        </select>
        <input
          type="text"
          name="vendor"
          placeholder="Filter by vendor"
          value={filters.vendor}
          onChange={handleFilterChange}
        />
        <input
          type="text"
          name="storage_location"
          placeholder="Filter by location"
          value={filters.storage_location}
          onChange={handleFilterChange}
        />
        <button onClick={clearFilters}>Clear Filters</button>
      </div>

      <div className="spools-list">
        {spools.length === 0 ? (
          <p>No spools found</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Product ID</th>
                <th>Vendor</th>
                <th>Price</th>
                <th>Location</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {spools.map((spool) => (
                <tr key={spool.id}>
                  <td>{spool.id}</td>
                  <td><a href={`/products/${spool.product_id}`}>{spool.product_id}</a></td>
                  <td>{spool.vendor || '-'}</td>
                  <td>{spool.price ? `$${spool.price}` : '-'}</td>
                  <td>{spool.storage_location || '-'}</td>
                  <td><span className={`status-${spool.status}`}>{spool.status}</span></td>
                  <td>
                    {spool.status === 'in_stock' && (
                      <button onClick={() => markSpoolUsed(spool.id)}>
                        Mark Used
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default SpoolListPage;
