import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import {
  HiCloudUpload,
  HiDocumentText,
  HiFolder,
  HiSearch,
  HiTrash,
  HiDownload,
  HiEye,
  HiClock,
  HiChip,
  HiSparkles,
  HiRefresh,
  HiPlus,
  HiX,
} from 'react-icons/hi';
import { FaFilePdf, FaFileWord, FaFileExcel, FaFileCsv } from 'react-icons/fa';
import { documentsAPI } from '../../services/api';

const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [query, setQuery] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [queryResults, setQueryResults] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [isSummarizing, setIsSummarizing] = useState(null); // document_id or 'all'
  const [summaryModal, setSummaryModal] = useState(null); // { filename, summary }
  const [isDownloading, setIsDownloading] = useState(null);
  const fileInputRef = useRef(null);

  // Fetch documents from backend on mount
  const fetchDocuments = useCallback(async () => {
    try {
      const response = await documentsAPI.list();
      const docs = (response.data.documents || []).map((d) => ({
        id: d.document_id,
        name: d.filename,
        type: d.filename.split('.').pop().toLowerCase(),
        size: d.size || 'N/A',
        date: d.uploaded_at || new Date().toISOString().split('T')[0],
        status: d.status || 'indexed',
        chunks: d.chunks_count || 0,
      }));
      setDocuments(docs);
    } catch (err) {
      // Fallback to demo data if backend unavailable
      console.warn('Could not fetch documents from backend, using demo data');
      setDocuments([
        { id: 'demo-1', name: 'Q4 Financial Report.pdf', type: 'pdf', size: '2.4 MB', date: '2024-01-18', status: 'indexed', chunks: 45 },
        { id: 'demo-2', name: 'Contract Template.docx', type: 'docx', size: '845 KB', date: '2024-01-15', status: 'indexed', chunks: 12 },
      ]);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const getFileIcon = (type) => {
    switch (type) {
      case 'pdf': return FaFilePdf;
      case 'docx': return FaFileWord;
      case 'xlsx': return FaFileExcel;
      case 'csv': return FaFileCsv;
      default: return HiDocumentText;
    }
  };

  const getFileColor = (type) => {
    switch (type) {
      case 'pdf': return 'text-red-400';
      case 'docx': return 'text-blue-400';
      case 'xlsx': return 'text-emerald-400';
      case 'csv': return 'text-amber-400';
      default: return 'text-slate-400';
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    await processFiles(files);
  };

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files);
    await processFiles(files);
  };

  const processFiles = async (files) => {
    for (const file of files) {
      const ext = file.name.split('.').pop().toLowerCase();
      if (!['pdf', 'docx', 'xlsx', 'csv', 'txt', 'md'].includes(ext)) {
        toast.error(`Unsupported file type: ${ext}`);
        continue;
      }

      setUploadProgress({ name: file.name, progress: 10 });

      try {
        const formData = new FormData();
        formData.append('file', file);

        setUploadProgress({ name: file.name, progress: 40 });
        const response = await documentsAPI.upload(formData);
        setUploadProgress({ name: file.name, progress: 80 });

        const doc = response.data;
        const newDoc = {
          id: doc.document_id,
          name: doc.filename || file.name,
          type: ext,
          size: `${(file.size / 1024 / 1024).toFixed(2)} MB`,
          date: new Date().toISOString().split('T')[0],
          status: doc.status || 'processing',
          chunks: doc.chunks_count || 0,
        };

        setDocuments(prev => [newDoc, ...prev]);
        setUploadProgress({ name: file.name, progress: 100 });
        toast.success(`${file.name} uploaded successfully!`);

        // Poll for processing completion
        setTimeout(async () => {
          await fetchDocuments();
        }, 5000);

      } catch (err) {
        console.error('Upload error:', err);
        toast.error(`Failed to upload ${file.name}: ${err.response?.data?.detail || err.message}`);
      } finally {
        setUploadProgress(null);
      }
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) {
      toast.error('Please enter a query');
      return;
    }

    setIsQuerying(true);
    try {
      const response = await documentsAPI.query(query, 5);
      const results = response.data;
      
      if (results.sources && results.sources.length > 0) {
        setQueryResults(results.sources.map((s, i) => ({
          document: s.filename || `Source ${i + 1}`,
          content: results.answer || 'No answer generated',
          relevance: s.relevance || 0.8,
          page: null,
        })));
      } else if (results.answer) {
        setQueryResults([{
          document: 'AI Response',
          content: results.answer,
          relevance: 1.0,
          page: null,
        }]);
      } else {
        setQueryResults([{
          document: 'No Results',
          content: 'No relevant information found in your documents.',
          relevance: 0,
          page: null,
        }]);
      }
      toast.success('Query completed');
    } catch (err) {
      console.error('Query error:', err);
      const detail = err.response?.data?.detail;
      const msg = Array.isArray(detail) ? detail.map(d => d.msg).join(', ') : (detail || err.message);
      toast.error('Query failed: ' + msg);
    } finally {
      setIsQuerying(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await documentsAPI.delete(id);
      setDocuments(prev => prev.filter(d => d.id !== id));
      toast.success('Document deleted');
    } catch (err) {
      console.error('Delete error:', err);
      // Remove from UI anyway (demo mode)
      setDocuments(prev => prev.filter(d => d.id !== id));
      toast.success('Document removed');
    }
  };

  const handleSummarize = async (documentId, filename) => {
    setIsSummarizing(documentId);
    try {
      const response = await documentsAPI.summarize(documentId, false);
      const summaries = response.data.summaries || [];
      if (summaries.length > 0) {
        setSummaryModal({
          filename: summaries[0].filename || filename,
          summary: summaries[0].summary,
          documentId: documentId,
          wordCount: summaries[0].word_count,
          pages: summaries[0].pages,
        });
        toast.success('Summary generated!');
      } else {
        toast.error('No summary generated');
      }
    } catch (err) {
      console.error('Summarize error:', err);
      toast.error('Summarization failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsSummarizing(null);
    }
  };

  const handleSummarizeAll = async () => {
    setIsSummarizing('all');
    try {
      const response = await documentsAPI.summarize(null, true);
      const summaries = response.data.summaries || [];
      if (summaries.length > 0) {
        const combinedSummary = summaries.map(s =>
          `📄 ${s.filename}\n${'─'.repeat(40)}\n${s.summary}`
        ).join('\n\n');
        setSummaryModal({
          filename: `All Documents (${summaries.length})`,
          summary: combinedSummary,
          documentId: 'all',
          wordCount: summaries.reduce((sum, s) => sum + (s.word_count || 0), 0),
        });
        toast.success(`Summarized ${summaries.length} documents!`);
      } else {
        toast.error('No documents to summarize');
      }
    } catch (err) {
      console.error('Summarize all error:', err);
      toast.error('Summarization failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsSummarizing(null);
    }
  };

  const handleDownloadSummary = async (documentId, filename) => {
    setIsDownloading(documentId);
    try {
      let response;
      if (documentId === 'all') {
        response = await documentsAPI.downloadAllSummaries();
      } else {
        response = await documentsAPI.downloadSummary(documentId);
      }
      
      // Create download link
      const blob = new Blob([response.data], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = documentId === 'all'
        ? 'all_documents_summary.txt'
        : `summary_${filename || documentId}.txt`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
      toast.success('Summary downloaded!');
    } catch (err) {
      console.error('Download error:', err);
      toast.error('Download failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsDownloading(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Documents</h1>
          <p className="text-slate-400">Upload and query your documents with AI-powered retrieval</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleSummarizeAll}
            disabled={isSummarizing === 'all' || documents.length === 0}
            className="btn-ghost flex items-center gap-2 border border-slate-700 disabled:opacity-50"
          >
            {isSummarizing === 'all' ? (
              <>
                <span className="w-5 h-5 border-2 border-primary-400 border-t-transparent rounded-full animate-spin" />
                Summarizing...
              </>
            ) : (
              <>
                <HiSparkles className="w-5 h-5" />
                Summarize All
              </>
            )}
          </button>
          <button
            onClick={() => {
              if (documents.length > 0 && documents[0].id !== 'all') {
                handleDownloadSummary('all', 'all_documents');
              }
            }}
            disabled={isDownloading || documents.length === 0}
            className="btn-ghost flex items-center gap-2 border border-slate-700 disabled:opacity-50"
          >
            <HiDownload className="w-5 h-5" />
            Download All Summaries
          </button>
          <button
            onClick={fetchDocuments}
            className="btn-ghost flex items-center gap-2 border border-slate-700"
          >
            <HiRefresh className="w-5 h-5" />
            Refresh
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="btn-primary flex items-center gap-2"
          >
            <HiPlus className="w-5 h-5" />
            Upload
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.docx,.xlsx,.csv,.txt"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
              <HiDocumentText className="w-5 h-5 text-primary-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{documents.length}</p>
              <p className="text-sm text-slate-400">Documents</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-secondary-500/20 flex items-center justify-center">
              <HiChip className="w-5 h-5 text-secondary-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">
                {documents.reduce((sum, d) => sum + d.chunks, 0)}
              </p>
              <p className="text-sm text-slate-400">Total Chunks</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
              <HiSparkles className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">
                {documents.filter(d => d.status === 'indexed').length}
              </p>
              <p className="text-sm text-slate-400">Indexed</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
              <HiSearch className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">142</p>
              <p className="text-sm text-slate-400">Queries Today</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Upload Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`card border-2 border-dashed cursor-pointer transition-all ${
          isDragging
            ? 'border-primary-500 bg-primary-500/10'
            : 'border-slate-700 hover:border-slate-600'
        }`}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="flex flex-col items-center justify-center py-8">
          <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 ${
            isDragging ? 'bg-primary-500/20' : 'bg-slate-800'
          }`}>
            <HiCloudUpload className={`w-8 h-8 ${isDragging ? 'text-primary-400' : 'text-slate-400'}`} />
          </div>
          <p className="text-lg font-medium text-white mb-1">
            {isDragging ? 'Drop files here' : 'Drag and drop files'}
          </p>
          <p className="text-slate-400 text-sm mb-4">or click to browse</p>
          <div className="flex flex-wrap justify-center gap-2">
            {['PDF', 'DOCX', 'XLSX', 'CSV', 'TXT'].map((format) => (
              <span key={format} className="text-xs bg-slate-800 text-slate-400 px-2 py-1 rounded">
                {format}
              </span>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Upload Progress */}
      {uploadProgress && (
        <div className="card">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
              <HiDocumentText className="w-5 h-5 text-primary-400 animate-pulse" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-white mb-1">{uploadProgress.name}</p>
              <div className="w-full bg-slate-800 rounded-full h-2">
                <div
                  className="bg-primary-500 h-2 rounded-full transition-all"
                  style={{ width: `${uploadProgress.progress}%` }}
                />
              </div>
            </div>
            <span className="text-slate-400">{uploadProgress.progress}%</span>
          </div>
        </div>
      )}

      {/* Query Section */}
      <div className="card bg-gradient-to-br from-slate-800/80 to-slate-900/80">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <HiSparkles className="w-5 h-5 text-primary-400" />
          AI Document Query
        </h3>
        <div className="flex gap-4 mb-4">
          <div className="flex-1 relative">
            <HiSearch className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask anything about your documents..."
              className="input pl-12"
              onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
            />
          </div>
          <button
            onClick={handleQuery}
            disabled={isQuerying}
            className="btn-primary flex items-center gap-2 px-6"
          >
            {isQuerying ? (
              <>
                <span className="spinner-small" />
                Searching...
              </>
            ) : (
              <>
                <HiSearch className="w-5 h-5" />
                Query
              </>
            )}
          </button>
        </div>

        {/* Query Results */}
        {queryResults.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium text-slate-400">Results</h4>
              <button
                onClick={() => setQueryResults([])}
                className="text-sm text-slate-500 hover:text-slate-300"
              >
                Clear
              </button>
            </div>
            {queryResults.map((result, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 rounded-xl bg-slate-800/50 hover:bg-slate-800 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <HiDocumentText className="w-5 h-5 text-primary-400" />
                    <span className="font-medium text-white">{result.document}</span>
                    {result.page && (
                      <span className="text-xs text-slate-500">Page {result.page}</span>
                    )}
                  </div>
                  <span className={`text-sm font-medium ${
                    result.relevance >= 0.9 ? 'text-emerald-400' : result.relevance >= 0.8 ? 'text-amber-400' : 'text-slate-400'
                  }`}>
                    {(result.relevance * 100).toFixed(0)}% match
                  </span>
                </div>
                <p className="text-slate-300 text-sm">{result.content}</p>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Documents List */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">All Documents</h3>
          <div className="relative">
            <HiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search documents..."
              className="input pl-9 py-2 text-sm w-48"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Name</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Size</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Chunks</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Status</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Date</th>
                <th className="text-right py-3 px-4 text-slate-400 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => {
                const FileIcon = getFileIcon(doc.type);
                const fileColor = getFileColor(doc.type);

                return (
                  <tr key={doc.id} className="border-b border-slate-800 hover:bg-slate-800/50">
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-3">
                        <FileIcon className={`w-6 h-6 ${fileColor}`} />
                        <span className="text-white font-medium">{doc.name}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-slate-400">{doc.size}</td>
                    <td className="py-4 px-4 text-slate-400">{doc.chunks}</td>
                    <td className="py-4 px-4">
                      <span className={`badge ${
                        doc.status === 'indexed'
                          ? 'bg-emerald-500/20 text-emerald-400'
                          : 'bg-amber-500/20 text-amber-400'
                      }`}>
                        {doc.status === 'indexed' ? 'Indexed' : 'Processing...'}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-slate-400">{doc.date}</td>
                    <td className="py-4 px-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleSummarize(doc.id, doc.name)}
                          disabled={isSummarizing === doc.id}
                          title="Summarize with AI"
                          className="p-2 rounded-lg hover:bg-primary-500/20 text-slate-400 hover:text-primary-400 transition-colors disabled:opacity-50"
                        >
                          {isSummarizing === doc.id ? (
                            <span className="w-5 h-5 block border-2 border-primary-400 border-t-transparent rounded-full animate-spin" />
                          ) : (
                            <HiSparkles className="w-5 h-5" />
                          )}
                        </button>
                        <button
                          onClick={() => handleDownloadSummary(doc.id, doc.name)}
                          disabled={isDownloading === doc.id}
                          title="Download Summary"
                          className="p-2 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition-colors disabled:opacity-50"
                        >
                          {isDownloading === doc.id ? (
                            <span className="w-5 h-5 block border-2 border-white border-t-transparent rounded-full animate-spin" />
                          ) : (
                            <HiDownload className="w-5 h-5" />
                          )}
                        </button>
                        <button
                          onClick={() => handleDelete(doc.id)}
                          className="p-2 rounded-lg hover:bg-red-500/20 text-slate-400 hover:text-red-400 transition-colors"
                        >
                          <HiTrash className="w-5 h-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Summary Modal */}
      {summaryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-3xl max-h-[80vh] flex flex-col"
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-slate-700">
              <div>
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <HiSparkles className="w-5 h-5 text-primary-400" />
                  AI Summary
                </h3>
                <p className="text-sm text-slate-400 mt-1">{summaryModal.filename}</p>
                {summaryModal.wordCount && (
                  <p className="text-xs text-slate-500 mt-0.5">
                    {summaryModal.wordCount.toLocaleString()} words
                    {summaryModal.pages ? ` • ${summaryModal.pages} pages` : ''}
                  </p>
                )}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleDownloadSummary(summaryModal.documentId, summaryModal.filename)}
                  disabled={isDownloading}
                  className="btn-primary flex items-center gap-2 text-sm py-2 px-4"
                >
                  <HiDownload className="w-4 h-4" />
                  Download
                </button>
                <button
                  onClick={() => setSummaryModal(null)}
                  className="p-2 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
                >
                  <HiX className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="prose prose-invert prose-sm max-w-none">
                <pre className="whitespace-pre-wrap font-sans text-slate-300 text-sm leading-relaxed bg-transparent p-0">
                  {summaryModal.summary}
                </pre>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default Documents;
