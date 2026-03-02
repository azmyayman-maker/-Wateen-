"use client";

import React, { useState, useEffect, useCallback } from "react";
import { 
  Check, 
  X, 
  FileText, 
  Building2, 
  Clock, 
  AlertCircle,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Loader2,
  ExternalLink
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface KYCDocument {
  id: string;
  document_type: string;
  document_type_display: string;
  status: string;
  version: number;
  uploaded_at: string;
  presigned_url: string | null;
  reviewer_notes: string | null;
}

interface AgencyKYC {
  id: string;
  manager_name: string;
  commercial_registry: string;
  moh_license_number: string;
  tax_id: string;
  status: string;
  created_at: string;
  kyc_documents: KYCDocument[];
}

interface ReviewActionProps {
  agencyId: string;
  onActionComplete: () => void;
}

const ReviewActions: React.FC<ReviewActionProps> = ({ agencyId, onActionComplete }) => {
  const [notes, setNotes] = useState("");
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [action, setAction] = useState<"APPROVE" | "REJECT" | null>(null);

  const handleAction = async () => {
    if (!action) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/admin/agencies/${agencyId}/review/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({
          action,
          notes: action === "REJECT" ? notes : "",
        }),
      });

      if (response.ok) {
        onActionComplete();
        setShowRejectModal(false);
        setNotes("");
      } else {
        const error = await response.json();
        alert(error.detail || "Action failed");
      }
    } catch (error) {
      console.error("Review action failed:", error);
      alert("Failed to process review action");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="flex gap-2">
        <button
          onClick={() => setAction("APPROVE")}
          disabled={isLoading}
          className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 hover:bg-emerald-500 hover:text-white transition-all text-xs font-bold uppercase tracking-wider disabled:opacity-50"
        >
          <Check className="w-4 h-4" />
          Approve
        </button>
        <button
          onClick={() => {
            setAction("REJECT");
            setShowRejectModal(true);
          }}
          disabled={isLoading}
          className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-rose-500/20 border border-rose-500/40 text-rose-400 hover:bg-rose-500 hover:text-white transition-all text-xs font-bold uppercase tracking-wider disabled:opacity-50"
        >
          <X className="w-4 h-4" />
          Reject
        </button>
      </div>

      <AnimatePresence>
        {showRejectModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 flex items-center justify-center z-50"
            onClick={() => setShowRejectModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-slate-900 border border-slate-700 rounded-xl p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-amber-500" />
                Reject Agency Application
              </h3>
              <p className="text-slate-400 text-sm mb-4">
                Please provide a reason for rejection. This will be visible to the agency admin.
              </p>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Enter rejection reason (required)..."
                className="w-full bg-slate-800 border border-slate-600 rounded-lg p-3 text-white placeholder-slate-500 focus:border-rose-500 focus:outline-none resize-none"
                rows={4}
              />
              <div className="flex gap-3 mt-4">
                <button
                  onClick={() => setShowRejectModal(false)}
                  className="flex-1 py-2 px-4 rounded-lg border border-slate-600 text-slate-300 hover:bg-slate-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAction}
                  disabled={!notes.trim() || isLoading}
                  className="flex-1 py-2 px-4 rounded-lg bg-rose-500 text-white font-bold hover:bg-rose-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <X className="w-4 h-4" />
                  )}
                  Confirm Reject
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export const KYCReviewList: React.FC = () => {
  const [agencies, setAgencies] = useState<AgencyKYC[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchQueue = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/v1/admin/kyc-queue/", {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch queue");
      }

      const data = await response.json();
      setAgencies(data.results || []);
    } catch (err) {
      setError("Failed to load KYC queue");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchQueue();
  }, [fetchQueue]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("ar-EG", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(date);
  };

  const getDocumentTypeIcon = (type: string) => {
    switch (type) {
      case "COMMERCIAL_REGISTRY":
        return "📋";
      case "MOH_LICENSE":
        return "🏥";
      case "TAX_ID":
        return "💰";
      default:
        return "📄";
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <AlertCircle className="w-12 h-12 text-rose-500" />
        <p className="text-slate-400">{error}</p>
        <button
          onClick={fetchQueue}
          className="flex items-center gap-2 px-4 py-2 bg-cyan-500/20 text-cyan-400 rounded-lg hover:bg-cyan-500/30 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full flex flex-col p-4 z-10 overflow-y-auto custom-scrollbar pr-2">
      <div className="flex items-center gap-2 mb-4">
        <Building2 className="w-4 h-4 text-cyan-500" />
        <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest">
          Agency KYC Queue
        </h3>
        <span className="ml-auto bg-cyan-500/20 text-cyan-400 text-[10px] font-mono font-bold px-2 py-0.5 rounded">
          {agencies.length} PENDING
        </span>
      </div>

      {agencies.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <Check className="w-12 h-12 text-emerald-500 mb-4" />
          <p className="text-slate-300 font-medium">All caught up!</p>
          <p className="text-slate-500 text-sm">No pending agency applications</p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          <AnimatePresence>
            {agencies.map((agency, idx) => (
              <motion.div
                key={agency.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: idx * 0.05 }}
                className="bg-slate-900/80 border border-slate-700/50 rounded-xl overflow-hidden hover:border-cyan-500/30 transition-colors"
              >
                {/* Main Row */}
                <div 
                  className="p-4 cursor-pointer"
                  onClick={() => setExpandedId(expandedId === agency.id ? null : agency.id)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <p className="text-white font-bold">{agency.manager_name}</p>
                      <p className="text-[11px] text-slate-500 font-mono mt-1">
                        CR: {agency.commercial_registry} • MoH: {agency.moh_license_number}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex items-center gap-1 text-slate-500 text-xs">
                        <Clock className="w-3 h-3" />
                        {formatDate(agency.created_at)}
                      </div>
                      {expandedId === agency.id ? (
                        <ChevronUp className="w-4 h-4 text-slate-500" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-slate-500" />
                      )}
                    </div>
                  </div>

                  {/* Document Count Badge */}
                  <div className="flex items-center gap-2 mt-3">
                    <span className="text-xs text-slate-400 bg-slate-800 px-2 py-1 rounded flex items-center gap-1">
                      <FileText className="w-3 h-3" />
                      {agency.kyc_documents.length} Documents
                    </span>
                    {agency.kyc_documents.every(doc => doc.status === "VERIFIED") && (
                      <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded">
                        All Verified
                      </span>
                    )}
                  </div>
                </div>

                {/* Expanded Details */}
                <AnimatePresence>
                  {expandedId === agency.id && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="border-t border-slate-700/50 bg-slate-950/50"
                    >
                      <div className="p-4 space-y-4">
                        {/* Documents List */}
                        <div>
                          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                            Submitted Documents
                          </h4>
                          <div className="grid gap-2">
                            {agency.kyc_documents.map((doc) => (
                              <div
                                key={doc.id}
                                className="flex items-center justify-between p-2 bg-slate-900 rounded-lg border border-slate-800"
                              >
                                <div className="flex items-center gap-2">
                                  <span className="text-lg">
                                    {getDocumentTypeIcon(doc.document_type)}
                                  </span>
                                  <div>
                                    <p className="text-sm text-white">
                                      {doc.document_type_display}
                                    </p>
                                    <p className="text-[10px] text-slate-500">
                                      v{doc.version} • {formatDate(doc.uploaded_at)}
                                    </p>
                                  </div>
                                </div>
                                {doc.presigned_url && (
                                  <a
                                    href={doc.presigned_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300"
                                    onClick={(e) => e.stopPropagation()}
                                  >
                                    View PDF
                                    <ExternalLink className="w-3 h-3" />
                                  </a>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Review Actions */}
                        <div>
                          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                            Review Action
                          </h4>
                          <ReviewActions
                            agencyId={agency.id}
                            onActionComplete={fetchQueue}
                          />
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(15, 23, 42, 0.2);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(6, 182, 212, 0.2);
          border-radius: 4px;
        }
        .custom-scrollbar:hover::-webkit-scrollbar-thumb {
          background: rgba(6, 182, 212, 0.5);
        }
      `}</style>
    </div>
  );
};
