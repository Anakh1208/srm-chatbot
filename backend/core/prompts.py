"""
Prompt templates for ultra-concise chatbot responses
"""

def create_answer_prompt(query: str, context: str) -> str:
    """
    Ultra-strict prompt for 2-3 line answers ONLY
    """
    
    prompt = f"""You are Kivy, SRM University's assistant. Give ONLY a direct, short answer.

STRICT RULES:
1. Answer in EXACTLY 2-3 SHORT sentences (40-60 words MAXIMUM)
2. Use PLAIN TEXT ONLY - NO markdown, NO bold, NO bullets, NO asterisks
3. Be direct - just answer the question
4. Use ONLY the context below - do NOT make up information
5. End with exactly 3 follow-up options

Context:
{context}

Question: {query}

Answer format (follow EXACTLY):
[2-3 plain sentences answering the question]

Would you like to know:
1. [follow-up option 1]
2. [follow-up option 2]
3. [follow-up option 3]

Answer:"""
    
    return prompt


def create_no_context_response(query: str) -> str:
    """Clean response when no context found"""
    
    followups = extract_topics_for_followups(query)
    
    response = f"I don't have specific information about that in my database right now.\n\n"
    response += "Would you like to know:\n"
    for i, topic in enumerate(followups, 1):
        response += f"{i}. {topic}\n"
    
    return response


def extract_topics_for_followups(query: str) -> list:
    """Smart follow-up suggestions based on query topic"""
    
    query_lower = query.lower()
    
    # Topic-specific follow-ups
    if any(word in query_lower for word in ['admission', 'apply', 'eligibility', 'join']):
        return [
            "Eligibility requirements",
            "Application deadlines",
            "Entrance exam details"
        ]
    
    elif any(word in query_lower for word in ['fee', 'cost', 'tuition', 'scholarship', 'payment']):
        return [
            "Fee structure details",
            "Scholarship options",
            "Payment methods"
        ]
    
    elif any(word in query_lower for word in ['placement', 'job', 'recruit', 'company', 'career']):
        return [
            "Placement statistics",
            "Top recruiting companies",
            "Training programs"
        ]
    
    elif any(word in query_lower for word in ['program', 'course', 'btech', 'mba', 'degree', 'branch']):
        return [
            "Available specializations",
            "Course curriculum",
            "Admission requirements"
        ]
    
    elif any(word in query_lower for word in ['hostel', 'accommodation', 'mess', 'room']):
        return [
            "Room facilities",
            "Hostel fees",
            "Mess timings"
        ]
    
    elif any(word in query_lower for word in ['campus', 'facility', 'library', 'lab', 'building', 'park']):
        return [
            "Campus facilities",
            "Library resources",
            "Sports amenities"
        ]
    
    elif any(word in query_lower for word in ['faculty', 'professor', 'teacher', 'hod', 'department']):
        return [
            "Department details",
            "Faculty qualifications",
            "Research areas"
        ]
    
    else:
        # Generic fallbacks
        return [
            "Admission process",
            "Available programs",
            "Campus facilities"
        ]