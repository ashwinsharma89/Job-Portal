import { Search, MapPin, ChevronDown, Check } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

interface SearchBarProps {
    onSearch: (query: string, locations: string[]) => void;
    className?: string;
}

export function SearchBar({ onSearch, className = '' }: SearchBarProps) {
    const [query, setQuery] = useState('');
    const [selectedLocations, setSelectedLocations] = useState<string[]>([]);
    const [isLocationOpen, setIsLocationOpen] = useState(false);
    const locationRef = useRef<HTMLDivElement>(null);

    const locationOptions = [
        'Remote',
        'Bangalore',
        'Delhi NCR',
        'Mumbai',
        'Hyderabad',
        'Pune',
        'Chennai',
        'Kolkata',
        'Dubai',
        'Abu Dhabi'
    ];

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (locationRef.current && !locationRef.current.contains(event.target as Node)) {
                setIsLocationOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const toggleLocation = (location: string) => {
        setSelectedLocations(prev =>
            prev.includes(location)
                ? prev.filter(l => l !== location)
                : [...prev, location]
        );
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSearch(query, selectedLocations);
    };

    const getLocationLabel = () => {
        if (selectedLocations.length === 0) return 'Anywhere (Global)';
        if (selectedLocations.length === 1) return selectedLocations[0];
        return `${selectedLocations.length} Locations`;
    };

    return (
        <form onSubmit={handleSubmit} className={`${className} group`}>
            <div className="glass-card bg-slate-500/5 p-1.5 flex flex-col md:flex-row gap-2 border-white/10 group-focus-within:border-blue-500/30 group-focus-within:shadow-[0_0_30px_rgba(59,130,246,0.15)]">
                {/* Search Input Area */}
                <div className="flex-[2] flex items-center gap-3 px-4 py-2 rounded-xl transition-all">
                    <Search className="w-5 h-5 text-dim group-focus-within:text-blue-400 flex-shrink-0 transition-colors" />
                    <input
                        type="text"
                        placeholder="Search jobs by title, skills, or AI Agent keywords..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        className="w-full h-10 outline-none text-main placeholder:text-dim/50 bg-transparent text-sm font-medium"
                    />
                </div>

                {/* Vertical Divider */}
                <div className="hidden md:block w-px bg-white/5 my-2"></div>

                {/* Multi-Select Location Area */}
                <div className="flex-1 relative" ref={locationRef}>
                    <button
                        type="button"
                        onClick={() => setIsLocationOpen(!isLocationOpen)}
                        className="w-full flex items-center justify-between gap-3 px-4 py-2 rounded-xl transition-all hover:bg-slate-500/5"
                    >
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                            <MapPin className="w-5 h-5 text-dim flex-shrink-0" />
                            <span className="text-sm font-semibold text-main truncate">
                                {getLocationLabel()}
                            </span>
                            {selectedLocations.length > 0 && (
                                <span className="w-5 h-5 bg-blue-600 text-white rounded-full text-[10px] flex items-center justify-center shadow-lg shadow-blue-500/20 flex-shrink-0">
                                    {selectedLocations.length}
                                </span>
                            )}
                        </div>
                        <ChevronDown className={`w-4 h-4 text-dim transition-transform ${isLocationOpen ? 'rotate-180' : ''}`} />
                    </button>

                    {isLocationOpen && (
                        <div className="absolute z-[9999] w-full mt-2 glass-card surface-main border border-slate-200 dark:border-white/10 shadow-2xl p-2 max-h-64 overflow-y-auto custom-scrollbar animate-in fade-in zoom-in-95">
                            <div className="space-y-1">
                                {locationOptions.map((location) => (
                                    <label
                                        key={location}
                                        className={`flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer transition-all group ${selectedLocations.includes(location)
                                            ? 'bg-blue-600/20 text-blue-600 dark:text-blue-100'
                                            : 'text-main hover:bg-slate-500/10 dark:hover:bg-slate-500/5'
                                            }`}
                                    >
                                        <span className="text-xs font-medium">{location}</span>
                                        <div
                                            className={`w-4 h-4 rounded border flex items-center justify-center transition-all ${selectedLocations.includes(location)
                                                    ? 'bg-blue-600 border-blue-600'
                                                    : 'border-slate-300 dark:border-white/10 group-hover:border-slate-400 dark:group-hover:border-white/30'
                                                }`}
                                        >
                                            {selectedLocations.includes(location) && <Check className="w-3 h-3 text-white" />}
                                        </div>
                                        <input
                                            type="checkbox"
                                            className="hidden"
                                            checked={selectedLocations.includes(location)}
                                            onChange={() => toggleLocation(location)}
                                        />
                                    </label>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Search Action Button */}
                <button
                    type="submit"
                    className="btn-modern-primary px-10 py-3 text-sm font-bold whitespace-nowrap !rounded-xl"
                >
                    Find Jobs
                </button>
            </div>
        </form>
    );
}
