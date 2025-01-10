import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
import PyPDF2
import docx
import re
from typing import Dict, List

class ResumeAnalyzer:
    def __init__(self):
        self.model_name = "t5-small"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load model and tokenizer
        self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name).to(self.device)

        # Define analysis categories
        self.categories = [
            "work_experience",
            "education",
            "skills",
            "achievements",
            "formatting",
            "ats_compatibility"
        ]

    def read_resume(self, file_path: str) -> str:
        """Read resume content from PDF or DOCX"""
        text = ""
        if file_path.endswith('.pdf'):
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
        elif file_path.endswith('.docx'):
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        return text

    def analyze_section(self, section: str, content: str) -> str:
        """Analyze specific resume section"""
        prompt = f"Analyze this resume {section}. Provide specific improvements:\n{content}"
        
        input_ids = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True
        ).input_ids.to(self.device)

        outputs = self.model.generate(
            input_ids,
            max_length=150,
            num_beams=4,
            temperature=0.7,
            no_repeat_ngram_size=2
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def check_ats_compatibility(self, text: str) -> Dict:
        """Check resume for ATS compatibility issues"""
        issues = []
        
        # Check for common ATS issues
        if re.search(r'<|>|\{|\}|\[|\]', text):
            issues.append("Contains special characters that may confuse ATS")
        
        if re.search(r'\.(png|jpg|jpeg|gif|bmp)$', text, re.MULTILINE):
            issues.append("Contains images without alt text")
            
        if len(text.split()) < 100:
            issues.append("Content might be too brief for ATS")
            
        return {
            "is_ats_friendly": len(issues) == 0,
            "issues": issues
        }

    def analyze_resume(self, file_path: str) -> Dict:
        """Complete resume analysis"""
        # Read resume
        content = self.read_resume(file_path)
        
        # Initial ATS check
        ats_results = self.check_ats_compatibility(content)
        
        # Analyze each section
        analysis = {
            "overall_summary": self.analyze_section("complete content", content),
            "sections": {},
            "ats_compatibility": ats_results
        }
        
        # Analyze individual sections
        for category in self.categories:
            analysis["sections"][category] = self.analyze_section(category, content)
        
        return analysis

    def get_improvement_recommendations(self, analysis: Dict) -> List[str]:
        """Generate specific improvement recommendations"""
        recommendations = []
        
        if not analysis["ats_compatibility"]["is_ats_friendly"]:
            recommendations.extend(analysis["ats_compatibility"]["issues"])
            
        # Add section-specific recommendations
        for section, content in analysis["sections"].items():
            recommendations.append(f"{section.title()}: {content}")
            
        return recommendations

    def chat_analyze(self, prompt: str, context: Dict = None) -> str:
        """Interactive chat analysis"""
        input_text = prompt
        if context:
            input_text = f"Based on the resume context: {str(context)}\n{prompt}"
            
        input_ids = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=512,
            truncation=True
        ).input_ids.to(self.device)

        outputs = self.model.generate(
            input_ids,
            max_length=200,
            num_beams=4,
            temperature=0.7,
            no_repeat_ngram_size=2
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)