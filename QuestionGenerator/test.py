from main import QuestionGeneratorAgent

text = """
Онегин отвергает Татьяну. Позже он убивает Ленского на дуэли.
Спустя годы он снова встречает Татьяну, но она уже замужем.
"""

chapters = text.split("\n")

agent = QuestionGeneratorAgent(num_questions=5)

result = agent.run(
    full_text=text,
    chapters=chapters
)

for q in result["questions"]:
    print("\n---")
    print("Вопрос:", q["text"])
    print("Сложность:", q["difficulty"])
    for opt in q["options"]:
        print(opt)
    print("Ответ:", q["correct_answer"])
    print("Цитата:", q["quote_evidence"])