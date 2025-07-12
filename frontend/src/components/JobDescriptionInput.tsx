
import { useState } from "react";
import { FileText, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";

interface JobDescriptionInputProps {
  onSubmit: (description: string) => void;
  hasResume: boolean;
}

const JobDescriptionInput = ({ onSubmit, hasResume }: JobDescriptionInputProps) => {
  const [description, setDescription] = useState('');

  const handleTextChange = (value: string) => {
    setDescription(value);
    // Update parent component immediately when text changes
    onSubmit(value.trim());
  };

  const sampleJD = `We are seeking a Senior Software Engineer to join our dynamic development team. 

Key Requirements:
• 5+ years of experience in full-stack development
• Proficiency in React, Node.js, and TypeScript
• Experience with cloud platforms (AWS, Azure, or GCP)
• Strong knowledge of database systems (PostgreSQL, MongoDB)
• Familiarity with DevOps practices and CI/CD pipelines
• Experience with Agile/Scrum methodologies
• Excellent problem-solving and communication skills

Preferred Qualifications:
• Experience with microservices architecture
• Knowledge of container technologies (Docker, Kubernetes)
• Previous experience in fintech or healthcare industries
• Bachelor's degree in Computer Science or related field`;

  const fillSample = () => {
    setDescription(sampleJD);
    onSubmit(sampleJD.trim());
  };

  return (
    <Card className="w-full h-fit">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Job Description
        </CardTitle>
        <CardDescription>
          Paste the job description or requirements you want to match your resume against
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Textarea
            placeholder="Paste the job description here... Include requirements, qualifications, and key skills mentioned in the job posting."
            value={description}
            onChange={(e) => handleTextChange(e.target.value)}
            className="min-h-[300px] resize-none"
          />
        </div>
        
        <div className="flex items-center justify-between">
          <Button 
            variant="outline" 
            onClick={fillSample}
            className="text-sm"
          >
            Use Sample Job Description
          </Button>
          
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">
              {description.length} characters
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default JobDescriptionInput;
