import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, Download, FileText, Calendar, Loader2 } from 'lucide-react';
import { format } from 'date-fns';
import { useAllSubmissions, downloadSubmissionFile } from '../hooks/useSubmissions';

export default function SubmissionsList() {
  const { data: submissions = [], isLoading, error } = useAllSubmissions();
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('newest');

  // Filtrare și Sortare
  const filteredSubmissions = submissions
    .filter(sub =>
      (sub.filepath || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (sub.id || '').toString().includes(searchTerm)
    )
    .sort((a, b) => {
      // AICI: am inlocuit submitted_at cu created_at
      const dateA = new Date(a.created_at || 0).getTime();
      const dateB = new Date(b.created_at || 0).getTime();
      return sortBy === 'newest' ? dateB - dateA : dateA - dateB;
    });

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-6 pt-24 flex justify-center">
        <Loader2 size={30} className="animate-spin text-cyan-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-6 pt-24 text-center text-rose-400">
        Nu am putut încărca lista de submisii. Asigură-te că endpoint-ul global există.
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 pt-24 pb-24">
      <div className="mb-8">
        <h1 className="font-display font-bold text-3xl text-white mb-2">Explore Submissions</h1>
        <p className="text-slate-400">View, search, and manage all assignment submissions across the platform.</p>
      </div>

      {/* Controale pentru Căutare și Sortare */}
      <div className="flex flex-col sm:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search by filename or ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-surface-3/30 border border-cyan-900/30 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-500/50"
          />
        </div>

        <div className="flex items-center gap-2 bg-surface-3/30 border border-cyan-900/30 rounded-xl px-3 py-1">
          <Filter size={16} className="text-slate-400" />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-transparent text-sm text-slate-200 focus:outline-none py-1.5"
          >
            <option value="newest" className="bg-slate-900">Newest first</option>
            <option value="oldest" className="bg-slate-900">Oldest first</option>
          </select>
        </div>
      </div>

      {/* Lista de Submisii */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSubmissions.length === 0 ? (
          <div className="col-span-full text-center py-12 text-slate-500">
            No submissions found matching your criteria.
          </div>
        ) : (
          filteredSubmissions.map((sub, index) => (
            <motion.div
              key={sub.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="glass p-5 rounded-2xl flex flex-col hover:border-cyan-500/30 transition-colors"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-400">
                    <FileText size={20} />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-white truncate max-w-[180px]">
                        {sub.filepath || `File #${sub.id}`}
                    </h3>
                    <p className="text-xs text-slate-500 font-mono">ID: {sub.id}</p>
                  </div>
                </div>
                <button
                  onClick={() => downloadSubmissionFile(sub.id, sub.filename)}
                  className="p-2 bg-surface-3/50 hover:bg-cyan-500/20 text-slate-400 hover:text-cyan-300 rounded-lg transition-colors"
                  title="Download File"
                >
                  <Download size={16} />
                </button>
              </div>

              <div className="mt-auto flex items-center justify-between text-xs text-slate-400 border-t border-cyan-900/30 pt-3">
                <span className="flex items-center gap-1.5">
                  <Calendar size={13} />
                  {/* AICI: am inlocuit submitted_at cu created_at */}
                  {sub.created_at ? format(new Date(sub.created_at), 'MMM d, yyyy') : 'N/A'}
                </span>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
}