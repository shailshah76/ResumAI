# evaluator.py (Pydantic version)
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Literal

class EvaluationResult(BaseModel):
    resume_a: int = Field(description="Score for resume A out of 100")
    resume_b: int = Field(description="Score for resume B out of 100")
    winner: Literal["A", "B"] = Field(description="Which resume is better")
    rationale: str = Field(description="Brief explanation of why the winner is stronger")

# Create parser
evaluation_parser = PydanticOutputParser(pydantic_object=EvaluationResult)

SYSTEM = (
    "You are an experienced tech recruiter. "
    "Compare two resumes (A and B) against the given job description."
)

EVAL_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM),
        (
            "user",
            "Job description:\n{job_description}\n\n"
            "### Resume A\n{resume_a}\n\n"
            "### Resume B\n{resume_b}\n\n"
            "Score each resume out of 100 and explain briefly why the winner is stronger.\n\n"
            "{format_instructions}"
        ),
    ]
)

def evaluate_resumes(llm, job_description: str, resume_a: str, resume_b: str) -> Dict:
    try:
        # Create the evaluation chain
        chain = EVAL_PROMPT | llm | evaluation_parser
        
        # Get format instructions
        format_instructions = evaluation_parser.get_format_instructions()
        
        # Invoke the chain
        result = chain.invoke({
            "job_description": job_description,
            "resume_a": resume_a,
            "resume_b": resume_b,
            "format_instructions": format_instructions
        })
        
        # Convert to dict
        return result.model_dump()
        
    except Exception as e:
        print(f"Error during evaluation: {e}")
        # Return a default response if evaluation fails
        return {
            "resume_a": 50,
            "resume_b": 50,
            "winner": "A",
            "rationale": f"Error during evaluation: {str(e)}"
        }