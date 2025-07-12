
import { useState, useEffect } from "react";
import { Download, FileText, CheckCircle, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

interface ResumeGeneratorProps {
  resumeFile: File | null;
  jobDescription: string;
  selectedKeywords: string[];
  matchScore: number | null;
}

const ResumeGenerator = ({ 
  resumeFile, 
  jobDescription, 
  selectedKeywords, 
  matchScore 
}: ResumeGeneratorProps) => {
  const [isGenerating, setIsGenerating] = useState(true);
  const [progress, setProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  const finalScore = matchScore ? Math.min(matchScore + (selectedKeywords.length * 3), 95) : 85;

  useEffect(() => {
    const generateResume = async () => {
      setIsGenerating(true);
      setProgress(0);

      // Simulate resume generation with progress updates
      const steps = [
        { message: "Analyzing original resume structure...", duration: 1000 },
        { message: "Integrating selected keywords...", duration: 1500 },
        { message: "Optimizing for ATS compatibility...", duration: 1200 },
        { message: "Formatting and finalizing...", duration: 800 },
      ];

      for (let i = 0; i < steps.length; i++) {
        await new Promise(resolve => setTimeout(resolve, steps[i].duration));
        setProgress(((i + 1) / steps.length) * 100);
      }

      setIsGenerating(false);
      setIsComplete(true);
    };

    generateResume();
  }, []);

  const handleDownload = () => {
    // In a real implementation, this would download the generated resume
    const blob = new Blob(['Sample optimized resume content...'], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'optimized-resume.pdf';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleStartOver = () => {
    window.location.reload();
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Download className="h-5 w-5" />
          Step 5: Your Optimized Resume
        </CardTitle>
        <CardDescription>
          AI-generated resume optimized for ATS systems and job requirements
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {isGenerating ? (
          <div className="space-y-6">
            <div className="text-center py-8">
              <div className="animate-pulse mb-4">
                <FileText className="h-16 w-16 text-blue-600 mx-auto" />
              </div>
              <h3 className="text-lg font-medium mb-2">Generating Your Optimized Resume...</h3>
              <p className="text-gray-600 mb-4">
                Please wait while we create your ATS-friendly resume
              </p>
              <Progress value={progress} className="w-full max-w-md mx-auto" />
              <p className="text-sm text-gray-500 mt-2">{Math.round(progress)}% complete</p>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Success Message */}
            <div className="text-center p-6 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg">
              <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Your Resume is Ready! 🎉
              </h3>
              <p className="text-gray-600 mb-4">
                We've optimized your resume with the selected keywords and improved ATS compatibility
              </p>
              
              <div className="flex items-center justify-center gap-4 mb-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{finalScore}%</div>
                  <p className="text-sm text-gray-600">Final Match Score</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{selectedKeywords.length}</div>
                  <p className="text-sm text-gray-600">Keywords Added</p>
                </div>
              </div>
            </div>

            {/* Improvements Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Star className="h-5 w-5 text-yellow-500" />
                  What We Improved
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-2">Keywords Integrated:</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedKeywords.map(keyword => (
                        <Badge key={keyword} variant="outline" className="bg-green-50 text-green-700">
                          {keyword}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium mb-2">ATS Optimizations:</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• Improved keyword density and placement</li>
                      <li>• Enhanced section headers and formatting</li>
                      <li>• Optimized for machine readability</li>
                      <li>• Maintained professional appearance</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Download Actions */}
            <div className="flex flex-col sm:flex-row gap-3">
              <Button 
                onClick={handleDownload}
                className="flex-1 bg-green-600 hover:bg-green-700"
                size="lg"
              >
                <Download className="mr-2 h-5 w-5" />
                Download Optimized Resume (PDF)
              </Button>
              
              <Button 
                variant="outline" 
                onClick={handleStartOver}
                size="lg"
              >
                Optimize Another Resume
              </Button>
            </div>

            {/* Tips */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">💡 Pro Tips for Job Applications:</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Customize your resume for each job application</li>
                <li>• Use the same keywords from the job description in your cover letter</li>
                <li>• Keep your LinkedIn profile updated with the same keywords</li>
                <li>• Consider getting your resume reviewed by industry professionals</li>
              </ul>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ResumeGenerator;
