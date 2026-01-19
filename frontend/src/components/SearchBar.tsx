import { Search, MapPin } from 'lucide-react';
import { useState } from 'react';

interface SearchBarProps {
    onSearch: (query: string, location: string) => void;
    className?: string;
}

export function SearchBar({ onSearch, className = '' }: SearchBarProps) {
    const [query, setQuery] = useState('');
    const [location, setLocation] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSearch(query, location);
    };

    return (
        <form onSubmit={handleSubmit} className={`${className}`}>
            <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-2 flex flex-col md:flex-row gap-2">
                {/* Search Input */}
                <div className="flex-1 flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-50 transition-colors">
                    <Search className="w-5 h-5 text-slate-400 flex-shrink-0" />
                    <input
                        type="text"
                        placeholder="Search for AI Agents, Media Analytics, or Data Engineering..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        className="w-full outline-none text-slate-900 placeholder:text-slate-400 bg-transparent"
                    />
                </div>

                {/* Divider */}
                <div className="hidden md:block w-px bg-slate-200"></div>

                {/* Location Input */}
                <div className="flex-1 flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-50 transition-colors">
                    <MapPin className="w-5 h-5 text-slate-400 flex-shrink-0" />
                    <select
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                        className="w-full outline-none text-slate-900 bg-transparent appearance-none cursor-pointer"
                    >
                        <option value="">Any Location</option>
                        <option value="Remote">Remote</option>
                        <option value="Bangalore">Bangalore</option>
                        <option value="Delhi NCR">Delhi NCR</option>
                        <option value="Mumbai">Mumbai</option>
                        <option value="Hyderabad">Hyderabad</option>
                        <option value="Pune">Pune</option>
                        <option value="Chennai">Chennai</option>
                        <option value="UAE">🇦🇪 UAE</option>
                        <option value="Dubai">🇦🇪 Dubai</option>
                        <option value="Chennai">Chennai</option>
                        <option value="Kolkata">Kolkata</option>
                    </select>
                </div>

                {/* Search Button */}
                <button
                    type="submit"
                    className="btn-primary px-8 py-3 text-base font-semibold whitespace-nowrap transform transition-all duration-150 ease-out hover:scale-110 hover:shadow-2xl hover:shadow-blue-500/40 active:scale-90 active:shadow-none active:translate-y-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 border-none ring-offset-2 focus:ring-2 focus:ring-blue-500"
                    style={{ WebkitTapHighlightColor: 'transparent' }}
                >
                    Find Jobs
                </button>
            </div>
        </form>
    );
}
