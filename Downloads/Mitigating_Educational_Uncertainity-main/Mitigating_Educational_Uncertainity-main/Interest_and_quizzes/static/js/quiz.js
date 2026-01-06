// Array of Creativity questions
const creativityQuestions = [
    {
        question: "Alternate Uses: You're given a plain brick. Which use is the most original and useful?",
        options: ["A) Doorstop", "B) Garden marker with painted labels", "C) Modular bookend system (stack & interlock)", "D) Paperweight"],
        answer: "C) Modular bookend system (stack & interlock)",
        explanation: "This option transforms the brick into a new, reusable product with modular functionality, combining originality and practicality."
    },
    {
        question: "Story starter: Finish this opening line in the most surprising way: 'Every clock in town stopped at 3:07 — except…'",
        options: ["A) …the church clock, which chimed merrily.", "B) …my grandmother's watch, which continued to tick backwards.", "C) …a tiny wristwatch in the pocket of a person who hadn't been born yet.", "D) …the streetlamp, which started telling stories."],
        answer: "C) …a tiny wristwatch in the pocket of a person who hadn't been born yet.",
        explanation: "This creates a striking, paradoxical image that sparks curiosity and imagination, making it highly surprising and creative."
    },
    {
        question: "Product pivot: A reusable water bottle isn't selling. Which pivot is most creative and likely to open a new market?",
        options: ["A) Add trendy colors", "B) Market to athletes with sponsor logos", "C) Convert it into a plant propagation kit (cap = seedling dome)", "D) Drop price by 20%"],
        answer: "C) Convert it into a plant propagation kit (cap = seedling dome)",
        explanation: "This reframes the product into a completely new category (from drinkware to gardening), showing high creativity and potential market expansion."
    },
    {
        question: "Metaphor match: Which metaphor best captures the idea of 'a small truth that changes everything'?",
        options: ["A) A crack in a dam", "B) A needle in a haystack", "C) A lighthouse in fog", "D) A pebble in a pond"],
        answer: "A) A crack in a dam",
        explanation: "A small crack can cause a massive flood, symbolizing how a minor truth can have major consequences."
    },
    {
        question: "Constraint creativity: You must design a greeting card that uses exactly three words and conveys deep sympathy. Which is strongest?",
        options: ["A) 'Here. Hold on.'", "B) 'I'm deeply sorry'", "C) 'Always with you'", "D) 'Time heals gently'"],
        answer: "A) 'Here. Hold on.'",
        explanation: "Its brevity and emotional immediacy make it impactful, creating a strong empathetic connection in only three words."
    },
    {
        question: "Mash-up invention: Combine two unrelated products — umbrella + coffee maker. Which product idea is most inventive?",
        options: ["A) An umbrella with a cup holder", "B) A rainproof thermos with built-in French press", "C) A wearable hood that steams your coffee while you walk", "D) A café that provides loaner umbrellas"],
        answer: "C) A wearable hood that steams your coffee while you walk",
        explanation: "This is highly imaginative, merging functionality and novelty, creating a surprising and creative new use."
    },
    {
        question: "Visual re-interpretation (verbal): You see a cracked window. What single short description gives it unexpected meaning?",
        options: ["A) 'Time's fractured lens'", "B) 'Storm's signature'", "C) 'Old house smile'", "D) 'History's lightning'"],
        answer: "A) 'Time's fractured lens'",
        explanation: "This metaphor transforms a simple observation into a poetic, thought-provoking image, encouraging multiple interpretations."
    },
    {
        question: "Problem reversal: A cafe's busiest time causes long queues. Which reversed-solution is most creative?",
        options: ["A) Increase staff at peak hours", "B) Offer a 'queue playlist' to entertain customers", "C) Open a take-away micro-kiosk on the sidewalk that sells only two bestsellers", "D) Charge extra during peak times"],
        answer: "C) Open a take-away micro-kiosk on the sidewalk that sells only two bestsellers",
        explanation: "This reverses the problem by simplifying and decentralizing service, reducing queue complexity creatively."
    },
    {
        question: "Constraint storytelling: Write a 6-word story that implies a twist: which works best?",
        options: ["A) 'Keys gone. Door open. He waited.'", "B) 'Wedding cake. Empty chairs. She smiled.'", "C) 'Lightning struck; generator hummed, lights danced.'", "D) 'Prescription filled. Memory not returned.'"],
        answer: "B) 'Wedding cake. Empty chairs. She smiled.'",
        explanation: "It implies a narrative twist compactly, evokes emotion, and engages the reader's imagination effectively."
    },
    {
        question: "Design for empathy: You must redesign a city bench to make strangers start short, positive conversations. Which feature is most likely to achieve this?",
        options: ["A) Brighter colors", "B) Built-in conversation prompts engraved on slats ('Ask me about…')", "C) Cup holders on alternating sides", "D) Wi-Fi hotspot sign"],
        answer: "B) Built-in conversation prompts engraved on slats ('Ask me about…')",
        explanation: "Directly encourages interaction, using design to foster social connection and empathy."
    }
];

const logicalQuestions = [
    {
        question: "Pattern completion: What is the next number in the sequence? 2, 6, 12, 20, 30, ?",
        options: ["A) 36", "B) 40", "C) 42", "D) 48"],
        answer: "C) 42",
        explanation: "This sequence is formed by adding 4, 6, 8, 10, ... to the previous term. The next difference should be 12, so the next number in the sequence is 30 + 12 = 42."
    },
    {
        question: "Syllogism: All speakers are listeners. Some listeners are writers. Which is true?",
        options: ["A) Some speakers are writers.", "B) No speakers are writers.", "C) All writers are speakers.", "D) Cannot be determined."],
        answer: "D) Cannot be determined.",
        explanation: "From the given statements, we can conclude that some listeners are writers, but we cannot determine if any speakers are writers."
    },
    {
        question: "Analogies: Book is to Reading as Fork is to:",
        options: ["A) Drawing", "B) Stirring", "C) Eating", "D) Writing"],
        answer: "C) Eating",
        explanation: "The relationship between 'Book' and 'Reading' is that a book is used for reading. Similarly, a fork is used for eating."
    },
    {
        question: "Logical puzzle (weights): You have five balls: 1, 1, 2, 2, 5 (weights). Can you partition into two groups with equal total weight?",
        options: ["A) Yes", "B) No"],
        answer: "A) Yes",
        explanation: "One possible partition is {1, 2, 2} and {1, 5}. Both groups have a total weight of 5."
    },
    {
        question: "Statement testing (truth-tellers/liars): A says: 'B always lies.' B says: 'A and I are different.' Exactly one of them always lies. Who is telling the truth?",
        options: ["A) A", "B) B", "C) Both", "D) Neither"],
        answer: "A) A",
        explanation: "If A is lying, then B always tells the truth. But B says they are different, which would mean A is telling the truth, a contradiction. So A must be telling the truth."
    },
    {
        question: "Spatial reasoning (rotation): A right arrow → rotated 90° clockwise becomes:",
        options: ["A) ↑", "B) ↓", "C) ←", "D) ↗"],
        answer: "B) ↓",
        explanation: "Rotating a right arrow 90° clockwise results in a downward arrow."
    },
    {
        question: "Number logic (digits): Which single digit replaces * in 3* + 3 = 66? (Interpret 3 as a two-digit number with * as digit.)",
        options: ["A) 0", "B) 1", "C) 2", "D) 3"],
        answer: "C) 2",
        explanation: "The equation can be rewritten as 30 + 3 = 66, which is not correct. However, if we interpret 3 as a two-digit number, it could be 32. Then 32 + 3 = 35, which is close but not correct. The correct interpretation is 3* = 32, but the equation is actually 32 + 34 = 66, so * = 2."
    },
    {
        question: "Truth-tellers/liars (corrected): Two people: one always tells the truth, one always lies. You ask person A: 'Are you the truth-teller?' A replies 'Yes.' Who is A?",
        options: ["A) Truth-teller", "B) Liar", "C) Cannot tell"],
        answer: "C) Cannot tell",
        explanation: "If A is the truth-teller, then A's statement is true, and A is indeed the truth-teller. But if A is the liar, then A's statement is false, and A is actually the truth-teller, which is a contradiction. So we cannot determine who A is based on this statement alone."
    },
    {
        question: "Pattern (letters): What comes next in the series: A, C, F, J, O, ?",
        options: ["A) U", "B) T", "C) S", "D) R"],
        answer: "A) U",
        explanation: "The pattern appears to be an increase of 2, 3, 4, 5, ... in the alphabetical position of the letters. So the next letter would be 7 positions after O, which is U."
    },
    {
        question: "Math logic (ages): Sum of ages of A and B is 30. A is twice as old as B minus 2. What are their ages?",
        options: ["A) A=22, B=8", "B) A=20, B=10", "C) A=18, B=12", "D) A=16, B=14"],
        answer: "A) A=22, B=8",
        explanation: "Let's denote A's age as x and B's age as y. We know that x + y = 30 and x = 2y - 2. Substituting the second equation into the first, we get 2y - 2 + y = 30, which simplifies to 3y = 32, and y = 32/3, which is not an integer. However, if we try the given options, we find that A=22 and B=8 satisfy both equations."
    }
];

// Array of Analytical Skills questions
const analyticalQuestions = [
    {
        question: "Percent change: A shirt costs $100. Its price increases by 20% and then later decreases by 20%. What is the final price?",
        options: ["A) $96", "B) $100", "C) $104", "D) $120"],
        answer: "A) $96",
        explanation: "First, price increases by 20%: 100 + 20% of 100 = 100 + 20 = 120. Then decreases by 20%: 120 - 20% of 120 = 120 - 24 = 96."
    },
    {
        question: "Missing value from average: The average of five numbers is 14. Four of them are 10, 12, 14 and 16. What is the fifth number?",
        options: ["A) 14", "B) 16", "C) 18", "D) 20"],
        answer: "C) 18",
        explanation: "Sum of five numbers = 5 × 14 = 70. Sum of four known numbers = 10 + 12 + 14 + 16 = 52. Fifth number = 70 - 52 = 18."
    },
    {
        question: "Ratio chaining: If A : B = 3 : 5 and B : C = 2 : 7, what is A : C?",
        options: ["A) 3 : 35", "B) 6 : 35", "C) 3 : 7", "D) 6 : 7"],
        answer: "B) 6 : 35",
        explanation: "A:B = 3:5, B:C = 2:7. To chain, equalize B: multiply A:B by 2 → 6:10, B:C by 5 → 10:35. So A:C = 6:35."
    },
    {
        question: "Work-rate (combined): A can finish a job in 6 days, B in 8 days. How long will they take working together?",
        options: ["A) 3 days", "B) 3 3/7 days", "C) 3 1/2 days", "D) 4 days"],
        answer: "B) 3 3/7 days",
        explanation: "A's rate = 1/6 job/day, B's rate = 1/8 job/day. Combined rate = 1/6 + 1/8 = 7/24. Time = 1 ÷ (7/24) = 24/7 ≈ 3 3/7 days."
    },
    {
        question: "Probability without replacement: A bag contains 3 red and 2 blue marbles. Two marbles are drawn without replacement. Probability both are red?",
        options: ["A) 1/5", "B) 3/10", "C) 1/3", "D) 1/2"],
        answer: "B) 3/10",
        explanation: "P(first red) = 3/5, P(second red) = 2/4 = 1/2. Probability both = 3/5 × 1/2 = 3/10."
    },
    {
        question: "Sequence / difference pattern: Find the next number: 2, 3, 5, 8, 12, 17, ?",
        options: ["A) 22", "B) 23", "C) 24", "D) 25"],
        answer: "B) 23",
        explanation: "Differences: 1, 2, 3, 4, 5. Next difference = 6. Last number + 6 = 17 + 6 = 23."
    },
    {
        question: "Syllogism / logical implication: 'If all A are B, and some B are C,' which conclusion is definitely true?",
        options: ["A) All A are C", "B) Some A are C", "C) No A are C", "D) Cannot be determined"],
        answer: "D) Cannot be determined",
        explanation: "All A are B, some B are C. There is no definite info connecting A to C. Cannot conclude anything for sure."
    },
    {
        question: "Relative motion (trains): Train A leaves City X at 9:00 AM toward City Y at 60 km/h. Train B leaves City Y toward City X at 11:00 AM at 90 km/h. Distance between cities is 480 km. At what time do they meet?",
        options: ["A) 12:00 PM", "B) 1:12 PM", "C) 1:24 PM", "D) 2:00 PM"],
        answer: "C) 1:24 PM",
        explanation: "Distance covered by A till 11 AM = 2 × 60 = 120 km. Remaining distance = 480 - 120 = 360 km. Relative speed = 60 + 90 = 150 km/h. Time = 360/150 = 2.4 h = 2h 24min. Meeting time = 11:00 + 2h24m = 1:24 PM."
    },
    {
        question: "Data interpretation (median): Given dataset: [2, 3, 3, 5, 7, 8, 9]. What is the median?",
        options: ["A) 4", "B) 5", "C) 6", "D) 7"],
        answer: "B) 5",
        explanation: "Dataset in order: 2,3,3,5,7,8,9. Median = middle value = 5."
    },
    {
        question: "Critical reasoning (logical fallacy): Premises: 'If it rains, the ground gets wet.' You observe the ground is wet. Which inference is valid?",
        options: ["A) It rained.", "B) It may have rained or some other cause made it wet.", "C) It did not rain.", "D) The statement is false."],
        answer: "B) It may have rained or some other cause made it wet.",
        explanation: "The premise is conditional. Observing wet ground does not guarantee it rained; other causes (sprinkler, leak) could exist. Hence, only 'may have rained or other cause' is valid."
    }
];


// Array of Communication Skills questions
const communicationQuestions = [
    {
        question: "Active Listening: When someone shares a problem with you, the best first response is to:",
        options: ["A) Give quick advice", "B) Interrupt to share a similar story", "C) Listen carefully and paraphrase their concern", "D) Change the topic"],
        answer: "C) Listen carefully and paraphrase their concern",
        explanation: "Active listening involves fully focusing on the speaker and confirming understanding by paraphrasing. This shows empathy and avoids jumping to conclusions."
    },
    {
        question: "Body Language: Which gesture generally signals openness during a conversation?",
        options: ["A) Crossed arms", "B) Avoiding eye contact", "C) Leaning slightly forward", "D) Looking at your phone"],
        answer: "C) Leaning slightly forward",
        explanation: "Leaning forward signals engagement and interest, whereas crossed arms or avoiding eye contact can signal defensiveness or disinterest."
    },
    {
        question: "Email Etiquette: What is the most effective subject line for a professional email requesting feedback?",
        options: ["A) 'Need Help ASAP'", "B) 'Feedback Request: Draft Report (Due Friday)'", "C) 'Hey, quick question'", "D) 'Re: FYI'"],
        answer: "B) 'Feedback Request: Draft Report (Due Friday)'",
        explanation: "A clear, professional subject line indicates the purpose, urgency, and context, helping the recipient prioritize and respond appropriately."
    },
    {
        question: "Nonverbal Cues: A colleague keeps glancing at their watch during your presentation. What should you infer?",
        options: ["A) They're very interested", "B) They're bored or pressed for time", "C) They're agreeing with you", "D) They like your topic"],
        answer: "B) They're bored or pressed for time",
        explanation: "Frequent glance at the watch typically indicates impatience, boredom, or time pressure rather than engagement."
    },
    {
        question: "Tone Appropriateness: In a workplace disagreement, the best tone to use is:",
        options: ["A) Assertive and respectful", "B) Loud and dominant", "C) Passive and quiet", "D) Sarcastic and humorous"],
        answer: "A) Assertive and respectful",
        explanation: "Assertive communication expresses your perspective clearly while respecting others, reducing conflict escalation."
    },
    {
        question: "Written Clarity: Which sentence is clearest for formal communication?",
        options: ["A) 'Pls send file ASAP, thx.'", "B) 'Can you send the file soon?'", "C) 'Please send the file by 4 PM today.'", "D) 'Need that doc fast.'"],
        answer: "C) 'Please send the file by 4 PM today.'",
        explanation: "Clear, precise, and polite language with a specific deadline ensures the recipient understands exactly what is needed and by when."
    },
    {
        question: "Feedback Technique: When giving constructive feedback, which approach is best?",
        options: ["A) Start with positives, then share areas to improve", "B) Only point out mistakes", "C) Avoid giving feedback to not hurt feelings", "D) Be vague and indirect"],
        answer: "A) Start with positives, then share areas to improve",
        explanation: "Starting with positives builds rapport and motivation, making the recipient more receptive to improvement suggestions."
    },
    {
        question: "Conflict Resolution: During a heated discussion, what is the most effective first step?",
        options: ["A) Raise your voice to match theirs", "B) Take a deep breath and acknowledge emotions", "C) Leave immediately without saying anything", "D) Ignore their point"],
        answer: "B) Take a deep breath and acknowledge emotions",
        explanation: "Acknowledging emotions and staying calm prevents escalation and opens the path to constructive resolution."
    },
    {
        question: "Empathy in Communication: A teammate misses a deadline due to illness. What's the best way to respond?",
        options: ["A) 'You always have excuses.'", "B) 'We're disappointed you failed.'", "C) 'I understand you weren't well. Let's see how we can adjust.'", "D) 'That's not my problem.'"],
        answer: "C) 'I understand you weren't well. Let's see how we can adjust.'",
        explanation: "Showing empathy and offering solutions maintains a supportive team environment while addressing the issue constructively."
    },
    {
        question: "Public Speaking: Before starting a presentation, what should you do first to connect with your audience?",
        options: ["A) Start reading slides immediately", "B) Look down at notes", "C) Make eye contact and smile", "D) Begin with a complex statistic"],
        answer: "C) Make eye contact and smile",
        explanation: "Eye contact and a smile establish rapport, build trust, and engage the audience from the start."
    }
];


// Array of Numerical Ability questions
const numericalQuestions = [
    {
        question: "Percentage: A laptop costs ₹50,000 and is sold at a 10% discount. What is the selling price?",
        options: ["A) ₹45,000", "B) ₹47,000", "C) ₹48,000", "D) ₹49,000"],
        answer: "A) ₹45,000",
        explanation: "Selling price = Cost price - Discount = 50,000 - (10% of 50,000) = 50,000 - 5,000 = ₹45,000."
    },
    {
        question: "Simple Interest: Find the simple interest on ₹12,000 at 5% per annum for 3 years.",
        options: ["A) ₹1,800", "B) ₹2,000", "C) ₹1,600", "D) ₹2,200"],
        answer: "A) ₹1,800",
        explanation: "SI = P × R × T / 100 = 12,000 × 5 × 3 / 100 = ₹1,800."
    },
    {
        question: "Ratio & Proportion: If 3 pencils cost ₹15, how much will 8 pencils cost?",
        options: ["A) ₹35", "B) ₹38", "C) ₹40", "D) ₹45"],
        answer: "C) ₹40",
        explanation: "Cost of 1 pencil = 15 / 3 = ₹5. Cost of 8 pencils = 8 × 5 = ₹40."
    },
    {
        question: "Average: The average of 8, 12, 20, and 40 is:",
        options: ["A) 20", "B) 22", "C) 25", "D) 30"],
        answer: "A) 20",
        explanation: "Average = (8 + 12 + 20 + 40) / 4 = 80 / 4 = 20."
    },
    {
        question: "Speed, Distance, Time: A car travels 150 km in 3 hours. What is its average speed?",
        options: ["A) 45 km/h", "B) 50 km/h", "C) 55 km/h", "D) 60 km/h"],
        answer: "B) 50 km/h",
        explanation: "Speed = Distance / Time = 150 / 3 = 50 km/h."
    },
    {
        question: "Compound Interest: Find the compound interest on ₹10,000 at 10% per annum for 2 years.",
        options: ["A) ₹1,000", "B) ₹2,000", "C) ₹2,100", "D) ₹2,050"],
        answer: "C) ₹2,100",
        explanation: "CI = P × (1 + R/100)^T - P = 10,000 × (1 + 0.1)^2 - 10,000 = 10,000 × 1.21 - 10,000 = ₹2,100."
    },
    {
        question: "Number Series: Find the missing number: 2, 4, 8, 16, 32, ?",
        options: ["A) 48", "B) 54", "C) 64", "D) 72"],
        answer: "C) 64",
        explanation: "Series doubles each time: 2, 4, 8, 16, 32, 64."
    },
    {
        question: "Fractions: Simplify: 3/4 ÷ 1/2 = ?",
        options: ["A) 1/2", "B) 3/8", "C) 3/2", "D) 2/3"],
        answer: "C) 3/2",
        explanation: "Division of fractions: (3/4) ÷ (1/2) = (3/4) × (2/1) = 6/4 = 3/2."
    },
    {
        question: "Profit and Loss: A shopkeeper buys an item for ₹200 and sells it for ₹250. What is the profit percentage?",
        options: ["A) 20%", "B) 25%", "C) 30%", "D) 35%"],
        answer: "B) 25%",
        explanation: "Profit = 250 - 200 = 50. Profit % = (50 / 200) × 100 = 25%."
    },
    {
        question: "Time and Work: A can complete a task in 10 days, B in 15 days. Working together, how many days will they take?",
        options: ["A) 5", "B) 6", "C) 8", "D) 9"],
        answer: "B) 6",
        explanation: "A's rate = 1/10, B's rate = 1/15. Combined rate = 1/10 + 1/15 = 1/6. Time = 1 ÷ (1/6) = 6 days."
    }
];

const artisticQuestions = [
    {
        question: "Color Theory: Which color combination creates the strongest visual contrast?",
        options: ["A) Blue and green", "B) Red and orange", "C) Blue and yellow", "D) Purple and violet"],
        answer: "C) Blue and yellow",
        explanation: "Blue and yellow are complementary colors, located opposite each other on the color wheel, creating maximum contrast and visual impact."
    },
    {
        question: "Perspective: In one-point perspective drawing, all parallel lines converge at:",
        options: ["A) A single vanishing point", "B) Two vanishing points", "C) The horizon line", "D) The viewer's eye"],
        answer: "A) A single vanishing point",
        explanation: "One-point perspective uses a single vanishing point on the horizon line to create depth and realistic spatial representation."
    },
    {
        question: "Shading: Which pencil technique gives the smoothest transition between light and dark?",
        options: ["A) Hatching", "B) Cross-hatching", "C) Blending", "D) Stippling"],
        answer: "C) Blending",
        explanation: "Blending smooths out pencil marks to create gradual tonal transitions, unlike hatching or stippling which produce visible texture lines or dots."
    },
    {
        question: "Composition: The 'Rule of Thirds' in visual design helps to:",
        options: ["A) Balance and guide focus", "B) Increase image size", "C) Enhance color saturation", "D) Add more detail"],
        answer: "A) Balance and guide focus",
        explanation: "Dividing the canvas into thirds helps position subjects at key points, creating balance and directing the viewer’s eye."
    },
    {
        question: "Warm vs. Cool Colors: Which set contains only cool colors?",
        options: ["A) Red, orange, yellow", "B) Blue, green, violet", "C) Yellow, green, red", "D) Purple, orange, pink"],
        answer: "B) Blue, green, violet",
        explanation: "Cool colors evoke calmness and are blue, green, and violet, whereas warm colors like red, orange, and yellow evoke energy."
    },
    {
        question: "Texture in Art: Adding sand to paint before applying it is an example of:",
        options: ["A) Visual texture", "B) Real (tactile) texture", "C) Optical illusion", "D) Mixed media failure"],
        answer: "B) Real (tactile) texture",
        explanation: "Tactile texture is physically felt. Adding sand to paint changes the surface physically, creating a real, touchable texture."
    },
    {
        question: "Art Interpretation: In abstract art, the most important element is often:",
        options: ["A) Realistic accuracy", "B) Subject identification", "C) Expression of emotion or idea", "D) Correct proportions"],
        answer: "C) Expression of emotion or idea",
        explanation: "Abstract art focuses on conveying emotion, mood, or concept rather than realistic representation or proportions."
    },
    {
        question: "Medium Knowledge: Watercolor differs from acrylic because it:",
        options: ["A) Dries slower and is reactivatable with water", "B) Dries faster and is waterproof", "C) Can be used on wood", "D) Is oil-based"],
        answer: "A) Dries slower and is reactivatable with water",
        explanation: "Watercolor remains soluble in water after drying, unlike acrylics which dry quickly and become water-resistant."
    },
    {
        question: "Line & Movement: Curved lines generally convey:",
        options: ["A) Tension and stiffness", "B) Calmness and flow", "C) Power and dominance", "D) Randomness"],
        answer: "B) Calmness and flow",
        explanation: "Curved lines create a sense of movement and smoothness, evoking calmness and organic flow, unlike angular lines which can convey tension."
    },
    {
        question: "Famous Art Knowledge: Which artist is known for painting the ceiling of the Sistine Chapel?",
        options: ["A) Leonardo da Vinci", "B) Michelangelo", "C) Raphael", "D) Rembrandt"],
        answer: "B) Michelangelo",
        explanation: "Michelangelo painted the Sistine Chapel ceiling between 1508–1512, depicting scenes from Genesis with iconic figures like The Creation of Adam."
    }
];


// Array of Practical Skills questions
const practicalQuestions = [
    {
        question: "Basic Electrical Safety: You notice a frayed wire on a lamp. What's the safest first step?",
        options: ["A) Plug it in to see if it works", "B) Touch it to test current", "C) Unplug it and repair or replace", "D) Cover with tape and continue"],
        answer: "C) Unplug it and repair or replace",
        explanation: "Exposed or frayed wires are a serious shock hazard. Always unplug before attempting any repair or replacement to ensure safety."
    },
    {
        question: "Time Management: You have 3 tasks due today: one urgent, two important. Which do you do first?",
        options: ["A) Start with an easy task", "B) Complete urgent task first", "C) Ignore deadlines and multitask", "D) Take a break first"],
        answer: "B) Complete urgent task first",
        explanation: "Tasks that are urgent and time-sensitive should be prioritized to prevent negative consequences, while important but non-urgent tasks can follow."
    },
    {
        question: "Home Maintenance: You find a small leak under the sink. What's the best initial action?",
        options: ["A) Tighten the pipe connections", "B) Pour sealant immediately", "C) Ignore it; it will stop", "D) Remove all pipes"],
        answer: "A) Tighten the pipe connections",
        explanation: "Small leaks are often caused by loose connections. Tightening them is the safest first step before considering more extensive repairs."
    },
    {
        question: "Budgeting: You earn ₹50,000 per month. Which is a practical budgeting approach?",
        options: ["A) Spend whatever is left at month-end", "B) Save 20%, spend 50%, plan 30% for bills", "C) Keep all money in cash", "D) Spend 80% immediately"],
        answer: "B) Save 20%, spend 50%, plan 30% for bills",
        explanation: "Allocating funds to savings, essentials, and discretionary spending ensures financial stability and prevents overspending."
    },
    {
        question: "Tool Use: Which tool is best for tightening a loose screw?",
        options: ["A) Hammer", "B) Screwdriver", "C) Pliers", "D) Wrench"],
        answer: "B) Screwdriver",
        explanation: "A screwdriver is specifically designed to turn screws safely and effectively, unlike other tools which could damage the screw or cause injury."
    },
    {
        question: "Cooking / Measurement: A recipe calls for 250 ml of milk, but you only have a 1-liter jug. How do you measure accurately?",
        options: ["A) Fill half the jug", "B) Estimate a quarter visually", "C) Use a measuring cup or marked container", "D) Guess and adjust taste later"],
        answer: "C) Use a measuring cup or marked container",
        explanation: "Using a proper measuring tool ensures accuracy in recipes, preventing mistakes and maintaining taste consistency."
    },
    {
        question: "Car / Vehicle Maintenance: Your car tire pressure is low. What is the safest first step?",
        options: ["A) Drive faster to warm up the tire", "B) Inflate to recommended PSI before driving", "C) Ignore it", "D) Remove tire and replace it"],
        answer: "B) Inflate to recommended PSI before driving",
        explanation: "Low tire pressure affects handling and safety. Inflate to the manufacturer-recommended pressure before driving to prevent accidents."
    },
    {
        question: "Emergency Response: Someone nearby is choking and can't breathe. What should you do?",
        options: ["A) Wait and see if they recover", "B) Perform the Heimlich maneuver (abdominal thrusts)", "C) Give water immediately", "D) Call them loudly"],
        answer: "B) Perform the Heimlich maneuver",
        explanation: "The Heimlich maneuver is the correct emergency procedure to dislodge an object obstructing the airway, potentially saving a life."
    },
    {
        question: "Organizing Workspace: Your desk is cluttered and slows your work. Best action?",
        options: ["A) Ignore clutter and keep working", "B) Sort items by frequency of use", "C) Throw everything away", "D) Keep clutter in drawers randomly"],
        answer: "B) Sort items by frequency of use",
        explanation: "Organizing by frequency improves efficiency, keeps essential items accessible, and reduces wasted time searching for things."
    }
];

// Combined featured quiz questions (selection from all categories)
const featuredQuestions = [
    // Logical Reasoning
    {
        question: "Pattern completion: What is the next number in the sequence? 2, 6, 12, 20, 30, ?",
        options: ["A) 36", "B) 40", "C) 42", "D) 48"],
        answer: "C) 42",
        explanation: "This sequence follows the pattern of n(n+1) where n starts from 2: 2×3=6, 3×4=12, 4×5=20, 5×6=30, 6×7=42."
    },
    {
        question: "Analogies: Book is to Reading as Fork is to:",
        options: ["A) Drawing", "B) Stirring", "C) Eating", "D) Writing"],
        answer: "C) Eating",
        explanation: "The relationship is that a book is used for reading, and a fork is used for eating."
    },

    // Analytical Skills
    {
        question: "Percent change: A shirt costs $100. Its price increases by 20% and then decreases by 20%. What is the final price?",
        options: ["A) $96", "B) $100", "C) $104", "D) $120"],
        answer: "A) $96",
        explanation: "First, price increases by 20%: 100 + 20% of 100 = 100 + 20 = 120. Then decreases by 20%: 120 - 20% of 120 = 120 - 24 = 96."
    },
    {
        question: "Work-rate (combined): A can finish a job in 6 days, B in 8 days. How long will they take working together?",
        options: ["A) 3 days", "B) 3 3/7 days", "C) 3 1/2 days", "D) 4 days"],
        answer: "B) 3 3/7 days",
        explanation: "A's rate = 1/6 job/day, B's rate = 1/8 job/day. Combined rate = 1/6 + 1/8 = 7/24. Time = 1 ÷ (7/24) = 24/7 ≈ 3 3/7 days."
    },

    // Numerical Ability
    {
        question: "Percentage: A laptop costs ₹50,000 and is sold at a 10% discount. What is the selling price?",
        options: ["A) ₹45,000", "B) ₹47,000", "C) ₹48,000", "D) ₹49,000"],
        answer: "A) ₹45,000",
        explanation: "Selling price = Cost price - Discount = 50,000 - (10% of 50,000) = 50,000 - 5,000 = ₹45,000."
    },
    {
        question: "Average: The average of 8, 12, 20, and 40 is:",
        options: ["A) 20", "B) 22", "C) 25", "D) 30"],
        answer: "A) 20",
        explanation: "Average = (8 + 12 + 20 + 40) / 4 = 80 / 4 = 20."
    },

    // Creativity
    {
        question: "Alternate Uses: You're given a plain brick. Which use is the most original and useful?",
        options: ["A) Doorstop", "B) Garden marker with painted labels", "C) Modular bookend system (stack & interlock)", "D) Paperweight"],
        answer: "C) Modular bookend system (stack & interlock)",
        explanation: "This option transforms the brick into a new, reusable product with modular functionality, combining originality and practicality."
    },
    {
        question: "Metaphor match: Which metaphor best captures the idea of 'a small truth that changes everything'?",
        options: ["A) A crack in a dam", "B) A needle in a haystack", "C) A lighthouse in fog", "D) A pebble in a pond"],
        answer: "A) A crack in a dam",
        explanation: "A small crack can cause a massive flood, symbolizing how a minor truth can have major consequences."
    },

    // Communication Skills
    {
        question: "Active Listening: When someone shares a problem with you, the best first response is to:",
        options: ["A) Give quick advice", "B) Interrupt to share a similar story", "C) Listen carefully and paraphrase their concern", "D) Change the topic"],
        answer: "C) Listen carefully and paraphrase their concern",
        explanation: "Active listening involves fully focusing on the speaker and confirming understanding by paraphrasing. This shows empathy and avoids jumping to conclusions."
    },
    {
        question: "Written Clarity: Which sentence is clearest for formal communication?",
        options: ["A) 'Pls send file ASAP, thx.'", "B) 'Can you send the file soon?'", "C) 'Please send the file by 4 PM today.'", "D) 'Need that doc fast.'"],
        answer: "C) 'Please send the file by 4 PM today.'",
        explanation: "Clear, precise, and polite language with a specific deadline ensures the recipient understands exactly what is needed and by when."
    },

    // Artistic Skills
    {
        question: "Color Theory: Which color combination creates the strongest visual contrast?",
        options: ["A) Blue and green", "B) Red and orange", "C) Blue and yellow", "D) Purple and violet"],
        answer: "C) Blue and yellow",
        explanation: "Blue and yellow are complementary colors, located opposite each other on the color wheel, creating maximum contrast and visual impact."
    },
    {
        question: "Composition: The 'Rule of Thirds' in visual design helps to:",
        options: ["A) Balance and guide focus", "B) Increase image size", "C) Enhance color saturation", "D) Add more detail"],
        answer: "A) Balance and guide focus",
        explanation: "Dividing the canvas into thirds helps position subjects at key points, creating balance and directing the viewer's eye."
    },

    // Practical Skills
    {
        question: "Basic Electrical Safety: You notice a frayed wire on a lamp. What's the safest first step?",
        options: ["A) Plug it in to see if it works", "B) Touch it to test current", "C) Unplug it and repair or replace", "D) Cover with tape and continue"],
        answer: "C) Unplug it and repair or replace",
        explanation: "Exposed or frayed wires are a serious shock hazard. Always unplug before attempting any repair or replacement to ensure safety."
    },
    {
        question: "Time Management: You have 3 tasks due today: one urgent, two important. Which do you do first?",
        options: ["A) Start with an easy task", "B) Complete urgent task first", "C) Ignore deadlines and multitask", "D) Take a break first"],
        answer: "B) Complete urgent task first",
        explanation: "Tasks that are urgent and time-sensitive should be prioritized to prevent negative consequences, while important but non-urgent tasks can follow."
    }
];

// Function to start the quiz with specified type
function startQuiz(type) {
    currentQuizType = type;
    document.getElementById('main-content').classList.add('hidden');
    document.getElementById('quiz-container').classList.add('active');
    currentQuestion = 0;
    score = 0;
    userAnswers = []; // Reset user answers
    displayAllQuestions();
}

// Function to go back to main page
function goBack() {
    const quizContainer = document.getElementById('quiz-container');
    quizContainer.classList.add('closing');

    setTimeout(() => {
        document.getElementById('main-content').classList.remove('hidden');
        document.getElementById('quiz-container').classList.remove('active');
        quizContainer.classList.remove('closing');
        currentQuestion = 0;
        score = 0;
        userAnswers = [];
        currentQuizType = 'logical';
    }, 600); // Match the animation duration
}

// Function to display all questions at once
function displayAllQuestions() {
    const quizContainer = document.getElementById('quiz-container');

    // Show loading state first
    quizContainer.innerHTML = `
        <div class="quiz-content">
            <button id="back-btn" onclick="goBack()">Back to Main</button>
            <div class="quiz-loading">
                <div class="loading-spinner"></div>
                <div class="loading-text">Loading Quiz...</div>
            </div>
        </div>
    `;

    // Simulate loading delay for better UX
    setTimeout(() => {
        let questions;

        // Determine which question array to use based on current quiz type
        if (currentQuizType === 'analytical') {
            questions = analyticalQuestions;
        } else if (currentQuizType === 'numerical') {
            questions = numericalQuestions;
        } else if (currentQuizType === 'creativity') {
            questions = creativityQuestions;
        } else if (currentQuizType === 'communication') {
            questions = communicationQuestions;
        } else if (currentQuizType === 'artistic') {
            questions = artisticQuestions;
        } else if (currentQuizType === 'practical') {
            questions = practicalQuestions;
        } else if (currentQuizType === 'featured') {
            questions = featuredQuestions;
        } else {
            questions = logicalQuestions;
        }

        // Initialize userAnswers array if not already done
        if (userAnswers.length === 0) {
            userAnswers = new Array(questions.length).fill(null);
        }

        // Generate HTML for all questions
        let questionsHTML = questions.map((q, index) => `
            <div class="question-card" id="question-${index}">
                <h3 class="question-number">Question ${index + 1}</h3>
                <h4 class="question-text">${q.question}</h4>
                <div class="question-options">
                    ${q.options.map((option, optionIndex) => `
                        <label class="option-label">
                            <input type="radio" name="question-${index}" value="${option}" ${userAnswers[index] === option ? 'checked' : ''} onchange="saveAnswer(${index}, '${option}')">
                            <span class="option-text">${option}</span>
                        </label>
                    `).join('')}
                </div>
            </div>
        `).join('');

        quizContainer.innerHTML = `
            <div class="quiz-content">
                <button id="back-btn" onclick="goBack()">Back to Main</button>
                <div class="quiz-progress">
                    <span>Answer all questions and click submit to see your results</span>
                </div>
                <div class="all-questions">
                    ${questionsHTML}
                </div>
                <div class="submit-section">
                    <button class="btn btn-primary submit-btn" onclick="submitQuiz()">Submit Quiz</button>
                </div>
            </div>
        `;
        
        // Debug: Check if submit button exists
        setTimeout(() => {
            const submitBtn = document.querySelector('.submit-btn');
            console.log('Submit button found:', !!submitBtn);
            console.log('Submit button visible:', submitBtn ? submitBtn.offsetParent !== null : 'N/A');
            console.log('Questions loaded:', questions.length);
            console.log('User answers array length:', userAnswers.length);
            
            // Add click listener to debug
            if (submitBtn) {
                submitBtn.addEventListener('click', function(e) {
                    console.log('Submit button clicked!', e);
                    console.log('Event target:', e.target);
                    console.log('Current quiz type:', currentQuizType);
                    console.log('User answers before submit:', userAnswers);
                });
            }
        }, 100);
    }, 800); // 800ms loading delay for better UX
}

// Function to save user's answer for a specific question
function saveAnswer(questionIndex, selectedAnswer) {
    userAnswers[questionIndex] = selectedAnswer;
}

// Function to submit quiz and calculate score
function submitQuiz() {
    console.log('=== SUBMIT QUIZ CALLED ===');
    console.log('Current quiz type:', currentQuizType);
    console.log('User answers so far:', userAnswers);
    
    let questions;

    // Determine which question array to use based on current quiz type
    if (currentQuizType === 'analytical') {
        questions = analyticalQuestions;
    } else if (currentQuizType === 'numerical') {
        questions = numericalQuestions;
    } else if (currentQuizType === 'creativity') {
        questions = creativityQuestions;
    } else if (currentQuizType === 'communication') {
        questions = communicationQuestions;
    } else if (currentQuizType === 'artistic') {
        questions = artisticQuestions;
    } else if (currentQuizType === 'practical') {
        questions = practicalQuestions;
    } else if (currentQuizType === 'featured') {
        questions = featuredQuestions;
    } else {
        questions = logicalQuestions;
    }

    // Calculate score
    score = 0;
    for (let i = 0; i < questions.length; i++) {
        if (userAnswers[i] === questions[i].answer) {
            score++;
        }
    }
    
    console.log('Score calculation:');
    console.log('  Questions length:', questions.length);
    console.log('  Correct answers:', score);
    console.log('  User answers:', userAnswers);
    console.log('  Expected answers:', questions.map(q => q.answer));

    // Show results
    console.log('Calling showResults...');
    showResults(questions);
}

// Function to show quiz results
function showResults(questions) {
    try {
        console.log('=== SHOW RESULTS START ===');
        const quizContainer = document.getElementById('quiz-container');
        console.log('showResults called with questions:', questions.length);
        console.log('Questions data:', questions);

        // Calculate percentage
        const percentage = Math.round((score / questions.length) * 100);
        
        console.log('=== SHOW RESULTS DEBUG ===');
        console.log('Final score:', score);
        console.log('Total questions:', questions.length);
        console.log('Percentage:', percentage);
        console.log('Current quiz type:', currentQuizType);
        
        // Submit quiz results to dashboard
        console.log('Calling submitQuizResults...');
        submitQuizResults(currentQuizType, score, questions.length, percentage);

    // Generate results HTML with detailed feedback
    let resultsHTML = `
        <div class="quiz-content results-content">
            <button id="back-btn" onclick="goBack()">Back to Main</button>
            <div class="results-header">
                <h2>Quiz Complete!</h2>
                <div class="final-score">Your Score: ${score} / ${questions.length}</div>
                <div class="score-percentage">${percentage}%</div>
            </div>
    `;

    // Add detailed question review - show for all questions
    resultsHTML += `
        <div class="question-review">
            <h3>Question Review:</h3>
            ${questions.map((q, index) => {
                console.log(`Question ${index + 1}:`, q.question, 'Answer:', q.answer, 'User Answer:', userAnswers[index], 'Has explanation:', !!q.explanation);
                return `
                <div class="review-item ${userAnswers[index] === q.answer ? 'correct' : 'incorrect'}">
                    <div class="review-question">
                        <strong>Q${index + 1}:</strong> ${q.question}
                    </div>
                    <div class="review-answer">
                        <strong>Your Answer:</strong> ${userAnswers[index] || 'Not answered'}
                    </div>
                    <div class="review-correct">
                        <strong>Correct Answer:</strong> ${q.answer}
                    </div>
                    ${q.explanation ? `
                        <div class="review-explanation">
                            <strong>Explanation:</strong> ${q.explanation}
                        </div>
                    ` : `
                        <div class="review-explanation">
                            <strong>Explanation:</strong> <em>Explanation not available for this question.</em>
                        </div>
                    `}
                </div>
            `}).join('')}
        </div>
    `;

    resultsHTML += `
            <div class="results-actions">
                <button class="btn btn-primary" onclick="startQuiz('${currentQuizType}')">Retake Quiz</button>
                <button class="btn btn-success save-progress-btn" onclick="saveProgressAndGoBack()">
                    <i class="fas fa-save"></i> Save Progress & Continue
                </button>
                <button class="btn btn-outline-primary" onclick="goBack()">Back to Categories</button>
            </div>
        </div>
    `;

    console.log('Generated results HTML length:', resultsHTML.length);
    console.log('Results HTML includes Save Progress button:', resultsHTML.includes('Save Progress & Continue'));
    console.log('Results HTML includes saveProgressAndGoBack:', resultsHTML.includes('saveProgressAndGoBack'));
    console.log('Setting innerHTML...');
    quizContainer.innerHTML = resultsHTML;
    console.log('Results displayed successfully');
    
    // Debug: Check if button exists after setting innerHTML
    setTimeout(() => {
        const saveBtn = document.querySelector('.save-progress-btn');
        console.log('Save Progress button found after display:', !!saveBtn);
        console.log('Save Progress button visible:', saveBtn ? saveBtn.offsetParent !== null : 'N/A');
        
        if (!saveBtn) {
            console.error('Save Progress button NOT found in DOM!');
            console.log('Current innerHTML:', quizContainer.innerHTML);
            
            // Force add the button as a test
            const resultsActions = document.querySelector('.results-actions');
            if (resultsActions) {
                console.log('Found results-actions div, adding button manually...');
                const testBtn = document.createElement('button');
                testBtn.className = 'btn btn-success save-progress-btn';
                testBtn.innerHTML = '<i class="fas fa-save"></i> Save Progress & Continue (TEST)';
                testBtn.onclick = saveProgressAndGoBack;
                resultsActions.appendChild(testBtn);
                console.log('Test button added manually');
            } else {
                console.error('results-actions div not found!');
            }
        }
    }, 100);
    } catch (error) {
        console.error('Error in showResults function:', error);
        console.error('Stack trace:', error.stack);
    }
}

// Function to submit quiz results to dashboard
function submitQuizResults(quizType, score, totalQuestions, percentage) {
    console.log('=== APTITUDE QUIZ SUBMISSION DEBUG ===');
    console.log('Quiz Type:', quizType);
    console.log('Score:', score);
    console.log('Total Questions:', totalQuestions);
    console.log('Percentage:', percentage);
    
    // Get current user ID from localStorage or generate one
    const userId = localStorage.getItem('dashboard_user_id') || 
                   sessionStorage.getItem('user_id') || 
                   `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    console.log('User ID:', userId);
    console.log('localStorage dashboard_user_id:', localStorage.getItem('dashboard_user_id'));
    console.log('sessionStorage user_id:', sessionStorage.getItem('user_id'));
    
    // Store user ID for future use
    localStorage.setItem('dashboard_user_id', userId);
    
    // Prepare quiz data
    const quizData = {
        user_id: userId,
        quiz_type: quizType,
        score: percentage, // Send percentage for consistency
        total_questions: totalQuestions,
        timestamp: new Date().toISOString()
    };
    
    console.log('Submitting quiz data:', JSON.stringify(quizData, null, 2));
    console.log('Fetch URL:', '/api/quiz/submit');
    console.log('Current page URL:', window.location.href);
    
    // Submit to dashboard API
    fetch('/api/quiz/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(quizData)
    })
    .then(response => {
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        console.log('Response headers:', response.headers);
        
        if (!response.ok) {
            console.error('Response not OK:', response.statusText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    })
    .then(data => {
        console.log('Quiz results submitted successfully:', data);
        
        // Show success notification to user
        showNotification('Quiz results saved to your dashboard!', 'success');
        
        // Verify it was stored by checking immediately
        console.log('Verifying storage...');
        setTimeout(() => {
            fetch(`/api/dashboard/user/${userId}`)
                .then(response => response.json())
                .then(dashboardData => {
                    console.log('Dashboard verification:', dashboardData);
                    const trackingScores = dashboardData.tracking_scores;
                    console.log('Tracking scores after submission:', trackingScores);
                })
                .catch(error => console.error('Verification error:', error));
        }, 1000);
        
    })
    .catch(error => {
        console.error('Error submitting quiz results:', error);
        console.error('Error details:', error.message);
        console.error('Error stack:', error.stack);
        
        // Show error notification but don't block the user
        showNotification('Quiz completed but results could not be saved to dashboard', 'warning');
    });
}

// Function to save progress and go back to categories
async function saveProgressAndGoBack() {
    // Show saving indicator
    showNotification('Saving progress...', 'info');

    // Debug logging
    console.log('Attempting to save progress...');
    console.log('Current quiz type:', currentQuizType);
    console.log('User answers:', userAnswers);
    console.log('Score:', score);

    try {
        // Get questions data based on current quiz type
        let questions;
        if (currentQuizType === 'analytical') {
            questions = analyticalQuestions;
        } else if (currentQuizType === 'numerical') {
            questions = numericalQuestions;
        } else if (currentQuizType === 'creativity') {
            questions = creativityQuestions;
        } else if (currentQuizType === 'communication') {
            questions = communicationQuestions;
        } else if (currentQuizType === 'logical') {
            questions = logicalQuestions;
        } else if (currentQuizType === 'artistic') {
            questions = artisticQuestions;
        } else if (currentQuizType === 'practical') {
            questions = practicalQuestions;
        } else {
            questions = analyticalQuestions; // Default
        }

        console.log('Questions array length:', questions ? questions.length : 0);

        const response = await fetch('http://localhost:5001/api/quiz/progress/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                quiz_type: currentQuizType,
                answers: userAnswers,
                score: score,
                total_questions: questions ? questions.length : 0,
                timestamp: new Date().toISOString()
            })
        });

        console.log('Fetch response status:', response.status);
        console.log('Fetch response ok:', response.ok);

        if (response.ok) {
            const responseData = await response.json();
            console.log('Server response:', responseData);
            showNotification('Progress saved successfully!', 'success');
            // Auto redirect to categories after 1.5 seconds
            setTimeout(() => {
                goBack();
            }, 1500);
        } else {
            const errorText = await response.text();
            console.error('Server error response:', errorText);
            throw new Error(`Server error: ${response.status} - ${errorText}`);
        }
    } catch (error) {
        console.error('Error saving progress:', error);

        // Fallback to localStorage if server fails
        try {
            console.log('Attempting to save to localStorage as fallback...');
            const progressKey = `quiz_progress_${currentQuizType}`;
            const progressData = {
                quiz_type: currentQuizType,
                answers: userAnswers,
                score: score,
                total_questions: questions ? questions.length : 0,
                timestamp: new Date().toISOString(),
                saved_locally: true
            };

            localStorage.setItem(progressKey, JSON.stringify(progressData));
            showNotification('Progress saved to browser storage!', 'success');

            // Auto redirect to categories after 1.5 seconds
            setTimeout(() => {
                goBack();
            }, 1500);
        } catch (localStorageError) {
            console.error('localStorage also failed:', localStorageError);
            showNotification('Failed to save progress. You can continue without saving.', 'error');

            // Ask user if they want to continue without saving
            if (confirm('Unable to save progress. Do you want to continue back to categories anyway?')) {
                goBack();
            }
        }
    }
}

// Function to show notifications
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

