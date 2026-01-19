import { useState, useRef } from 'react';
import { Upload, FileText, X, Loader2, CheckCircle } from 'lucide-react';
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
        <div className="flex flex-col gap-2">
            {/* Upload Area / Active State */}
            {!activeContext ? (
                <div
                    className="flex items-center gap-2 px-3 py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg cursor-pointer transition-all text-white/90 text-sm"
                    onClick={() => fileInputRef.current?.click()}
                >
                    {isUploading ? (
                        <Loader2 className="w-4 h-4 animate-spin text-blue-200" />
                    ) : (
                        <Upload className="w-4 h-4 text-blue-200" />
                    )}
                    <span className="hidden sm:inline">Upload Resume for Smart Search</span>
                    <span className="sm:hidden">Attach Resume</span>
                    <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        accept=".pdf,.docx,.doc"
                        onChange={handleUpload}
                    />
                </div>
            ) : (
                <div className="flex items-center gap-2 px-3 py-2 bg-emerald-500/20 border border-emerald-500/30 rounded-lg text-emerald-100 text-sm animate-fade-in-up">
                    <div className="flex items-center gap-1.5 flex-1 min-w-0">
                        <FileText className="w-4 h-4 shrink-0 text-emerald-400" />
                        <span className="truncate font-medium">{activeContext.name}</span>
                        <span className="text-emerald-500/70 text-xs whitespace-nowrap hidden sm:inline">• Context Active</span>
                    </div>
                    <button
                        onClick={clearContext}
                        className="p-1 hover:bg-emerald-500/20 rounded-full transition-colors"
                    >
                        <X className="w-3.5 h-3.5 text-emerald-400" />
                    </button>
                </div>
            )}
        </div>
    );
}
