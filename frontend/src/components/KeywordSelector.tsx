
import { useState } from "react";
import { CheckCircle, ArrowRight, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";

interface KeywordSelectorProps {
  suggestedKeywords: string[];
  matchScore: number | null;
  onKeywordsSelected: (keywords: string[]) => void;
}

const KeywordSelector = ({ suggestedKeywords, matchScore, onKeywordsSelected }: KeywordSelectorProps) => {
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);

  const handleKeywordToggle = (keyword: string) => {
    setSelectedKeywords(prev => 
      prev.includes(keyword) 
        ? prev.filter(k => k !== keyword)
        : [...prev, keyword]
    );
  };

  const handleSelectAll = () => {
    setSelectedKeywords(suggestedKeywords);
  };

  const handleClearAll = () => {
    setSelectedKeywords([]);
  };

  const estimatedNewScore = matchScore ? Math.min(matchScore + (selectedKeywords.length * 3), 95) : 0;

  const handleContinue = () => {
    if (selectedKeywords.length > 0) {
      onKeywordsSelected(selectedKeywords);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CheckCircle className="h-5 w-5" />
          Step 4: Select Keywords to Include
        </CardTitle>
        <CardDescription>
          Choose relevant keywords that you're familiar with or willing to add to your resume
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Current vs Projected Score */}
        <div className="grid md:grid-cols-2 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-600 mb-1">
              {matchScore}%
            </div>
            <p className="text-sm text-gray-600">Current Score</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600 mb-1">
              {estimatedNewScore}%
            </div>
            <p className="text-sm text-green-600">Projected Score</p>
          </div>
        </div>

        {/* Keyword Selection */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium text-gray-900">
              Suggested Keywords ({suggestedKeywords.length})
            </h3>
            <div className="space-x-2">
              <Button variant="outline" size="sm" onClick={handleSelectAll}>
                Select All
              </Button>
              <Button variant="outline" size="sm" onClick={handleClearAll}>
                Clear All
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {suggestedKeywords.map((keyword, index) => {
              const isSelected = selectedKeywords.includes(keyword);
              const isHighPriority = index < 5; // First 5 are high priority
              
              return (
                <div
                  key={keyword}
                  className={`flex items-center space-x-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                    isSelected 
                      ? 'border-blue-300 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleKeywordToggle(keyword)}
                >
                  <Checkbox
                    checked={isSelected}
                    onChange={() => handleKeywordToggle(keyword)}
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">{keyword}</span>
                      {isHighPriority && (
                        <Star className="h-3 w-3 text-yellow-500 fill-current" />
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Keywords Summary */}
        {selectedKeywords.length > 0 && (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">
              Selected Keywords ({selectedKeywords.length})
            </h4>
            <div className="flex flex-wrap gap-2">
              {selectedKeywords.map(keyword => (
                <Badge key={keyword} variant="outline" className="bg-blue-100 text-blue-800">
                  {keyword}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="flex justify-between items-center pt-4">
          <p className="text-sm text-gray-600">
            {selectedKeywords.length === 0 
              ? 'Select keywords to improve your resume match score'
              : `Selected ${selectedKeywords.length} keywords • Estimated score increase: +${selectedKeywords.length * 3}%`
            }
          </p>
          
          <Button 
            onClick={handleContinue}
            disabled={selectedKeywords.length === 0}
            className="bg-blue-600 hover:bg-blue-700"
          >
            Generate Optimized Resume
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default KeywordSelector;
