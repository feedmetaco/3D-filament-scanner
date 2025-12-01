import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { productsApi } from '../services/api';

export default function ProductForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    brand: '',
    line: '',
    material: '',
    color_name: '',
    diameter_mm: 1.75,
    barcode: '',
    sku: '',
    notes: '',
  });

  useEffect(() => {
    if (id) {
      loadProduct();
    }
  }, [id]);

  const loadProduct = async () => {
    try {
      const { data } = await productsApi.get(parseInt(id!));
      setFormData({
        brand: data.brand,
        line: data.line || '',
        material: data.material,
        color_name: data.color_name,
        diameter_mm: data.diameter_mm,
        barcode: data.barcode || '',
        sku: data.sku || '',
        notes: data.notes || '',
      });
    } catch (error) {
      console.error('Failed to load product:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (id) {
        await productsApi.update(parseInt(id), formData);
      } else {
        await productsApi.create(formData);
      }
      navigate('/inventory');
    } catch (error) {
      console.error('Failed to save product:', error);
      alert('Failed to save. Please try again.');
    } finally {
      setLoading(false);
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
          {id ? 'Edit Product' : 'New Product'}
        </h2>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-4 bg-zinc-900/50 border border-zinc-800 rounded-lg p-4">
          <div>
            <label className="block text-xs font-mono text-zinc-400 mb-1.5">
              BRAND <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              value={formData.brand}
              onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-cyan-500 transition-colors"
              placeholder="Sunlu, eSUN, Bambu Lab..."
            />
          </div>

          <div>
            <label className="block text-xs font-mono text-zinc-400 mb-1.5">PRODUCT LINE</label>
            <input
              type="text"
              value={formData.line}
              onChange={(e) => setFormData({ ...formData, line: e.target.value })}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-cyan-500 transition-colors"
              placeholder="Silk, Matte, Basic..."
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-mono text-zinc-400 mb-1.5">
                MATERIAL <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.material}
                onChange={(e) => setFormData({ ...formData, material: e.target.value })}
                className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-cyan-500 transition-colors"
                placeholder="PLA, PETG, ABS..."
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-zinc-400 mb-1.5">
                DIAMETER <span className="text-red-500">*</span>
              </label>
              <select
                required
                value={formData.diameter_mm}
                onChange={(e) => setFormData({ ...formData, diameter_mm: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-cyan-500 transition-colors"
              >
                <option value="1.75">1.75mm</option>
                <option value="2.85">2.85mm</option>
                <option value="3.0">3.00mm</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono text-zinc-400 mb-1.5">
              COLOR <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              value={formData.color_name}
              onChange={(e) => setFormData({ ...formData, color_name: e.target.value })}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-cyan-500 transition-colors"
              placeholder="Red, Blue, Transparent..."
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-mono text-zinc-400 mb-1.5">BARCODE</label>
              <input
                type="text"
                value={formData.barcode}
                onChange={(e) => setFormData({ ...formData, barcode: e.target.value })}
                className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-cyan-500 transition-colors"
                placeholder="Optional"
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-zinc-400 mb-1.5">SKU</label>
              <input
                type="text"
                value={formData.sku}
                onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-cyan-500 transition-colors"
                placeholder="Optional"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono text-zinc-400 mb-1.5">NOTES</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-cyan-500 transition-colors resize-none"
              placeholder="Additional notes..."
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
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
