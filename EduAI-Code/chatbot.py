from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RiskChatbot:
    def __init__(self):
        self.phrases = ["How do I know if I am at risk?", "How can I improve my engagement?",
            "I have missed assessments", "Where can I get academic support?", "What does the risk score mean?"]
        self.labels = ["risk_explanation", "engagement_advice", "assessment_support", "academic_support", "risk_score"]
        self.vectorizer = TfidfVectorizer()
        self.vectors = self.vectorizer.fit_transform(self.phrases)
        self.responses = {
            "risk_explanation": "A risk indicator is an early signal for offering support, not a final judgment about your ability or future.",
            "engagement_advice": "Try setting a weekly study plan, checking course materials regularly, and contacting your lecturer when you get stuck.",
            "assessment_support": "Check assessment instructions and deadlines, then contact your lecturer or academic advisor about missed work as soon as possible.",
            "academic_support": "Contact your lecturer, academic advisor, or university student-support services to discuss the help available to you.",
            "risk_score": "The risk score is a model estimate based on available data. It can be wrong and should be reviewed alongside the student's circumstances."}
    def respond(self, question):
        query = self.vectorizer.transform([question])
        similarities = cosine_similarity(query, self.vectors)[0]
        index = int(similarities.argmax())
        if similarities[index] < 0.08:
            return "I may not understand that question yet. Please contact your lecturer or student support office for guidance."
        return self.responses[self.labels[index]]

def run_chatbot_demo():
    bot = RiskChatbot()
    print("\nStudent support chatbot demonstration:")
    for question in ["How do I know if I am at risk?", "I have missed assessments", "Where can I get academic support?"]:
        print(f"Student: {question}\nChatbot: {bot.respond(question)}\n")

if __name__ == "__main__":
    bot = RiskChatbot()
    while True:
        question = input("Ask the chatbot (type 'exit' to stop): ")
        if question.strip().lower() in {"exit", "quit"}: break
        print(bot.respond(question))
