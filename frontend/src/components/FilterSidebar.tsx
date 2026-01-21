import { X, ChevronDown, Check } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

interface FilterSidebarProps {
    filters: {
        experience: string[];
        ctc: string[];
        skills: string[];
        jobPortals: string[];
    };
    selectedFilters: {
        experience: string[];
        ctc: string[];
        skills: string[];
        jobPortals: string[];
        country: string;
    };
    onFilterChange: (category: 'experience' | 'ctc' | 'skills' | 'jobPortals' | 'country', value: string) => void;
    className?: string;
}

export function FilterSidebar({ filters, selectedFilters, onFilterChange, className = '' }: FilterSidebarProps) {
    const hasActiveFilters =
        selectedFilters.experience.length > 0 ||
        selectedFilters.ctc.length > 0 ||
        selectedFilters.skills.length > 0 ||
        selectedFilters.jobPortals.length > 0;

    return (
        <div className={`space-y-4 ${className}`}>
            {/* Country Selector - Modern Pill Toggle */}
            <div className="bg-slate-500/5 p-1 rounded-xl border border-white/5 flex gap-1">
                <button
                    onClick={() => onFilterChange('country', 'India')}
                    className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${selectedFilters.country === 'India' ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'text-dim hover:text-main'}`}
                >
                    🇮🇳 India
                </button>
                <button
                    onClick={() => onFilterChange('country', 'UAE')}
                    className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${selectedFilters.country === 'UAE' ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'text-dim hover:text-main'}`}
                >
                    🇦🇪 UAE
                </button>
            </div>

            <DropdownFilter
                label="Experience"
                options={filters.experience}
                selected={selectedFilters.experience}
                onChange={(val) => onFilterChange('experience', val)}
            />
            <DropdownFilter
                label="Salary Range"
                options={filters.ctc}
                selected={selectedFilters.ctc}
                onChange={(val) => onFilterChange('ctc', val)}
            />
            <DropdownFilter
                label="Key Skills"
                options={filters.skills}
                selected={selectedFilters.skills}
                onChange={(val) => onFilterChange('skills', val)}
            />
            <DropdownFilter
                label="Job Portals"
                options={filters.jobPortals}
                selected={selectedFilters.jobPortals}
                onChange={(val) => onFilterChange('jobPortals', val)}
            />

            {hasActiveFilters && (
                <button
                    onClick={() => {
                        // Reset logic handled in parent usually, or we can send reset signal
                        // For now we just trigger changes back to empty
                        Object.keys(filters).forEach(cat => {
                            const category = cat as keyof typeof filters;
                            filters[category].forEach(opt => {
                                if (selectedFilters[category].includes(opt)) {
                                    onFilterChange(category, opt);
                                }
                            });
                        });
                    }}
                    className="w-full py-2.5 text-xs font-bold text-red-400 hover:text-red-300 hover:bg-red-500/5 rounded-lg border border-red-500/10 transition-all flex items-center justify-center gap-2"
                >
                    <X className="w-3.5 h-3.5" />
                    Reset All Filters
                </button>
            )}
        </div>
    );
}

function DropdownFilter({ label, options, selected, onChange }: {
    label: string,
    options: string[],
    selected: string[],
    onChange: (val: string) => void
}) {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const activeCount = selected.length;

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-300 ${isOpen || activeCount > 0
                    ? 'bg-blue-600/10 border-blue-500/30 text-blue-400'
                    : 'bg-slate-500/5 border-white/5 text-dim hover:bg-slate-500/10 hover:text-main'
                    } border`}
            >
                <div className="flex items-center gap-2">
                    {activeCount > 0 && (
                        <span className="w-5 h-5 bg-blue-600 text-white rounded-full text-[10px] flex items-center justify-center shadow-lg shadow-blue-500/20">
                            {activeCount}
                        </span>
                    )}
                    <span className="truncate">{label}</span>
                </div>
                <ChevronDown className={`w-4 h-4 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            {isOpen && (
                <div className="absolute z-20 w-full mt-2 glass-card bg-[#1a1c26]/95 border border-white/10 shadow-2xl p-2 max-h-64 overflow-y-auto custom-scrollbar animate-in fade-in zoom-in-95">
                    <div className="space-y-1">
                        {options.map((option) => (
                            <label
                                key={option}
                                className={`flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer transition-all group ${selected.includes(option) ? 'bg-blue-600/20 text-blue-100' : 'text-dim hover:bg-slate-500/5 hover:text-main'}`}
                            >
                                <span className="text-xs font-medium">{option}</span>
                                <div className={`w-4 h-4 rounded border flex items-center justify-center transition-all ${selected.includes(option)
                                    ? 'bg-blue-600 border-blue-600'
                                    : 'border-white/10 group-hover:border-white/30'
                                    }`}>
                                    {selected.includes(option) && <Check className="w-3 h-3 text-white" />}
                                </div>
                                <input
                                    type="checkbox"
                                    className="hidden"
                                    checked={selected.includes(option)}
                                    onChange={() => onChange(option)}
                                />
                            </label>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
