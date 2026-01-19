// FilterSidebar component
import { Filter, X } from 'lucide-react';

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
        <div className={className}>
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                    <Filter className="w-5 h-5 text-blue-600" />
                    <h3 className="font-semibold text-slate-900">Refine Your Search</h3>
                </div>
                {hasActiveFilters && (
                    <button
                        onClick={() => {
                            filters.experience.forEach(exp => {
                                if (selectedFilters.experience.includes(exp)) {
                                    onFilterChange('experience', exp);
                                }
                            });
                            filters.ctc.forEach(ctc => {
                                if (selectedFilters.ctc.includes(ctc)) {
                                    onFilterChange('ctc', ctc);
                                }
                            });
                            filters.skills.forEach(skill => {
                                if (selectedFilters.skills.includes(skill)) {
                                    onFilterChange('skills', skill);
                                }
                            });
                            filters.jobPortals.forEach(portal => {
                                if (selectedFilters.jobPortals.includes(portal)) {
                                    onFilterChange('jobPortals', portal);
                                }
                            });
                        }}
                        className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
                    >
                        <X className="w-4 h-4" />
                        Clear All
                    </button>
                )}
            </div>

            {/* Horizontal Filter Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Country Toggle */}
                <div className="relative">
                    <select
                        className="w-full h-[42px] px-4 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:border-slate-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none appearance-none cursor-pointer"
                        value={selectedFilters.country}
                        onChange={(e) => onFilterChange('country', e.target.value)}
                    >
                        <option value="India">🇮🇳 India</option>
                        <option value="UAE">🇦🇪 UAE (Dubai/Gulf)</option>
                    </select>
                </div>

                <DropdownFilter
                    label="Experience Level"
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
                    label="Skills"
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
            </div>
        </div>
    );
}

// Reusable Dropdown Component
import { ChevronDown } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

function DropdownFilter({ label, options, selected, onChange }: {
    label: string,
    options: string[],
    selected: string[],
    onChange: (val: string) => void
}) {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Close on click outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`w-full flex items-center justify-between px-4 py-2.5 bg-white border rounded-xl text-sm font-medium transition-all duration-200 ${selected.length > 0
                    ? 'border-blue-500 text-blue-700 bg-blue-50/50 ring-1 ring-blue-500/20'
                    : 'border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-50'
                    }`}
            >
                <span className="truncate">
                    {selected.length > 0 ? `${label} (${selected.length})` : label}
                </span>
                <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <div className="absolute z-10 w-full mt-2 bg-white border border-slate-200 rounded-xl shadow-xl max-h-60 overflow-y-auto animate-in fade-in zoom-in-95 duration-100 p-2">
                    <div className="space-y-1">
                        {options.map((option) => (
                            <label
                                key={option}
                                className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer hover:bg-slate-50 transition-colors group"
                            >
                                <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${selected.includes(option)
                                    ? 'bg-blue-600 border-blue-600'
                                    : 'border-slate-300 group-hover:border-blue-400'
                                    }`}>
                                    {selected.includes(option) && (
                                        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                        </svg>
                                    )}
                                </div>
                                <input
                                    type="checkbox"
                                    className="hidden"
                                    checked={selected.includes(option)}
                                    onChange={() => onChange(option)}
                                />
                                <span className={`text-sm ${selected.includes(option) ? 'text-blue-700 font-medium' : 'text-slate-600'
                                    }`}>
                                    {option}
                                </span>
                            </label>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
