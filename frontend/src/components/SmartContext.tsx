import { useState, useRef } from 'react';
import { Upload, FileText, X, Loader2 } from 'lucide-react';
import { uploadResume } from '../api';

interface SmartContextProps {
    onContextChange: (contextId: string | undefined) => void;
}

export function SmartContext({ onContextChange }: SmartContextProps) {
    const [isUploading, setIsUploading] = useState(false);
    const [activeContext, setActiveContext] = useState<{ id: string; name: string } | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setIsUploading(true);
        try {
            const data = await uploadResume(file);
            setActiveContext({ id: data.context_id, name: data.filename });
            onContextChange(data.context_id);
        } catch (error) {
            console.error("Upload failed", error);
            alert("Failed to upload resume. Please try a valid PDF/DOCX.");
        } finally {
            setIsUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const clearContext = () => {
        setActiveContext(null);
        onContextChange(undefined);
    };

    return (
        <div className="w-full">
            {!activeContext ? (
                <div
                    className="group flex flex-col items-center justify-center p-6 bg-slate-500/5 border border-dashed border-white/10 rounded-2xl hover:border-blue-500/30 hover:bg-slate-500/10 transition-all cursor-pointer"
                    onClick={() => fileInputRef.current?.click()}
                >
                    <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                        {isUploading ? (
                            <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
                        ) : (
                            <Upload className="w-5 h-5 text-blue-400" />
                        )}
                    </div>
                    <p className="text-xs font-bold text-main mb-1">Upload Resume</p>
                    <p className="text-[10px] text-dim text-center font-medium">Power your search with AI matching</p>
                    <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        accept=".pdf,.docx,.doc"
                        onChange={handleUpload}
                    />
                </div>
            ) : (
                <div className="p-4 bg-blue-600/10 border border-blue-500/20 rounded-2xl flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center shrink-0">
                        <FileText className="w-5 h-5 text-blue-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-xs font-bold text-main truncate">{activeContext.name}</p>
                        <p className="text-[10px] text-blue-400/70 font-bold uppercase tracking-widest">Active Search Context</p>
                    </div>
                    <button
                        onClick={clearContext}
                        className="p-1.5 hover:bg-slate-500/10 rounded-full transition-colors text-dim hover:text-main"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>
            )}
        </div>
    );
}
