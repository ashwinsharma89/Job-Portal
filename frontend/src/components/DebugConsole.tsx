import { useState, useEffect } from 'react';
import { Activity, Database, Zap, Search, Clock, Server } from 'lucide-react';

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

// Global Store for Debug Metrics (Simple implementation without external lib)
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

    // if (!metrics) return null; // Logic removed to show "Ready" state

    const getStatusColor = (ms: number, threshold: number) =>
        ms < threshold ? 'text-green-500' : ms < threshold * 2 ? 'text-amber-500' : 'text-red-500';

    return (
        <div className={`fixed bottom-0 left-0 right-0 bg-slate-900 border-t border-slate-700 shadow-2xl transition-all duration-300 z-50 ${isOpen ? 'h-64' : 'h-10'}`}>
            {/* Header / Toggle */}
            <div
                className="h-10 flex items-center justify-between px-4 cursor-pointer hover:bg-slate-800"
                onClick={() => setIsOpen(!isOpen)}
            >
                <div className="flex items-center gap-4 text-xs font-mono">
                    <div className="flex items-center gap-1.5 text-blue-400">
                        <Activity className="w-3.5 h-3.5" />
                        <span className="font-bold">SYSTEM MONITOR</span>
                    </div>

                    {metrics ? (
                        <>
                            <span className="text-slate-400">|</span>
                            <span className={`${getStatusColor(metrics.timing.total, 500)} font-bold`}>
                                {metrics.timing.total}ms
                            </span>
                            <span className="text-slate-500">Latency</span>

                            <span className="text-slate-400">|</span>
                            <div className="flex items-center gap-1">
                                {metrics.meta.cache_hit ? (
                                    <span className="px-1.5 py-0.5 rounded bg-green-500/20 text-green-400 font-bold">CACHE HIT</span>
                                ) : (
                                    <span className="px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 font-bold">FRESH FETCH</span>
                                )}
                            </div>
                        </>
                    ) : (
                        <>
                            <span className="text-slate-400">|</span>
                            <span className="text-slate-500 italic">Ready for Search Request...</span>
                        </>
                    )}
                </div>

                <div className="text-slate-500 text-xs">
                    {isOpen ? 'Minimize' : 'Expand'}
                </div>
            </div>

            {/* Content Payload */}
            {isOpen && (
                <div className="flex h-full p-4 gap-6 overflow-x-auto pb-12 font-mono text-xs">
                    {!metrics ? (
                        <div className="flex w-full items-center justify-center text-slate-500 italic">
                            Run a search to see performance metrics.
                        </div>
                    ) : (
                        <>
                            {/* Timing Waterfall */}
                            <div className="flex-1 min-w-[300px] border-r border-slate-700 pr-6">
                                <h4 className="text-slate-400 mb-3 uppercase tracking-wider font-bold text-[10px] flex items-center gap-2">
                                    <Clock className="w-3 h-3" /> Latency Waterfall
                                </h4>
                                <div className="space-y-2">
                                    <MetricRow label="Vector Search" value={metrics.timing.vector_search} total={metrics.timing.total} color="bg-purple-500" icon={<Database className="w-3 h-3" />} />
                                    <MetricRow label="SQL Query" value={metrics.timing.sql_query} total={metrics.timing.total} color="bg-blue-500" icon={<Server className="w-3 h-3" />} />
                                    <MetricRow label="Reranking AI" value={metrics.timing.reranking} total={metrics.timing.total} color="bg-pink-500" icon={<Zap className="w-3 h-3" />} />
                                    <MetricRow label="Total Request" value={metrics.timing.total} total={metrics.timing.total} color="bg-slate-500" />
                                </div>
                            </div>

                            {/* Logic Stats */}
                            <div className="flex-1 min-w-[200px]">
                                <h4 className="text-slate-400 mb-3 uppercase tracking-wider font-bold text-[10px] flex items-center gap-2">
                                    <Search className="w-3 h-3" /> Search Logic
                                </h4>
                                <div className="grid grid-cols-2 gap-3">
                                    <StatBox label="Vector Hits" value={metrics.meta.vector_hits} sub="Semantic Matches" />
                                    <StatBox label="SQL Hits" value={metrics.meta.sql_hits} sub="Keyword Matches" />
                                    <StatBox label="Reranked" value={metrics.meta.reranked_count} sub="Top 50 Processed" />
                                    <StatBox label="Final Results" value={metrics.meta.final_results} sub="Returned to User" />
                                </div>
                            </div>
                        </>
                    )}
                </div>
            )}
        </div>
    );
}

function MetricRow({ label, value, total, color, icon }: any) {
    if (value === undefined) return null;
    const pct = Math.min((value / total) * 100, 100);
    return (
        <div className="group">
            <div className="flex justify-between mb-1 text-slate-300">
                <span className="flex items-center gap-2">{icon} {label}</span>
                <span className="font-bold">{value}ms</span>
            </div>
            <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className={`h-full ${color} rounded-full transition-all duration-500`} style={{ width: `${pct}%` }}></div>
            </div>
        </div>
    );
}

function StatBox({ label, value, sub }: any) {
    return (
        <div className="bg-slate-800 p-3 rounded-lg border border-slate-700">
            <div className="text-slate-400 text-[10px] uppercase mb-1">{label}</div>
            <div className="text-xl font-bold text-white mb-0.5">{value !== undefined ? value : '-'}</div>
            <div className="text-slate-500 text-[9px]">{sub}</div>
        </div>
    );
}
