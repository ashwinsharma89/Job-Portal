import { useState, useEffect } from 'react';
import { type Job, fetchJobs } from './api';
import { JobCard } from './components/JobCard';
import { SearchBar } from './components/SearchBar';
import { FilterSidebar } from './components/FilterSidebar';
import { Briefcase } from 'lucide-react';
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
  const [currentLocation, setCurrentLocation] = useState('');
  const [currentContextId, setCurrentContextId] = useState<string | undefined>(undefined);

  // Filter State
  const [selectedFilters, setSelectedFilters] = useState({
    experience: ['10-14 Years'],
    ctc: [] as string[],
    skills: [] as string[],
    jobPortals: [] as string[],
    country: 'India'
  });

  const handleSearch = async (query: string, location: string, filtersOverride?: typeof selectedFilters) => {
    setLoading(true);
    setError('');
    setCurrentPage(1); // Reset to first page on new search
    setCurrentQuery(query);
    setCurrentLocation(location);

    // Auto-detect country from location
    let targetCountry = filtersOverride?.country || selectedFilters.country;
    if (location === 'UAE' || location === 'Dubai') {
      targetCountry = 'UAE';
    } else if (['Bangalore', 'Delhi NCR', 'Mumbai', 'Hyderabad', 'Pune', 'Chennai', 'Kolkata'].includes(location)) {
      targetCountry = 'India';
    }

    // Update filters state if country changed
    if (targetCountry !== selectedFilters.country) {
      setSelectedFilters(prev => ({ ...prev, country: targetCountry }));
    }

    try {
      const filtersIdx = { ...(filtersOverride || selectedFilters), country: targetCountry };
      const data = await fetchJobs(query, location, 1, filtersIdx, currentContextId, targetCountry);
      setJobs(data);
      setHasMore(data.length > 0);
    } catch (err) {
      setError('Failed to fetch jobs. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // No-op for now as we will use useEffect for better synchronization
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

  // Auto-trigger search when filters change
  useEffect(() => {
    // Only auto-search if we have a query or at least one filter selected
    const hasFilters = Object.values(selectedFilters).some(f => f.length > 0);
    if (currentQuery || hasFilters || currentContextId) {
      handleSearch(currentQuery, currentLocation);
    }
  }, [selectedFilters, currentContextId]);

  const filteredJobs = jobs;
  const currentJobs = jobs;

  const paginate = async (pageNumber: number) => {
    setLoading(true);
    setCurrentPage(pageNumber);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    try {
      const data = await fetchJobs(currentQuery, currentLocation, pageNumber, selectedFilters, currentContextId, selectedFilters.country);
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
    <div className="min-h-screen bg-slate-50">
      {/* Professional Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                <Briefcase className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900">
                  JobPlatform<span className="text-blue-600">.ai</span> Agent
                </h1>
                <p className="text-xs text-slate-500">Autonomous Job Discovery</p>
              </div>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex items-center gap-8">
              <a href="#" className="text-sm font-medium text-slate-700 hover:text-blue-600 transition-colors">
                Find Jobs
              </a>
              <a href="#" className="text-sm font-medium text-slate-700 hover:text-blue-600 transition-colors">
                Companies
              </a>
              <a href="#" className="text-sm font-medium text-slate-700 hover:text-blue-600 transition-colors">
                Salaries
              </a>
              {/* 
              <button className="btn-primary text-sm">
                Sign In
              </button> 
              */}
              <div className="text-xs text-slate-500 font-medium px-3 py-1 bg-slate-100 rounded-full">
                Beta Access
              </div>
            </nav>
          </div>
        </div>
      </header >

      {/* Hero Section */}
      < div className="bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 relative" >
        {/* Background Pattern */}
        < div className="absolute inset-0 bg-grid-white/[0.05] bg-[size:20px_20px]" ></div >
        <div className="absolute inset-0 bg-gradient-to-t from-blue-900/20"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center mb-10">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight">
              Find Your Dream Tech Job
            </h2>
            <p className="text-blue-100 text-lg max-w-2xl mx-auto mb-6">
              Discover opportunities from top companies across India. Powered by AI-driven matching.
            </p>

            {/* Context Search */}
            <div className="flex justify-center mb-8">
              <SmartContext onContextChange={(id) => setCurrentContextId(id)} />
            </div>
          </div>

          {/* Search Bar */}
          <div className="max-w-4xl mx-auto">
            <SearchBar onSearch={handleSearch} className="shadow-2xl mb-6" />

            {/* Filters Below Search */}
            <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6">
              <FilterSidebar
                filters={FILTER_OPTIONS}
                selectedFilters={selectedFilters}
                onFilterChange={handleFilterChange}
              />
            </div>
          </div>


        </div>
      </div >

      {/* Main Content */}
      < main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" >
        {/* Job List - Full Width */}
        < div className="max-w-7xl mx-auto" >
          {/* Results Header */}
          < div className="flex items-center justify-between mb-6 bg-white rounded-xl p-4 border border-slate-200" >
            <div>
              <h3 className="text-lg font-semibold text-slate-900">
                {loading ? 'Searching...' : `${filteredJobs.length} Jobs Found`}
              </h3>
              {filteredJobs.length > 0 && (
                <p className="text-sm text-slate-500">
                  Page {currentPage}
                </p>
              )}
            </div>
            <select className="input-field w-auto text-sm">
              <option>Most Relevant</option>
              <option>Most Recent</option>
              <option>Highest Salary</option>
            </select>
          </div >

          {/* Loading State */}
          {
            loading && (
              <div className="flex flex-col items-center justify-center py-20">
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
                </div>
                <p className="mt-4 text-slate-600 font-medium">Finding the best matches...</p>
              </div>
            )
          }

          {/* Error State */}
          {
            error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-red-600 text-2xl">⚠️</span>
                </div>
                <p className="text-red-800 font-medium">{error}</p>
              </div>
            )
          }

          {/* Jobs Grid */}
          {
            !loading && !error && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {currentJobs.map(job => (
                    <JobCard key={job.id} job={job} contextId={currentContextId} />
                  ))}
                </div>

                {/* Empty State */}
                {filteredJobs.length === 0 && (
                  <div className="text-center py-20 bg-white rounded-xl border border-slate-200">
                    <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Briefcase className="w-8 h-8 text-slate-400" />
                    </div>
                    <h3 className="text-xl font-semibold text-slate-900 mb-2">No jobs found</h3>
                    <p className="text-slate-500 max-w-sm mx-auto">
                      Try adjusting your search criteria or location to find more opportunities.
                    </p>
                  </div>
                )}

                {/* Pagination */}
                {/* Only show pagination if we have jobs or if we are not on page 1 (to allow going back) */}
                {(filteredJobs.length > 0 || currentPage > 1) && (
                  <div className="mt-8 flex items-center justify-center gap-2">
                    <button
                      onClick={() => paginate(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="px-4 py-2 rounded-lg border border-slate-200 text-slate-700 font-medium hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Previous
                    </button>

                    <span className="text-slate-600 font-medium px-4">
                      Page {currentPage}
                    </span>

                    <button
                      onClick={() => paginate(currentPage + 1)}
                      disabled={!hasMore || filteredJobs.length < jobsPerPage}
                      className="px-4 py-2 rounded-lg border border-slate-200 text-slate-700 font-medium hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Next
                    </button>
                  </div>
                )}
              </>
            )
          }
        </div >
      </main >

      {/* Footer */}
      < footer className="bg-white border-t border-slate-200 mt-20" >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-slate-500 text-sm">
            © 2026 JobPortal.ai - Powered by AI • Built with ❤️ for job seekers
          </p>
        </div>
      </footer >

      {/* System Observability Console */}
      <DebugConsole />
    </div >
  );
}

export default App;
