import axios from 'axios';
import { debugStore } from './components/DebugConsole';
import { scrapeStore } from './components/SearchStatus';

// In development (Vite), it uses the proxy in vite.config.ts or defaults to localhost
// In production (Docker/Nginx), it should use relative path '/api' which Nginx proxies
const BASE_URL = import.meta.env.VITE_API_URL || '/api';
const API_URL = `${BASE_URL}/jobs`;
const UPLOAD_URL = `${BASE_URL}/upload_resume`;
const FEEDBACK_URL = `${BASE_URL}/feedback`;

export interface Job {
    id: number;
    title: string;
    company: string;
    location?: string;
    experience_min?: number;
    experience_max?: number;
    ctc_min?: number;
    ctc_max?: number;
    posted_at?: string;
    apply_link?: string;
    source?: string;
    logo_url?: string;
    description?: string;
    relevance_score?: number;
    match_breakdown?: Record<string, number>;
}

export const fetchJobs = async (
    query: string,
    location?: string,
    page: number = 1,
    filters?: {
        experience: string[];
        ctc: string[];
        skills: string[];
        jobPortals: string[];
    },
    contextId?: string,
    country: string = "India"
): Promise<Job[]> => {
    const params = new URLSearchParams();
    params.append('query', query);
    params.append('country', country);
    if (location) params.append('location', location);
    if (contextId) params.append('context_id', contextId);
    params.append('page', page.toString());

    if (filters) {
        filters.experience.forEach(exp => params.append('experience', exp));
        filters.ctc.forEach(ctc => params.append('ctc', ctc));
        filters.skills.forEach(skill => params.append('skills', skill));
        filters.jobPortals.forEach(portal => params.append('jobPortals', portal));
    }



    const response = await axios.get<Job[]>(`${API_URL}/jobs`, { params, timeout: 30000 });

    // Capture Debug Info (Axios lowercases headers)
    const debugInfo = response.headers['x-debug-info'];
    console.log("Debug Header content:", debugInfo);

    if (debugInfo) {
        try {
            const metrics = typeof debugInfo === 'string' ? JSON.parse(debugInfo) : debugInfo;
            debugStore.setMetrics(metrics);
        } catch (e) {
            console.error("Failed to parse debug info", e);
        }
    } else {
        console.warn("No X-Debug-Info header found in response.");
    }

    // Capture Scrape Signal
    const isBackgroundScrape = response.headers['x-background-scrape'] === 'true';
    if (isBackgroundScrape) {
        scrapeStore.setScraping(true);
    }

    return response.data;
};

export const uploadResume = async (file: File): Promise<{ context_id: string, filename: string }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_URL}/context/upload`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
    return response.data;
};

export const sendFeedback = async (jobId: number, actionType: 'CLICK' | 'APPLY' | 'DISMISS', contextId?: string) => {
    try {
        await axios.post(`${API_URL}/feedback`, {
            job_id: jobId,
            action_type: actionType,
            context_id: contextId
        });
    } catch (error) {
        console.error("Failed to send feedback:", error);
    }
};
