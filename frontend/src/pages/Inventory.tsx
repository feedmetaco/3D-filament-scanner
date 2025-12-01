import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { spoolsApi, productsApi } from '../services/api';
import type { Spool, Product } from '../services/api';

type SpoolWithProduct = Spool & { product?: Product };

export default function Inventory() {
  const [spools, setSpools] = useState<SpoolWithProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [spoolsRes, productsRes] = await Promise.all([
        spoolsApi.list(),
        productsApi.list(),
      ]);

      // Map products to spools
      const spoolsWithProducts = spoolsRes.data.map(spool => ({
        ...spool,
        product: productsRes.data.find(p => p.id === spool.product_id),
      }));

      setSpools(spoolsWithProducts);
    } catch (error) {
      console.error('Failed to load inventory:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredSpools = filter === 'all'
    ? spools
    : spools.filter(s => s.status === filter);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'in_stock':
        return 'text-green-400 bg-green-500/10 border-green-500/30';
      case 'used_up':
        return 'text-zinc-500 bg-zinc-800/50 border-zinc-700';
      case 'donated':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/30';
      case 'lost':
        return 'text-red-400 bg-red-500/10 border-red-500/30';
      default:
        return 'text-zinc-400 bg-zinc-800 border-zinc-700';
    }
  };

  const getStatusLabel = (status: string) => {
    return status.toUpperCase().replace('_', ' ');
  };

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-6 flex items-center justify-center min-h-[50vh]">
        <div className="text-center space-y-3">
          <svg className="animate-spin h-8 w-8 text-cyan-500 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-sm font-mono text-zinc-500">LOADING INVENTORY...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-mono tracking-tight">Inventory</h2>
          <p className="text-sm text-zinc-500 font-mono mt-1">
            {filteredSpools.length} SPOOL{filteredSpools.length !== 1 ? 'S' : ''}
          </p>
        </div>
        <Link
          to="/spools/new"
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-sm transition-colors"
        >
          + ADD
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
        {[
          { label: 'ALL', value: 'all' },
          { label: 'IN STOCK', value: 'in_stock' },
          { label: 'USED UP', value: 'used_up' },
          { label: 'DONATED', value: 'donated' },
          { label: 'LOST', value: 'lost' },
        ].map(({ label, value }) => (
          <button
            key={value}
            onClick={() => setFilter(value)}
            className={`px-3 py-1.5 text-xs font-mono whitespace-nowrap transition-all ${
              filter === value
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                : 'bg-zinc-800 text-zinc-400 border border-zinc-700 hover:text-zinc-100'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Spool List */}
      {filteredSpools.length === 0 ? (
        <div className="text-center py-12 space-y-3">
          <div className="w-16 h-16 mx-auto border-2 border-dashed border-zinc-700 rounded-lg flex items-center justify-center">
            <svg className="w-8 h-8 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
          </div>
          <p className="text-sm font-mono text-zinc-500">NO SPOOLS FOUND</p>
          <Link
            to="/scanner"
            className="inline-block px-6 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-sm transition-colors"
          >
            SCAN FIRST SPOOL
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredSpools.map((spool) => (
            <Link
              key={spool.id}
              to={`/spools/${spool.id}/edit`}
              className="block bg-zinc-900/50 border border-zinc-800 hover:border-zinc-700 rounded-lg p-4 transition-all group"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 space-y-2">
                  {/* Product Info */}
                  <div>
                    <h3 className="font-mono text-sm text-zinc-100 group-hover:text-cyan-400 transition-colors">
                      {spool.product?.brand || 'Unknown'} {spool.product?.material || 'Material'}
                    </h3>
                    <p className="text-sm text-zinc-400 font-mono mt-0.5">
                      {spool.product?.color_name || 'Color'} · {spool.product?.diameter_mm || '1.75'}mm
                    </p>
                  </div>

                  {/* Meta */}
                  <div className="flex flex-wrap gap-2 text-xs font-mono text-zinc-500">
                    {spool.vendor && (
                      <span className="flex items-center gap-1">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                        </svg>
                        {spool.vendor}
                      </span>
                    )}
                    {spool.price && (
                      <span className="flex items-center gap-1">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        ${spool.price.toFixed(2)}
                      </span>
                    )}
                    {spool.storage_location && (
                      <span className="flex items-center gap-1">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        {spool.storage_location}
                      </span>
                    )}
                  </div>
                </div>

                {/* Status Badge */}
                <div className={`px-2 py-1 border rounded text-xs font-mono whitespace-nowrap ${getStatusColor(spool.status)}`}>
                  {getStatusLabel(spool.status)}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
