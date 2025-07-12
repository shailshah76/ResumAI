
import { useState, useEffect } from "react";
import { Target, TrendingUp, AlertCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

interface MatchResultsProps {
  resumeFile: File | null;
  jobDescription: string;
  onAnalysisComplete: (score: number, keywords: string[]) => void;
}

const MatchResults = ({ resumeFile, jobDescription, onAnalysisComplete }: MatchResultsProps) => {
  const [isAnalyzing, setIsAnalyzing] = useState(true);
  const [matchScore, setMatchScore] = useState(0);

  useEffect(() => {
    // Simulate analysis process
    const analyzeMatch = async () => {
      setIsAnalyzing(true);
      
      // Simulate processing time
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Mock analysis results
      const score = Math.floor(Math.random() * 40) + 45; // 45-85%
      const keywords = [
        'React', 'TypeScript', 'Node.js', 'AWS', 'PostgreSQL',
        'Docker', 'Kubernetes', 'Microservices', 'CI/CD', 'Agile',
        'API Development', 'GraphQL', 'Jest Testing', 'MongoDB'
      ];
      
      setMatchScore(score);
      setIsAnalyzing(false);
      
      // Complete analysis after showing results
      setTimeout(() => {
        onAnalysisComplete(score, keywords);
      }, 2000);
    };

    if (resumeFile && jobDescription) {
      analyzeMatch();
    }
  }, [resumeFile, jobDescription, onAnalysisComplete]);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreMessage = (score: number) => {
    if (score >= 80) return 'Excellent match! Your resume aligns well with the job requirements.';
    if (score >= 60) return 'Good match! There are some areas for improvement.';
    return 'Needs improvement. Let\'s optimize your resume for better ATS compatibility.';
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5" />
          Step 3: Resume Analysis
        </CardTitle>
        <CardDescription>
          Analyzing your resume against the job description
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isAnalyzing ? (
          <div className="space-y-6">
            <div className="flex items-center justify-center py-12">
              <div className="text-center space-y-4">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <h3 className="text-lg font-medium">Analyzing Your Resume...</h3>
                <p className="text-gray-600">
                  Comparing skills, experience, and keywords with job requirements
                </p>
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                Extracting resume content...
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                Parsing job requirements...
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                Calculating match score...
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Match Score */}
            <div className="text-center p-6 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg">
              <div className="mb-4">
                <div className={`text-6xl font-bold ${getScoreColor(matchScore)} mb-2`}>
                  {matchScore}%
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Resume Match Score
                </h3>
                <p className="text-gray-600">
                  {getScoreMessage(matchScore)}
                </p>
              </div>
              
              <Progress value={matchScore} className="w-full max-w-md mx-auto h-3" />
            </div>

            {/* Analysis Breakdown */}
            <div className="grid md:grid-cols-2 gap-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                    Strengths Found
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2">
                    <Badge variant="outline" className="bg-green-50 text-green-700">
                      Technical Skills Match
                    </Badge>
                    <Badge variant="outline" className="bg-green-50 text-green-700">
                      Experience Level
                    </Badge>
                    <Badge variant="outline" className="bg-green-50 text-green-700">
                      Education Requirements
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-yellow-600" />
                    Areas to Improve
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2">
                    <Badge variant="outline" className="bg-yellow-50 text-yellow-700">
                      Missing Keywords
                    </Badge>
                    <Badge variant="outline" className="bg-yellow-50 text-yellow-700">
                      Industry Buzzwords
                    </Badge>
                    <Badge variant="outline" className="bg-yellow-50 text-yellow-700">
                      Technical Certifications
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="text-center py-4">
              <p className="text-gray-600">
                Preparing keyword suggestions to improve your match score...
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default MatchResults;
