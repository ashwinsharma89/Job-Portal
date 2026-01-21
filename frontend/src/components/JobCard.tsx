import { type Job, sendFeedback } from '../api';
import { MapPin, Briefcase, DollarSign, Clock, Building2, Sparkles } from 'lucide-react';

interface JobCardProps {
    job: Job;
    className?: string;
    contextId?: string;
}

export function JobCard({ job, className = '', contextId }: JobCardProps) {
    const timeAgo = (dateString?: string) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

        const days = Math.floor(diffInSeconds / 86400);
        if (days > 0) return `${days}d ago`;

        const hours = Math.floor(diffInSeconds / 3600);
        if (hours > 0) return `${hours}h ago`;

        return 'Just now';
    };

    const handleInteraction = (type: 'CLICK' | 'APPLY') => {
        sendFeedback(job.id, type, contextId);
    };

    const matchScore = job.relevance_score || 0;
    const isHighMatch = matchScore >= 80;

    return (
        <div className={`glass-card glass-hover p-6 flex flex-col group relative ${className}`}>
            {/* AI Match Badge (Top Right) */}
            {matchScore > 0 && (
                <div className="absolute top-4 right-4 z-10">
                    <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-[10px] font-bold tracking-tighter uppercase ${isHighMatch ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' : 'bg-slate-500/10 text-dim border-white/10'}`}>
                        {isHighMatch && <Sparkles className="w-3 h-3 text-blue-400 animate-pulse" />}
                        {Math.round(matchScore)}% Match
                    </div>
                </div>
            )}

            {/* Logo and Title Section */}
            <div className="flex flex-col items-center text-center mb-6">
                <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center p-2 mb-4 border border-white/5 shadow-inner group-hover:border-blue-500/30 transition-colors overflow-hidden">
                    {job.logo_url ? (
                        <img src={job.logo_url} alt={job.company} className="w-full h-full object-contain" />
                    ) : (
                        <Building2 className="w-8 h-8 text-slate-600" />
                    )}
                </div>

                <div className="w-full">
                    <h3
                        onClick={() => handleInteraction('CLICK')}
                        className="text-lg font-bold text-main leading-tight mb-1 hover:text-blue-400 transition-colors cursor-pointer line-clamp-2 min-h-[3rem] px-2"
                    >
                        {job.title}
                    </h3>
                    <p className="text-xs font-semibold text-dim uppercase tracking-widest">{job.company}</p>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-6">
                <div className="flex items-center gap-2 bg-slate-500/5 px-3 py-2 rounded-xl border border-white/5">
                    <MapPin className="w-3.5 h-3.5 text-blue-500" />
                    <span className="text-xs font-semibold text-main truncate">{job.location || 'Remote'}</span>
                </div>
                {(job.experience_min > 0 || job.experience_max > 0) && (
                    <div className="flex items-center gap-2 bg-slate-500/5 px-3 py-2 rounded-xl border border-white/5">
                        <Briefcase className="w-3.5 h-3.5 text-indigo-500" />
                        <span className="text-xs font-semibold text-main truncate">{job.experience_min || 0}+{job.experience_max || 0} Yrs</span>
                    </div>
                )}
                <div className={`flex items-center gap-2 bg-slate-500/5 px-3 py-2 rounded-xl border border-white/5 ${(job.experience_min > 0 || job.experience_max > 0) ? '' : 'col-span-2'}`}>
                    <DollarSign className="w-3.5 h-3.5 text-emerald-500" />
                    <span className="text-xs font-bold text-main">
                        {job.ctc_min ? `₹${(job.ctc_min / 100000).toFixed(1)}L - ₹${(job.ctc_max! / 100000).toFixed(1)}L` : 'Salary Undisclosed'}
                    </span>
                </div>
            </div>

            <div className="mt-auto pt-6 border-t border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-[10px] text-dim font-bold uppercase tracking-tighter">
                    <Clock className="w-3 h-3" />
                    {timeAgo(job.posted_at)}
                </div>

                <a
                    href={job.apply_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={() => handleInteraction('APPLY')}
                    className="btn-modern-primary !px-6 !py-2 text-xs !rounded-lg"
                >
                    Apply Now
                </a>
            </div>

            {/* Match Breakdown Tooltip (Overlaying) */}
            {job.match_breakdown && (
                <div className="absolute inset-x-0 bottom-0 p-4 translate-y-full opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none">
                    <div className="glass-card bg-[#161821]/95 p-3 text-[10px] border-blue-500/20 shadow-2xl">
                        <p className="text-blue-400 font-bold mb-2 uppercase tracking-widest border-b border-white/5 pb-1">AI Reasoning</p>
                        <div className="space-y-1">
                            {Object.entries(job.match_breakdown).slice(0, 4).map(([key, val]) => {
                                if (key === 'final_score') return null;
                                const label = key.replace(/_/g, ' ');
                                return (
                                    <div key={key} className="flex justify-between items-center opacity-80">
                                        <span className="capitalize">{label}</span>
                                        <span className={val > 0 ? 'text-emerald-400' : 'text-red-400'}>{val > 0 ? `+${val}` : val}</span>
                                    </div>
                                )
                            })}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
