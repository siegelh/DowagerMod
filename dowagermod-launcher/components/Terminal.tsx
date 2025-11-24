import React, { useEffect, useRef } from 'react';
import { LogEntry } from '../types';
import { Terminal as TerminalIcon } from 'lucide-react';

interface TerminalProps {
  logs: LogEntry[];
  title?: string;
}

export const Terminal: React.FC<TerminalProps> = ({ logs, title = "Installer Script Output" }) => {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="w-full bg-slate-950 rounded-lg border border-slate-800 overflow-hidden font-mono text-sm shadow-2xl">
      <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex items-center gap-2">
        <TerminalIcon size={14} className="text-slate-400" />
        <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">{title}</span>
        <div className="flex gap-1.5 ml-auto">
          <div className="w-2.5 h-2.5 rounded-full bg-slate-700"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-slate-700"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-slate-700"></div>
        </div>
      </div>
      <div className="p-4 h-64 overflow-y-auto space-y-1">
        {logs.length === 0 && (
          <div className="text-slate-600 italic">Waiting for process to start...</div>
        )}
        {logs.map((log, index) => (
          <div key={index} className="flex gap-3">
            <span className="text-slate-500 shrink-0">[{log.timestamp}]</span>
            <span className={`
              ${log.type === 'error' ? 'text-red-400' : ''}
              ${log.type === 'success' ? 'text-green-400' : ''}
              ${log.type === 'warning' ? 'text-yellow-400' : ''}
              ${log.type === 'info' ? 'text-slate-300' : ''}
            `}>
              {log.type === 'success' ? '➜ ' : ''}
              {log.message}
            </span>
          </div>
        ))}
        <div ref={endRef} />
      </div>
    </div>
  );
};