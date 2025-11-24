import React from 'react';
import { GitBranch, CheckCircle2, Clock, ArrowDownWideNarrow } from 'lucide-react';
import { GitHubBranch } from '../types';

interface BranchListProps {
  branches: GitHubBranch[];
  selectedBranch: GitHubBranch | null;
  onSelect: (branch: GitHubBranch) => void;
  isLoading: boolean;
}

export const BranchList: React.FC<BranchListProps> = ({ branches, selectedBranch, onSelect, isLoading }) => {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <p className="text-slate-400 text-sm">Fetching remote branches...</p>
      </div>
    );
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown date';
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 

    if (diffDays <= 1) return 'Today';
    if (diffDays <= 2) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    
    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 overflow-hidden flex flex-col h-full shadow-inner">
      <div className="p-4 bg-slate-800 border-b border-slate-700 shrink-0">
        <h3 className="text-slate-200 font-semibold flex items-center gap-2">
          <GitBranch size={18} />
          Available Branches
        </h3>
        <p className="text-slate-400 text-xs mt-1 flex items-center gap-1">
          <ArrowDownWideNarrow size={12} />
          Sorted by most recently updated
        </p>
      </div>
      
      <div className="overflow-y-auto flex-1 p-2 space-y-1">
        {branches.map((branch) => {
          const isSelected = selectedBranch?.name === branch.name;
          return (
            <button
              key={branch.name}
              onClick={() => onSelect(branch)}
              className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-200 flex items-center justify-between group
                ${isSelected 
                  ? 'bg-blue-600/10 border border-blue-500/50' 
                  : 'hover:bg-slate-700/50 border border-transparent'
                }
              `}
            >
              <div className="flex flex-col gap-1">
                <span className={`font-medium text-sm ${isSelected ? 'text-blue-400' : 'text-slate-200'}`}>
                  {branch.name}
                </span>
                <div className="flex items-center gap-3 text-xs text-slate-500 font-mono">
                  {branch.lastUpdated && (
                    <span className={`flex items-center gap-1 ${isSelected ? 'text-blue-300/70' : 'text-slate-500'}`}>
                      <Clock size={10} />
                      {formatDate(branch.lastUpdated)}
                    </span>
                  )}
                </div>
              </div>
              
              {isSelected && (
                <CheckCircle2 size={18} className="text-blue-400" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};