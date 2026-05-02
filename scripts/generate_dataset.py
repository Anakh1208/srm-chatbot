import csv
import random

courses = [
    "Computer Science Engineering", "Mechanical Engineering", "Civil Engineering",
    "Electrical Engineering", "Electronics Engineering", "MBBS", "B.Sc Nursing",
    "BA LLB", "BBA", "MBA", "BA English", "B.Com", "Biotechnology"
]

facilities = [
    "library", "hostel", "sports complex", "cafeteria",
    "Wi-Fi", "research labs", "hospital", "gym", "auditorium"
]

placements = [
    "TCS", "Infosys", "Wipro", "Amazon", "Microsoft", "Cognizant"
]

questions_templates = [
    "What is {topic}?",
    "Tell me about {topic}",
    "Do you offer {topic}?",
    "Can you explain {topic}?",
    "What are the details of {topic}?"
]

answers_templates = [
    "{topic} is available at the university with modern facilities and experienced faculty.",
    "The university provides excellent support for {topic} including infrastructure and training.",
    "{topic} is one of the key offerings with strong academic and practical exposure.",
    "Students can pursue {topic} with access to industry-level resources.",
]

def generate_dataset(output_file, num_rows=250):
    data = []

    all_topics = courses + facilities + placements + [
        "admissions", "scholarships", "placements", "campus life",
        "internships", "research opportunities", "hostel facilities"
    ]

    for i in range(num_rows):
        topic = random.choice(all_topics)

        question = random.choice(questions_templates).format(topic=topic)
        answer = random.choice(answers_templates).format(topic=topic)

        data.append([question, answer])

    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Question", "Answer"])
        writer.writerows(data)

    print(f"✅ Generated {num_rows} QA pairs in {output_file}")

if __name__ == "__main__":
    generate_dataset("data/university_faq_generated.csv", 250)