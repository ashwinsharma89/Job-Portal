import { type Job, sendFeedback } from '../api';
import { MapPin, Briefcase, DollarSign, ExternalLink, Clock, Building2 } from 'lucide-react';

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

    return (
        <div className={`card card-hover p-5 ${className} h-full flex flex-col`}>
            <div className="flex items-start gap-3 mb-3">
                {/* Company Logo */}
                <div className="w-12 h-12 bg-gradient-to-br from-slate-100 to-slate-200 rounded-lg flex items-center justify-center flex-shrink-0 overflow-hidden border border-slate-200">
                    {job.logo_url ? (
                        <img src={job.logo_url} alt={job.company} className="w-full h-full object-contain p-1.5" />
                    ) : (
                        <Building2 className="w-6 h-6 text-slate-400" />
                    )}
                </div>

                <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                        {/* Job Title */}
                        <h3
                            onClick={() => handleInteraction('CLICK')}
                            className="text-base font-semibold text-slate-900 leading-tight mb-1 hover:text-blue-600 transition-colors cursor-pointer line-clamp-2"
                        >
                            {job.title}
                        </h3>
                        {/* Match Score Badge */}
                        {job.relevance_score !== undefined && job.relevance_score > 0 && (
                            <div className="relative group">
                                <div className={`
                                    flex-shrink-0 px-2 py-1 rounded-md text-xs font-bold border cursor-help
                                    ${job.relevance_score >= 80 ? 'bg-green-50 text-green-700 border-green-200' :
                                        job.relevance_score >= 50 ? 'bg-amber-50 text-amber-700 border-amber-200' :
                                            'bg-slate-50 text-slate-600 border-slate-200'}
                                `}>
                                    {Math.round(job.relevance_score)}% Match
                                </div>

                                {/* Explainability Tooltip */}
                                {job.match_breakdown && (
                                    <div className="absolute top-full right-0 mt-2 w-48 bg-white border border-slate-200 shadow-xl rounded-xl p-3 z-50 hidden group-hover:block animate-in fade-in slide-in-from-top-1 duration-200">
                                        <div className="text-xs font-semibold text-slate-900 mb-2 border-b border-slate-100 pb-1">Match Breakdown</div>
                                        <div className="space-y-1.5">
                                            {Object.entries(job.match_breakdown).map(([key, val]) => {
                                                if (key === 'final_score') return null;
                                                // Format key (e.g. seniority_penalty -> Seniority Penalty)
                                                const label = key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
                                                const isPenalty = val < 1 && val > 0; // Check if it's a multiplier penalty
                                                const displayVal = isPenalty ? `-${Math.round((1 - val) * 100)}%` : `+${val}`;

                                                return (
                                                    <div key={key} className="flex justify-between items-center text-xs">
                                                        <span className="text-slate-500">{label}</span>
                                                        <span className={`font-medium ${isPenalty ? 'text-red-600' : 'text-slate-700'}`}>
                                                            {displayVal}
                                                        </span>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Company Name */}
                    <p className="text-sm text-slate-600 font-medium truncate">{job.company}</p>
                </div>
            </div>

            {/* Job Details */}
            <div className="flex flex-wrap gap-x-3 gap-y-1.5 text-xs text-slate-500 mb-3">
                <div className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span className="truncate">{job.location || 'Remote'}</span>
                </div>

                {job.experience_min !== undefined && job.experience_max !== undefined && (
                    <div className="flex items-center gap-1">
                        <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                        <span>{job.experience_min}-{job.experience_max} Yrs</span>
                    </div>
                )}

                {job.ctc_min && job.ctc_max && (
                    <div className="flex items-center gap-1">
                        <DollarSign className="w-3.5 h-3.5 text-slate-400" />
                        <span>₹{job.ctc_min}-{job.ctc_max} LPA</span>
                    </div>
                )}

                <div className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span>{timeAgo(job.posted_at)}</span>
                </div>
            </div>

            {/* Footer */}
            <div className="mt-auto flex items-center justify-between gap-2">
                {/* Source Badge */}
                {job.source && (
                    <span className="badge badge-secondary text-xs">
                        {job.source}
                    </span>
                )}

                {/* Apply Button */}
                {job.apply_link && (
                    <a
                        href={job.apply_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={() => handleInteraction('APPLY')}
                        className="btn-primary text-xs px-4 py-2 flex items-center gap-1.5 whitespace-nowrap ml-auto"
                    >
                        Apply
                        <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                )}
            </div>
        </div>
    );
}
