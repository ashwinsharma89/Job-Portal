import { useState, useEffect } from 'react';
import { RefreshCw, Sparkles } from 'lucide-react';

interface ScrapeState {
    isScraping: boolean;
    lastTriggered: number | null;
}

// Global Store
export const scrapeStore = {
    state: { isScraping: false, lastTriggered: null } as ScrapeState,
    listeners: [] as ((state: ScrapeState) => void)[],

    setScraping(isActive: boolean) {
        this.state = {
            isScraping: isActive,
            lastTriggered: isActive ? Date.now() : this.state.lastTriggered
        };
        this.listeners.forEach(l => l(this.state));

        // Auto-turn off after 30s (Simulated duration)
        if (isActive) {
            setTimeout(() => {
                this.setScraping(false);
            }, 30000);
        }
    },

    subscribe(listener: (state: ScrapeState) => void) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }
};

export function SearchStatus() {
    const [isScraping, setIsScraping] = useState(false);

    useEffect(() => {
        return scrapeStore.subscribe((state) => setIsScraping(state.isScraping));
    }, []);

    if (!isScraping) return null;

    return (
        <div className="fixed top-20 right-8 z-50 animate-in fade-in slide-in-from-right-4 duration-500">
            <div className="bg-indigo-600 text-white px-4 py-3 rounded-lg shadow-xl flex items-center gap-3 border border-indigo-400/30 backdrop-blur-sm">
                <div className="relative">
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    <Sparkles className="w-3 h-3 absolute -top-1 -right-1 text-yellow-300 animate-pulse" />
                </div>
                <div>
                    <div className="font-bold text-sm">AI Agent Active</div>
                    <div className="text-xs text-indigo-100">Searching specifically for you...</div>
                </div>
            </div>
        </div>
    );
}
