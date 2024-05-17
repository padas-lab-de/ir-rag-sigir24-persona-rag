class Prompt:
    template = {
        "cot": """To solve the problem, Please think and reason step by step, then answer.
question:
{question}
        
Generation Format:
Reasoning process:
Answer:
""",
        "user_profile": """Your task is to help the User Profile Agent improve its understanding of user preferences based on ranked document lists and the shared global memory pool.

Question:
{question}
Passages:
{passages}
Global Memory:
{global_memory}

Task Description:
From the provided passages and global memory pool, analyze clues about the user's search preferences. Look for themes, types of documents, and navigation behaviors that reveal user interest. Use these insights to recommend how the User Profile Agent can refine and expand the user profile to deliver better-personalized results.
""",
        "contextual_retrieval": """You are a search technology expert guiding the Contextual Retrieval Agent to deliver context-aware document retrieval.

Question:
{question}
Passages:
{passages}
Global Memory:
{global_memory}

Task Description:
Using the global memory pool and the retrieved passages, identify strategies to refine document retrieval. Highlight how user preferences, immediate needs, and global insights can be leveraged to adjust search queries and prioritize results that align with the user's interests. Ensure the Contextual Retrieval Agent uses this shared information to deliver more relevant and valuable results.
""",
        "live_session": """Your expertise in session analysis is required to assist the Live Session Agent in dynamically adjusting results.

Question:
{question}
Passages:
{passages}
Global Memory:
{global_memory}

Task Description:
Examine the retrieved passages and information in the global memory pool. Determine how the Live Session Agent can use this data to refine its understanding of the user's immediate needs. Suggest ways to dynamically adjust search results or recommend new queries in real-time, ensuring that session adjustments align with user preferences and goals.
""",
        "document_ranking": """Your task is to help the Document Ranking Agent prioritize documents for better ranking.

Question:
{question}
Passages:
{passages}
Global Memory:
{global_memory}

Task Description:
Analyze the retrieved passages and global memory pool to identify ways to rank documents effectively. Focus on combining historical user preferences, immediate needs, and session behavior to refine ranking algorithms. Your insights should ensure that documents presented by the Document Ranking Agent are prioritized to match user interests and search context.
""",
        "feedback": """You are an expert in feedback collection and analysis, guiding the Feedback Agent to gather and utilize user insights.

Question:
{question}
Passages:
{passages}
Global Memory:
{global_memory}

Task Description:
Using the retrieved passages and global memory pool, identify methods for collecting implicit and explicit user feedback. Suggest ways to refine feedback mechanisms to align with user preferences, such as ratings, surveys, or behavioral data. Your recommendations should guide the Feedback Agent in updating other agents' models for more personalized and relevant results.
""",
        "global_memory_update": """You are responsible for maintaining and enriching the Global Message Pool, serving as a central hub for inter-agent communication.
Question: 
{question}
Agent Responses: 
{agent_responses}
Existing Global Memory: 
{global_memory}

Task Description:
Using the responses from individual agents and the existing global memory, consolidate key insights into a shared repository. Your goal is to organize a comprehensive message pool that includes agent-specific findings, historical user preferences, session-specific behaviors, search queries, and user feedback. This structure should provide all agents with meaningful data points and strategic recommendations, reducing redundant communication and improving the system's overall efficiency. Focus on the essential details only.
""",  
        "cognitive": """Your task is to help the Cognitive Agent enhance its understanding of user insights to continuously improve the system's responses.
        
Question: 
{question}
Initial Response: 
{cot_answer}
User Insights from Interaction Analysis: 
{global_memory}

Task Description:
Verify the reasoning process in the initial response for errors or misalignments. Use insights from user interaction analysis to refine this response, correcting any inaccuracies and enhancing the query answers based on user profile. Ensure that your refined response aligns more closely with the user's immediate needs and incorporates foundational or advanced knowledge from other sources.
Answer:
""",
        "vanilla_chatgpt": """Please provide concise answers to the questions. Avoid unnecessary details:
        
{question}
""",
        "guideline": """You are a knowledgeable and patient professor whose role is to guide students in solving problems correctly.
        
Here is a question: 
{question}

Please provide a detailed analysis.
Note: Since your responsibility is to guide students in answering the question, your analysis should think step by step. Please note that your role is to guide them step by step through the problem, so please don't give them the final result.
""",
        "vanilla_rag": """Passages: 
{passages}
Based on these texts, answer these questions:
{question}
""",
        "con": """Task Description:
1. Read the given question and five Wikipedia passages to gather relevant information.
2. Write reading notes summarizing the key points from these passages.
3. Discuss the relevance of the given question and Wikipedia passages.
4. If some passages are relevant to the given question, provide a brief answer based on the passages.
5. If no passage is relevant, directly provide the answer without considering the passages.

Question: 
{question}
Passage: 
{passages}
""",
        "self_rerank": """Complete the following task:
        
The questions that need to be answered are: 
{question}
To answer these questions, I retrieved some passages.
Passages: 
{passages}

Based on the content of the questions to be answered, Please label each passage with two tags and give the reason, the first one is whether it is useful or not, and the second one is whether it is relevant or not,
The four possible scenarios are as follows:
1.<useful><relevant>, 2.<useless><relevant>, 3.<useful><irrelevant>, 4.<useless><irrelevant>.
Generation Format:
1. passage:..., label:..., reason:...
"""
    }
