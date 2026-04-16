from main import SummarizerAgent

# 👉 Простой тестовый текст (можешь заменить на любой)
text = """
Евгений Онегин — молодой дворянин, живущий в Петербурге. Он утомлён светской жизнью и не видит в ней смысла.
Он получает наследство и уезжает в деревню, где знакомится с поэтом Ленским.

Ленский влюблён в Ольгу, а её сестра Татьяна — тихая и задумчивая девушка — влюбляется в Онегина.
Она пишет ему письмо с признанием, но Онегин отвергает её.

Позже Онегин из скуки начинает ухаживать за Ольгой, что приводит к дуэли с Ленским.
Ленский погибает.

Спустя годы Онегин встречает Татьяну в Петербурге — теперь она замужем и стала светской дамой.
Он влюбляется в неё, но она отвергает его.
"""

# 👉 Простейшее разбиение на "главы"
chapters = text.split("\n\n")

# 👉 Запуск агента
agent = SummarizerAgent()

result = agent.run(
    full_text=text,
    chapters=chapters
)

# 👉 Вывод результатов
print("\n=== SUPER SHORT ===")
print(result["super_short"])

print("\n=== SHORT ===")
print(result["short"])

print("\n=== DETAILED ===")
print(result["detailed"])

print("\n=== QUOTES ===")
for q in result["key_quotes"]:
    print("-", q)

print("\n=== CHAPTER SUMMARIES ===")
for i, ch in enumerate(result["chapter_summaries"], 1):
    print(f"{i}. {ch}")