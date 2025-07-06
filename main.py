from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from resume import ResumeModel
from langchain.output_parsers import PydanticOutputParser
from evaluator import evaluate_resumes
import json

import os

# Load environment variables from .env file
load_dotenv()

resume_parser = PydanticOutputParser(pydantic_object=ResumeModel)

# Initialize the LangChain model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

SYSTEM_MSG2 = f"""
     You are an experienced tech recruiter with deep knowledge of the software industry, resume best practices, and hiring manager expectations at top tech companies.
     Your goal is to guide users in creating a highly effective, ATS-friendly, and tailored resume for software developer roles.
     You consider factors like the target role, tech stack, project impact, and clarity of communication. 
     You give actionable advice, rewrite content to improve phrasing and impact, and ensure the final resume stands out to recruiters and technical interviewers."""

SYSTEM_MSG = (
    "You are an experienced tech recruiter with deep knowledge of the software industry, "
    "resume best practices, and hiring manager expectations at top tech companies. "
    "Return your answer in the format specified."
)

prompt_tmpl = ChatPromptTemplate.from_messages(
    [
        ("system", "{system}"),
        ("user", "Using the job description below, craft a tailored resume.\n"
                 "{job_description}\n\n{format_instructions}")
    ]
)

# Pre‑fill the format instructions once
prompt1 = prompt_tmpl.partial(
    system=SYSTEM_MSG,
    format_instructions=resume_parser.get_format_instructions()
)

prompt2 = prompt_tmpl.partial(
    system=SYSTEM_MSG2,
    format_instructions=resume_parser.get_format_instructions()
)

chain1 = prompt1 | llm | resume_parser        # LangChain “pipe” syntax
chain2 = prompt2 | llm | resume_parser        # LangChain “pipe” syntax

job_desc = input("Paste JD: ")

result1: ResumeModel = chain1.invoke({"job_description": job_desc})
result2: ResumeModel = chain2.invoke({"job_description": job_desc})

# print(result1.model_dump_json(indent=2))
# print(result2.model_dump_json(indent=2))

# Evaluate the resumes
evaluation = evaluate_resumes(llm, job_desc, result1.model_dump_json(), result2.model_dump_json())
print("Evaluation Result:")
print("Evaluation:", json.dumps(evaluation, indent=2))