import { useState, useEffect } from 'react';
import { type Job, fetchJobs } from './api';
import { JobCard } from './components/JobCard';
import { SearchBar } from './components/SearchBar';
import { FilterSidebar } from './components/FilterSidebar';
import { Briefcase, Sun, Moon } from 'lucide-react';
import { DebugConsole } from './components/DebugConsole';

import { SmartContext } from './components/SmartContext';

// Mock Config for Filters
const FILTER_OPTIONS = {
  experience: ['0-3 Years', '3-6 Years', '6-10 Years', '10-14 Years', '14+ Years'],
  ctc: ['0-10 LPA', '10-20 LPA', '20-30 LPA', '30-40 LPA', '40-50 LPA', '50+ LPA'],
  skills: ['Python', 'SQL', 'AI', 'Generative AI', 'Data Engineering', 'ETL', 'Media Analytics', 'Alteryx', 'Tableau', 'System Design', 'AWS'],
  jobPortals: ['LinkedIn', 'Naukri', 'Indeed', 'Shine', 'Hirist', 'iimjobs', 'Remotive', 'Freshersworld', 'Apna', 'Foundit', 'ZipRecruiter', 'Glassdoor']
};

function App() {
  console.log("App component rendering...");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true); // Assuming there's more if we get a full page
  const jobsPerPage = 40; // Display 40 jobs per page

  // Search State for pagination
  const [currentQuery, setCurrentQuery] = useState('');
  const [currentLocations, setCurrentLocations] = useState<string[]>([]);
  const [currentContextId, setCurrentContextId] = useState<string | undefined>(undefined);

  // Theme State
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('theme') as 'dark' | 'light') || 'dark';
  });

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  // Filter State
  const [selectedFilters, setSelectedFilters] = useState({
    experience: [] as string[],
    ctc: [] as string[],
    skills: [] as string[],
    jobPortals: [] as string[],
    country: 'India'
  });

  const handleSearch = async (query: string, locations: string[], filtersOverride?: typeof selectedFilters) => {
    setLoading(true);
    setError('');
    setCurrentPage(1); // Reset to first page on new search
    setCurrentQuery(query);
    setCurrentLocations(locations);  // Store locations in state

    // Auto-detect country from selected locations
    let targetCountry = filtersOverride?.country || selectedFilters.country;

    if (locations.some((loc: string) => ['Dubai', 'Abu Dhabi'].includes(loc))) {
      targetCountry = 'UAE';
    } else if (locations.length > 0 && locations.every((loc: string) => ['Bangalore', 'Delhi NCR', 'Mumbai', 'Hyderabad', 'Pune', 'Chennai', 'Kolkata'].includes(loc))) {
      targetCountry = 'India';
    }

    // Update filters state if country changed
    if (targetCountry !== selectedFilters.country) {
      setSelectedFilters(prev => ({ ...prev, country: targetCountry }));
    }

    try {
      const filtersWithLocations = { ...(filtersOverride || selectedFilters), locations, country: targetCountry };
      // Handle empty query - backend will default to "Job" and use vector search
      const data = await fetchJobs(query || "", filtersWithLocations, currentContextId, targetCountry, 1);
      setJobs(data);
      setHasMore(data.length > 0);
    } catch (err) {
      setError('Failed to fetch jobs. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (category: 'experience' | 'ctc' | 'skills' | 'jobPortals' | 'country', value: string) => {
    if (category === 'country') {
      setSelectedFilters(prev => ({ ...prev, country: value }));
      return;
    }
    setSelectedFilters(prev => {
      const current = prev[category] as string[]; // Cast for array types
      const newValues = current.includes(value)
        ? current.filter(item => item !== value)
        : [...current, value];
      return { ...prev, [category]: newValues };
    });
  };

  // Auto-search when resume is uploaded (zero-click job discovery)
  useEffect(() => {
    if (currentContextId && !currentQuery && jobs.length === 0) {
      // Resume uploaded but no search query - auto-search with intelligent default
      console.log("🚀 Auto-searching based on resume context...");
      handleSearch("", []);
    }
  }, [currentContextId]);

  // Auto-search when filters change (only if we already have a query or results)
  useEffect(() => {
    if (currentQuery || jobs.length > 0) {
      handleSearch(currentQuery, []);
    }
  }, [selectedFilters]);

  const paginate = async (pageNumber: number) => {
    setLoading(true);
    setCurrentPage(pageNumber);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    try {
      const filtersWithLocations = { ...selectedFilters, locations: [] }; // Empty locations for pagination
      const data = await fetchJobs(currentQuery, filtersWithLocations, currentContextId, selectedFilters.country, pageNumber);
      setJobs(data);
      setHasMore(data.length > 0);
    } catch (e) {
      setError('Failed to fetch page');
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`flex h-screen overflow-hidden ${theme === 'light' ? 'light-theme' : ''} bg-rgb(var(--color-bg-base)) mesh-gradient`}>
      {/* --- SIDEBAR --- */}
      <aside className="w-80 sidebar-gradient border-r border-white/5 flex flex-col hidden lg:flex">
        {/* Sidebar Header: Logo */}
        <div className="p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-violet-600 rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.3)]">
              <Briefcase className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-main tracking-tight">
                Job.ai <span className="text-blue-500 text-glow">Agent</span>
              </h1>
              <p className="text-[10px] text-dim font-medium uppercase tracking-widest">Autonomous Search</p>
            </div>
          </div>
        </div>

        {/* Sidebar Content: Filters & Resume */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-8 custom-scrollbar">
          {/* Resume Upload Section */}
          <section>
            <h3 className="text-xs font-bold text-dim uppercase tracking-wider mb-4">Deep Matching</h3>
            <SmartContext onContextChange={(id) => setCurrentContextId(id)} />
          </section>

          {/* Filters Section */}
          <section>
            <h3 className="text-xs font-bold text-dim uppercase tracking-wider mb-4">Refine Search</h3>
            <FilterSidebar
              filters={FILTER_OPTIONS}
              selectedFilters={selectedFilters}
              onFilterChange={handleFilterChange}
            />
          </section>
        </div>

        {/* Sidebar Footer */}
        <div className="p-6 border-t border-white/5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 px-3 py-2 bg-slate-500/5 rounded-xl border border-white/5 flex-1">
              <div className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 text-[10px] font-bold">
                BA
              </div>
              <div className="flex-1">
                <p className="text-[10px] font-bold text-main">Beta Access</p>
              </div>
            </div>

            {/* Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              className="ml-2 p-3 rounded-xl bg-white/5 border border-white/5 text-slate-400 hover:text-blue-400 hover:bg-white/10 transition-all shadow-lg"
              title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
            >
              {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </aside>

      {/* --- MAIN CONTENT --- */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {/* Top Header / Search Area */}
        <header className="p-6 border-b border-white/5 glass-card !rounded-none z-10">
          <div className="max-w-5xl mx-auto w-full">
            <SearchBar onSearch={handleSearch} className="w-full" />
          </div>
        </header>

        {/* Results Area */}
        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar relative">
          <div className="max-w-6xl mx-auto">
            {/* Stats Bar */}
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-2xl font-bold text-main mb-1">
                  {loading
                    ? (currentContextId && !currentQuery ? 'Analyzing Your Resume...' : 'Searching Jobs...')
                    : (currentQuery ? `Results for "${currentQuery}"` : 'Recommended Jobs')}
                </h2>
                <p className="text-sm text-dim">
                  {loading
                    ? (currentContextId && !currentQuery
                      ? 'AI is matching your profile with 5,000+ opportunities...'
                      : 'Scanning multiple job portals...')
                    : `Found ${jobs.length} high-match positions`}
                </p>
              </div>

              <div className="flex items-center gap-4">
                <select className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-xs font-medium text-slate-300 outline-none hover:bg-white/10 transition-colors">
                  <option>Most Relevant</option>
                  <option>Highest Match %</option>
                  <option>Relevance DESC</option>
                </select>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-8 glass-card border-red-500/20 bg-red-500/5 p-4 flex items-center gap-4 animate-in fade-in slide-in-from-top-4">
                <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center text-red-400 flex-shrink-0">⚠️</div>
                <p className="text-sm text-red-200">{error}</p>
              </div>
            )}

            {/* Job Grid / Loading State */}
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="h-48 glass-card bg-white/5"></div>
                ))}
              </div>
            ) : jobs.length > 0 ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {jobs.map(job => (
                    <JobCard key={job.id} job={job} contextId={currentContextId} />
                  ))}
                </div>

                {/* Pagination */}
                <div className="mt-12 flex items-center justify-center gap-4 pb-12">
                  <button
                    onClick={() => paginate(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="btn-modern-secondary px-6 !py-2 text-sm disabled:opacity-30 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <div className="glass-card px-4 py-2 bg-white/5 border-white/10 font-bold text-sm text-blue-400">
                    {currentPage}
                  </div>
                  <button
                    onClick={() => paginate(currentPage + 1)}
                    disabled={!hasMore || jobs.length < jobsPerPage}
                    className="btn-modern-secondary px-6 !py-2 text-sm disabled:opacity-30 disabled:cursor-not-allowed"
                  >
                    Next Page
                  </button>
                </div>
              </>
            ) : (
              /* Empty State */
              <div className="py-20 text-center glass-card border-dashed">
                <Briefcase className="w-12 h-12 text-dim/30 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-main">No results found</h3>
                <p className="text-dim text-sm max-w-sm mx-auto mt-2">
                  Try adjusting your filters or search query to broaden the results.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Floating Debug Button Area */}
        <div className="fixed bottom-6 right-6 z-50">
          <DebugConsole />
        </div>
      </main>
    </div>
  );
}

export default App;
