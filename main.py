from llm_module import ResumeAnalyzer
import os

def print_menu():
    print("\n=== Resume Analysis Menu ===")
    print("1. Analyze Resume")
    print("2. Chat About Resume")
    print("3. Get ATS Recommendations")
    print("4. Exit")
    return input("\nSelect an option (1-4): ")

def analyze_resume_file(analyzer):
    file_path = input("\nEnter resume file path (PDF/DOCX): ")
    if not os.path.exists(file_path):
        print("File not found!")
        return None
        
    print("\nAnalyzing resume...")
    analysis = analyzer.analyze_resume(file_path)
    
    print("\n=== Analysis Results ===")
    print("\nOverall Summary:")
    print(analysis["overall_summary"])
    
    print("\nATS Compatibility:")
    print("Status:", "✓ ATS Friendly" if analysis["ats_compatibility"]["is_ats_friendly"] else "⚠ ATS Issues Found")
    if analysis["ats_compatibility"]["issues"]:
        print("Issues found:")
        for issue in analysis["ats_compatibility"]["issues"]:
            print(f"- {issue}")
            
    print("\nDetailed Analysis:")
    for section, content in analysis["sections"].items():
        print(f"\n{section.title()}:")
        print(content)
        
    return analysis

def chat_mode(analyzer, context=None):
    print("\n=== Chat Mode ===")
    print("Ask questions about your resume or get specific advice")
    print("Type 'quit' to return to menu")
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'quit':
            break
            
        response = analyzer.chat_analyze(user_input, context)
        print(f"\nAssistant: {response}")

def main():
    print("Initializing Resume Analyzer...")
    analyzer = ResumeAnalyzer()
    context = None
    
    while True:
        choice = print_menu()
        
        if choice == '1':
            context = analyze_resume_file(analyzer)
        elif choice == '2':
            chat_mode(analyzer, context)
        elif choice == '3':
            if context:
                recommendations = analyzer.get_improvement_recommendations(context)
                print("\n=== ATS Recommendations ===")
                for i, rec in enumerate(recommendations, 1):
                    print(f"\n{i}. {rec}")
            else:
                print("\nPlease analyze a resume first (Option 1)")
        elif choice == '4':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid option!")

if __name__ == "__main__":
    main()