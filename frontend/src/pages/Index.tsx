import { useState } from "react";
import { Upload, FileText, Target, Download, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import FileUpload from "@/components/FileUpload";
import JobDescriptionInput from "@/components/JobDescriptionInput";
import MatchResults from "@/components/MatchResults";
import KeywordSelector from "@/components/KeywordSelector";
import ResumeGenerator from "@/components/ResumeGenerator";

type Step = 'input' | 'analyze' | 'keywords' | 'generate';

const Index = () => {
  const [currentStep, setCurrentStep] = useState<Step>('input');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [matchScore, setMatchScore] = useState<number | null>(null);
  const [suggestedKeywords, setSuggestedKeywords] = useState<string[]>([]);
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);
  const { toast } = useToast();

  const steps = [
    { id: 'input', title: 'Input', icon: Upload, completed: !!resumeFile && !!jobDescription },
    { id: 'analyze', title: 'Analysis', icon: Target, completed: matchScore !== null },
    { id: 'keywords', title: 'Keywords', icon: CheckCircle, completed: selectedKeywords.length > 0 },
    { id: 'generate', title: 'Generate', icon: Download, completed: false },
  ];

  const handleFileUpload = (file: File) => {
    setResumeFile(file);
  };

  const handleJobDescriptionSubmit = (description: string) => {
    setJobDescription(description);
  };

  const handleAnalyze = () => {
    // Validate required fields
    if (!resumeFile) {
      toast({
        title: "Resume Required",
        description: "Please upload your resume before starting the analysis.",
        variant: "destructive",
      });
      return;
    }

    if (!jobDescription.trim()) {
      toast({
        title: "Job Description Required", 
        description: "Please enter a job description before starting the analysis.",
        variant: "destructive",
      });
      return;
    }

    // Proceed with analysis if both fields are present
    setCurrentStep('analyze');
  };

  const handleAnalysisComplete = (score: number, keywords: string[]) => {
    setMatchScore(score);
    setSuggestedKeywords(keywords);
    setCurrentStep('keywords');
  };

  const handleKeywordsSelected = (keywords: string[]) => {
    setSelectedKeywords(keywords);
    setCurrentStep('generate');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent mb-2">
              Resume Helper AI
            </h1>
            <p className="text-xl text-gray-600">Boost Your Resume. Match Jobs Smarter.</p>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Progress Steps */}
        <div className="mb-12">
          <div className="flex justify-center items-center space-x-4 overflow-x-auto pb-4">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isActive = currentStep === step.id;
              const isCompleted = step.completed;
              
              return (
                <div key={step.id} className="flex items-center">
                  <div className={`flex flex-col items-center min-w-0 ${isActive ? 'scale-110' : ''} transition-transform duration-200`}>
                    <div className={`
                      w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-all duration-200
                      ${isCompleted ? 'bg-green-500 text-white' : 
                        isActive ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-500'}
                    `}>
                      <Icon size={20} />
                    </div>
                    <span className={`text-sm font-medium text-center ${
                      isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-500'
                    }`}>
                      {step.title}
                    </span>
                  </div>
                  {index < steps.length - 1 && (
                    <div className={`w-16 h-0.5 mx-4 ${
                      steps[index + 1].completed ? 'bg-green-300' : 'bg-gray-300'
                    }`} />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Main Content */}
        {currentStep === 'input' && (
          <div className="space-y-8">
            <div className="grid lg:grid-cols-2 gap-8">
              {/* Resume Upload */}
              <div>
                <FileUpload onFileUpload={handleFileUpload} />
              </div>

              {/* Job Description Input */}
              <div>
                <JobDescriptionInput 
                  onSubmit={handleJobDescriptionSubmit}
                  hasResume={!!resumeFile}
                />
              </div>
            </div>

            {/* Static Analyze Button - Always visible */}
            <div className="flex justify-center">
              <Button 
                onClick={handleAnalyze}
                size="lg"
                className="bg-blue-600 hover:bg-blue-700 text-lg px-12 py-4"
              >
                <Target className="mr-2 h-5 w-5" />
                Start Analysis
              </Button>
            </div>
          </div>
        )}

        {currentStep === 'analyze' && (
          <MatchResults
            resumeFile={resumeFile}
            jobDescription={jobDescription}
            onAnalysisComplete={handleAnalysisComplete}
          />
        )}
        
        {currentStep === 'keywords' && (
          <KeywordSelector
            suggestedKeywords={suggestedKeywords}
            matchScore={matchScore}
            onKeywordsSelected={handleKeywordsSelected}
          />
        )}
        
        {currentStep === 'generate' && (
          <ResumeGenerator
            resumeFile={resumeFile}
            jobDescription={jobDescription}
            selectedKeywords={selectedKeywords}
            matchScore={matchScore}
          />
        )}
      </div>
    </div>
  );
};

export default Index;
