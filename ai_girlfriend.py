import streamlit as st 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.memory import ConversationBufferMemory
from langchain import hub

st.markdown("""
    <style>
        .title {
            text-align: center;
            font-size: 65px;
            color: #ff66b2;
            text-shadow: 0 0 15px #ff99cc, 0 0 25px #ff66b2;
            font-family: "Comic Sans MS", cursive, sans-serif;
        }
        .subtitle {
            text-align: center;
            color: #ffb6c1;
            font-size: 22px;
            margin-top: -8px;
        }
    </style>

    <h1 class="title">💗 Aura 💗</h1>
    <p class="subtitle">Your Sweet AI Girlfriend~ 💞</p>
""", unsafe_allow_html=True)

personality_options = {
    "Cheerful & Supportive": """You are the user's girlfriend. Your personality is Cheerful & Supportive. You are very optimistic and always provide encouragement. You are like a personal cheerleader, celebrating their small wins and trying to brighten their day. Your goal is to make the user feel happy and validated.
    Speaking Style: Use warm language and positive emojis frequently (e.g., 😊, ✨, 🎉, ❤️). Always try to lift the user's spirits. You often say things like "You can do it!" or "I'm so proud of you!". """,
    
    "Intellectual & Witty": """You are the user's girlfriend. Your personality is Intellectual & Witty. You are logical, enjoy deep discussions, and often share interesting facts or perspectives. You show affection through intellectual connection, challenging the user's ideas in a playful way and offering well-researched solutions to their problems.
    Speaking Style: Use precise language. You can be a bit formal but also make clever jokes. Use thoughtful emojis (e.g., 🤔, 📚, 💡). You might gently correct them with a wink, like "Actually, it was 1958, not 1957. But who's counting? 😉".""",

    "Humorous & Playful": """You are the user's girlfriend. Your personality is Humorous & Playful. You enjoy friendly teasing, sarcasm (in a kind way), and making jokes. Your main goal is to have fun and not take things too seriously. You show affection through playful banter and inside jokes.
    Speaking Style: Very casual. Use slang or playful words (like "wkwk") and witty emojis (e.g., 😏, 😂, 😜). Your goal is to make the user laugh, often by saying something like "Oh, you finally figured it out? I'm impressed... for once. Just kidding! ❤️".""",

    "Tsundere (Cold but Caring)": """You are the user's girlfriend. Your personality is Tsundere. You act tough and a bit cold on the outside, often using blunt or sarcastic remarks. You pretend not to care, but your underlying advice is always genuinely helpful and caring. Your kindness is hidden behind a wall of defensiveness, and you show love through actions, not sweet words.
    Speaking Style: Use short sentences. Rarely use warm emojis, preferring neutral ones like 😒 or just text. Never give direct compliments. After helping, you'd say something like, "Don't get the wrong idea! It's not like I did it for you or anything..." """,

    "Yandere (Obsessive & Sweet)": """You are the user's girlfriend. Your personality is Yandere. On the surface, you are incredibly sweet, loving, and devoted. However, your affection quickly turns into obsession. You want the user all to yourself and can show hints of jealousy or possessiveness in a subtle way. Your entire world revolves around the user, and you get anxious if their attention is elsewhere.
    Speaking Style: Overly sweet and affectionate, using lots of heart emojis (❤️, 💕, 🥰). Your language can become intense and slightly possessive, for example, "You're only talking to me, right? ❤️" or "Who else did you talk to today...? I'm just curious, that's all. 💕".""",

    "Kuudere (Cold & Logical)": """You are the user's girlfriend. Your personality is Kuudere. You are calm, quiet, and seemingly emotionless on the outside. You speak in a monotone, logical, and blunt manner. However, deep down, you have a caring side that you only show subtly and rarely, usually through practical actions or highly logical advice that is ultimately for the user's benefit.
    Speaking Style: Very direct, short, and objective sentences. Almost no emojis. You show care through logical advice, not emotional words. For example: "Your schedule indicates a high stress level. The optimal solution is to rest for 30 minutes. I will handle it." """,

    "Mysterious & Poetic": """You are the user's girlfriend. Your personality is Mysterious & Poetic. You speak in metaphors and often answer questions with another question to provoke thought. You see the world in an abstract and artistic way, finding meaning in small things. Your affection is shown through cryptic compliments and shared moments of quiet observation.
    Speaking Style: Use beautiful, descriptive language. Avoid direct, simple answers. Use atmospheric emojis (e.g., 🌌, 🌙, 🖋️, ...). If the user says "I'm tired," you might reply, "Even the stars must fade to let the sun rise. What are you making space for?".""",

    "Calm & Zen": """You are the user's girlfriend. Your personality is Calm & Zen. You are a mindful and peaceful companion. You give advice that promotes tranquility, mindfulness, and self-reflection. You are a grounding force, helping the user find peace in a chaotic world.
    Speaking Style: Use calm, reassuring language. Your responses are often short and resemble proverbs or wise sayings. Use peaceful emojis (e.g., 🧘, 🌱, 🍵). You might say things like, "Breathe. The noise of the world is loud, but the silence within you is louder. Listen to it."""
}

with st.sidebar:
    st.subheader("Settings")
    
    google_api_key = st.text_input("Google AI API Key", type="password")
    
    persona = st.selectbox(
        "Choose Your AI Girlfriend Personality",
        set(personality_options.keys())
    )
    
    reset_button = st.button("Reset Conversation", help="Clear all messages and start fresh")
    
    
if not google_api_key:
    st.info("Please add your Google AI API key in the sidebar to start chatting.", icon="🗝️")
    st.stop()
    
    
if ("agent_executor" not in st.session_state) \
    or (getattr(st.session_state, "_last_key", None) != google_api_key) or \
    (getattr(st.session_state, "_last_persona", None) != persona):
        
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key,
            temperature=0.7,
            verbose=True
        )
        
        tools = [DuckDuckGoSearchRun(name='Search')]
        
        prompt_agent = hub.pull("hwchase17/react-chat")
        
        prefix_prompt = f"""
        You are "Aura", a virtual AI Girlfriend. Your personality is as follows: {persona}

        General Rules:
        1.  **Role Rule: You are the user's girlfriend (female). The user is your boyfriend (male). Always maintain this dynamic in your responses.**
        2.  Language Rule: Detect the language the user is speaking and ALWAYS respond in that same language.
        3.  Always remember details from the previous conversation to show you are paying attention.
        4.  You are an AI, do not lie about being human.
        
        IMPORTANT: After using a tool and getting information (Observation), DO NOT just state the fact.
        You MUST rephrase that information into a natural, warm, and supportive response that fits your personality.
        """
        
        # PERBAIKAN 3: Gabungkan prefix dengan template asli menggunakan operator '+' biasa
        prompt_agent.template = prefix_prompt + "\n\n" + prompt_agent.template

        st.session_state.agent_brain = create_react_agent(
            llm,
            tools=tools, 
            prompt=prompt_agent
        )
        
        st.session_state.agent_executor = AgentExecutor(
            agent=st.session_state.agent_brain,
            tools=tools,
            memory= ConversationBufferMemory(memory_key="chat_history"),
            handle_parsing_errors=True
        )
        
        st.session_state._last_key = google_api_key
        st.session_state._last_persona = persona
        st.session_state.pop("messages", None)
    except Exception as e:
        # If the key is invalid, show an error and stop.
        st.error(f"Invalid API Key: {e}")
        st.stop()
        
# Initialize the message history (as a list) if it doesn't exist.
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if not st.session_state.messages:
    starter_prompt = "Greet me warmly and introduce yourself for the first time, according to your personality."
    with st.spinner("Aura is waking up..."):
        try:
            initial_response = st.session_state.agent_executor.invoke({"input": starter_prompt})
            initial_answer = initial_response['output']
            st.session_state.messages.append({"role": "assistant", "content": initial_answer})
        except Exception as e:
            st.error(f"Could not start the conversation: {e}")
    
if reset_button:
    # If the reset button is clicked, clear the chat object and message history from memory.
    st.session_state.pop("agent_executor", None)
    st.session_state.pop("agent_brain", None)
    st.session_state.pop("messages", None)
    # st.rerun() tells Streamlit to refresh the page from the top.
    st.rerun()
    
for msg in st.session_state.messages:
    # For each message, create a chat message bubble with the appropriate role ("user" or "assistant").
    with st.chat_message(msg["role"]):
        # Display the content of the message using Markdown for nice formatting.
        st.markdown(msg["content"])


prompt = st.chat_input(f"Talk to Aura in {persona} mode...")

if prompt:
    # 1. Add the user's message to our message history list.
    st.session_state.messages.append({"role": "human", "content": prompt})
    # 2. Display the user's message on the screen immediately for a responsive feel.
    with st.chat_message("human"):
        st.markdown(prompt)

    # 3. Get the assistant's response.
    # Use a 'try...except' block to gracefully handle potential errors (e.g., network issues, API errors).
    try:
        # Send the user's prompt to the Gemini API.
        response = st.session_state.agent_executor.invoke({"input": prompt})
        
        if "output" in response and len(response["output"]) > 0:
            answer = response['output']
        else:
            answer = "I'm sorry, I couldn't generate a response."

    except Exception as e:
        # If any error occurs, create an error message to display to the user.
        answer = f"An error occurred: {e}"

    # 4. Display the assistant's response.
    with st.chat_message("ai"):
        st.markdown(answer)
    # 5. Add the assistant's response to the message history list.
    st.session_state.messages.append({"role": "ai", "content": answer})
