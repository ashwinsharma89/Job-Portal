import { useState, useEffect } from 'react';
import { Activity, Database, Zap, Server } from 'lucide-react';

interface DebugMetrics {
    timing: {
        total: number;
        vector_search?: number;
        sql_query?: number;
        reranking?: number;
        [key: string]: number | undefined;
    };
    meta: {
        vector_hits?: number;
        sql_hits?: number;
        reranked_count?: number;
        cache_hit?: boolean;
        final_results?: number;
        [key: string]: any;
    };
}

export const debugStore = {
    metrics: null as DebugMetrics | null,
    listeners: [] as ((metrics: DebugMetrics | null) => void)[],
    setMetrics(metrics: DebugMetrics) {
        this.metrics = metrics;
        this.listeners.forEach(l => l(metrics));
    },
    subscribe(listener: (metrics: DebugMetrics | null) => void) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }
};

export function DebugConsole() {
    const [metrics, setMetrics] = useState<DebugMetrics | null>(null);
    const [isOpen, setIsOpen] = useState(false);

    useEffect(() => {
        return debugStore.subscribe(setMetrics);
    }, []);

    const getStatusColor = (ms: number, threshold: number) =>
        ms < threshold ? 'text-emerald-400' : ms < threshold * 2 ? 'text-amber-400' : 'text-rose-400';

    return (
        <div className={`fixed bottom-6 right-6 flex flex-col items-end z-50 transition-all duration-300 ${isOpen ? 'w-96' : 'w-auto'}`}>
            {/* Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`flex items-center gap-2 px-4 py-3 rounded-2xl glass-card border-white/10 shadow-2xl hover:bg-white/10 transition-all ${isOpen ? 'mb-4 border-blue-500/30' : ''}`}
            >
                <Activity className={`w-4 h-4 ${metrics ? 'text-emerald-400 animate-pulse' : 'text-blue-400'}`} />
                <span className="text-[10px] font-bold text-main tracking-widest uppercase">System Stats</span>
                {metrics && !isOpen && (
                    <span className={`text-[10px] font-bold ${getStatusColor(metrics.timing.total, 500)} ml-2`}>
                        {metrics.timing.total}ms
                    </span>
                )}
            </button>

            {/* Expanded Console */}
            {isOpen && (
                <div className="w-full glass-card bg-[#12141c]/95 border-white/10 p-5 shadow-[0_20px_50px_rgba(0,0,0,0.5)] animate-in slide-in-from-bottom-5 duration-300 overflow-hidden">
                    <div className="flex items-center justify-between mb-6 border-b border-white/5 pb-3">
                        <h4 className="text-[10px] font-bold text-dim uppercase tracking-[0.2em] flex items-center gap-2">
                            <Server className="w-3 h-3" /> Execution Metrics
                        </h4>
                        {metrics?.meta.cache_hit && (
                            <span className="text-[9px] font-bold bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20">CACHE HIT</span>
                        )}
                    </div>

                    {!metrics ? (
                        <p className="text-[10px] text-dim italic text-center py-10">Run search to capture metrics...</p>
                    ) : (
                        <div className="space-y-5">
                            {/* Timing Waterfall */}
                            <div className="space-y-3">
                                <MetricRow label="Vector Index" value={metrics.timing.vector_search} total={metrics.timing.total} color="bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.3)]" icon={<Database className="w-3 h-3" />} />
                                <MetricRow label="Primary DB" value={metrics.timing.sql_query} total={metrics.timing.total} color="bg-violet-500 shadow-[0_0_10px_rgba(139,92,246,0.3)]" icon={<Server className="w-3 h-3" />} />
                                <MetricRow label="AI Rerank" value={metrics.timing.reranking} total={metrics.timing.total} color="bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.3)]" icon={<Zap className="w-3 h-3" />} />
                            </div>

                            {/* Divider */}
                            <div className="h-px bg-white/5"></div>

                            {/* Quick Stats Grid */}
                            <div className="grid grid-cols-2 gap-3">
                                <div className="bg-slate-500/5 p-3 rounded-xl border border-white/5">
                                    <p className="text-[9px] font-bold text-dim uppercase mb-1">Hits</p>
                                    <p className="text-lg font-bold text-main">{metrics.meta.vector_hits || 0}</p>
                                </div>
                                <div className="bg-slate-500/5 p-3 rounded-xl border border-white/5">
                                    <p className="text-[9px] font-bold text-dim uppercase mb-1">Latency</p>
                                    <p className={`text-lg font-bold ${getStatusColor(metrics.timing.total, 500)}`}>{metrics.timing.total}ms</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

function MetricRow({ label, value, total, color, icon }: any) {
    if (value === undefined) return null;
    const pct = Math.max(5, (value / total) * 100);
    return (
        <div>
            <div className="flex justify-between items-center mb-1.5">
                <span className="flex items-center gap-2 text-[10px] font-bold text-dim uppercase tracking-tighter">
                    {icon} {label}
                </span>
                <span className="text-[10px] font-bold text-main">{value}ms</span>
            </div>
            <div className="h-1 w-full bg-slate-500/10 rounded-full overflow-hidden">
                <div className={`h-full ${color} rounded-full transition-all duration-1000`} style={{ width: `${pct}%` }}></div>
            </div>
        </div>
    );
}
