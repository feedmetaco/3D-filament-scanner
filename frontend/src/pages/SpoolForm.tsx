import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { spoolsApi, productsApi } from '../services/api';
import type { Product } from '../services/api';

export default function SpoolForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [formData, setFormData] = useState({
    product_id: 0,
    purchase_date: '',
    vendor: '',
    price: '',
    storage_location: '',
    status: 'in_stock' as 'in_stock' | 'used_up' | 'donated' | 'lost',
  });

  useEffect(() => {
    loadProducts();
    if (id) {
      loadSpool();
    }
  }, [id]);

  const loadProducts = async () => {
    try {
      const { data } = await productsApi.list();
      setProducts(data);
    } catch (error) {
      console.error('Failed to load products:', error);
    }
  };

  const loadSpool = async () => {
    try {
      const { data } = await spoolsApi.get(parseInt(id!));
      setFormData({
        product_id: data.product_id,
        purchase_date: data.purchase_date || '',
        vendor: data.vendor || '',
        price: data.price?.toString() || '',
        storage_location: data.storage_location || '',
        status: data.status,
      });
    } catch (error) {
      console.error('Failed to load spool:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const submitData = {
        ...formData,
        price: formData.price ? parseFloat(formData.price) : undefined,
        purchase_date: formData.purchase_date || undefined,
        vendor: formData.vendor || undefined,
        storage_location: formData.storage_location || undefined,
      };

      if (id) {
        await spoolsApi.update(parseInt(id), submitData);
      } else {
        await spoolsApi.create(submitData);
      }
      navigate('/inventory');
    } catch (error) {
      console.error('Failed to save spool:', error);
      alert('Failed to save. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!id) return;

    if (window.confirm('Delete this spool? This cannot be undone.')) {
      try {
        await spoolsApi.delete(parseInt(id));
        navigate('/inventory');
      } catch (error) {
        console.error('Failed to delete spool:', error);
        alert('Failed to delete. Please try again.');
      }
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate(-1)}
          className="p-2 text-zinc-400 hover:text-zinc-100 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h2 className="text-2xl font-mono tracking-tight">
          {id ? 'Edit Spool' : 'New Spool'}
        </h2>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-4 bg-zinc-900/50 border border-zinc-800 rounded-lg p-4">
          <div>
            <label className="block text-xs font-mono text-zinc-400 mb-1.5">
              PRODUCT <span className="text-red-500">*</span>
            </label>
            <select
              required
              value={formData.product_id}
              onChange={(e) => setFormData({ ...formData, product_id: parseInt(e.target.value) })}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-cyan-500 transition-colors"
            >
              <option value={0}>Select product...</option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.brand} {product.material} {product.color_name} ({product.diameter_mm}mm)
                </option>
              ))}
            </select>
            {!id && products.length === 0 && (
              <p className="text-xs text-amber-500 font-mono mt-1.5">
                No products found. Create a product first.
              </p>
            )}
          </div>

          <div>
            <label className="block text-xs font-mono text-zinc-400 mb-1.5">PURCHASE DATE</label>
            <input
              type="date"
              value={formData.purchase_date}
              onChange={(e) => setFormData({ ...formData, purchase_date: e.target.value })}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-mono text-zinc-400 mb-1.5">VENDOR</label>
              <input
                type="text"
                value={formData.vendor}
                onChange={(e) => setFormData({ ...formData, vendor: e.target.value })}
                className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-cyan-500 transition-colors"
                placeholder="Amazon, AliExpress..."
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-zinc-400 mb-1.5">PRICE</label>
              <input
                type="number"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-cyan-500 transition-colors"
                placeholder="0.00"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono text-zinc-400 mb-1.5">STORAGE LOCATION</label>
            <input
              type="text"
              value={formData.storage_location}
              onChange={(e) => setFormData({ ...formData, storage_location: e.target.value })}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-cyan-500 transition-colors"
              placeholder="Shelf A, Drawer 2..."
            />
          </div>

          <div>
            <label className="block text-xs font-mono text-zinc-400 mb-1.5">
              STATUS <span className="text-red-500">*</span>
            </label>
            <select
              required
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-cyan-500 transition-colors"
            >
              <option value="in_stock">IN STOCK</option>
              <option value="used_up">USED UP</option>
              <option value="donated">DONATED</option>
              <option value="lost">LOST</option>
            </select>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          {id && (
            <button
              type="button"
              onClick={handleDelete}
              className="px-6 py-3 bg-red-900/20 hover:bg-red-900/30 border border-red-900 text-red-400 font-mono text-sm transition-colors"
            >
              DELETE
            </button>
          )}
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="flex-1 py-3 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-300 font-mono text-sm transition-colors"
          >
            CANCEL
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 py-3 bg-cyan-600 hover:bg-cyan-500 disabled:bg-cyan-900 disabled:text-cyan-700 text-white font-mono text-sm font-bold transition-all disabled:cursor-not-allowed"
          >
            {loading ? 'SAVING...' : 'SAVE'}
          </button>
        </div>
      </form>
    </div>
  );
}
