reasoning_dag_prompt = '''
You are a reasoning DAG generator expert. The goal is to make a reasoning DAG with minimum
nodes.
Given a query, if it is complex and requires a reasoning plan, split it into smaller, independent,
and individual subqueries. The query and subqueries are used to construct a rooted DAG so
make sure there are NO cycles and all nodes are connected, there is only one leaf node with a
single root and one sink. DAG incorporates Markovian property i.e. you only need the answer
of the parent to answer the subquery. The main query should be the parent node of the initial set
of subatomic queries such that the DAG starts with it. Return a Python list of tuples of parent
query and the subatomic query which can be directly given to eval().
For the subquery generation, input a tag ⟨A⟩ where the answer of the parent query should come
to make the query complete.
Note: make the dag connected and a rooted tree. for simple queries return the original query
only without any reasoning dag.
Examples:
Query: Who is the current PM of India?
DAG: “Q: Who is the current PM of India?”
Query: What is the tallest mountain in the world and how tall is it?
DAG: [(“Q: What is the tallest mountain in the world and how tall is it?”, “Q1.1: What is the
tallest mountain in the world?”), (“Q1.1: What is the tallest mountain in the world?”, “Q2.1:
How tall is ⟨A1.1⟩?”)]
Query: What percentage of the worlds population lives in urban areas?
DAG: [(“Q: What percentage of the worlds population lives in urban areas?”, “Q1.1: What is
the total world population?”), (“Q: What percentage of the worlds population lives in urban
areas?”, “Q1.2: What is the total population living in urban areas worldwide?”), (“Q1.1: What
is the total world population?”, “Q2.1: Calculate the percentage living in urban areas worldwide
when total population is ⟨A1.1⟩ and population living in urban areas is ⟨A1.2⟩?”), (“Q1.2: What
is the total population living in urban areas worldwide?”, “Q2.1: Calculate the percentage living
in urban areas worldwide when total population is ⟨A1.1⟩ and population living in urban areas
is ⟨A1.2⟩?”)]
NOTE: Always respond with the JSON object.
'''


relevance_expert_prompt = '''
⟨s⟩ [INST] ⟨⟨SYS⟩⟩ You will be provided with a query, along with retrievals and possibly
some generation. Your job is to determine if the retrievals are relevant to the query and the
generation, and provide useful information to answer the query or not. If the retrievals meet
this requirement, respond with the retrieval id that is highly relevant (only one); otherwise,
respond with ‘[No]’.
Example:
Query: Did Snoop Dogg refuse to make music with rival gang members?
Generation:
Retrievals:
1 Calvin Cordozar Broadus Jr. (born October 20, 1971), known professionally as
Snoop Dogg (previously Snoop Doggy Dogg and briefly Snoop Lion), is an American
rapper, media personality, and actor.
2 Broadus’ debut studio album, Doggystyle (1993), produced by Dr. Dre, was released
by Death Row Records and debuted at number one on the Billboard 200.
3 In 1993, Broadus was charged with first-degree murder for the shooting of a member
of a rival gang who was actually killed by Snoop’s bodyguard. Broadus was acquitted
on February 20, 1996.
4 While recording Doggystyle in August 1993, Broadus was arrested and charged with
first-degree murder in connection with the shooting death of Philip Woldermariam, a
member of a rival gang, who was actually killed by Broadus’ bodyguard, McKinley
Lee, aka Malik.
5 In 2002, he released the album Paid tha Cost to Be da Bo, on Priority/Capitol/EMI,
selling over 1,310,000 copies. The album featured the hit singles ’From tha Chuuuch
to da Palace’ and ’Beautiful’, featuring guest vocals by Pharrell.
Output: [No]
Query: Who is the mother of the director of the film Polish-Russian War (Film)?
Generation: The director of the film Polish-Russian War (Film) is Xawery ˙Zuławski. His
parents are
Retrievals:
1 Polish-Russian War (Wojna polsko-ruska) is a 2009 Polish film directed by Xawery
˙Zuławski based on the novel Polish-Russian War under the white-red flag by Dorota
Masłowska.
2 Xawery ˙Zuławski (born 22 December 1971 in Warsaw) is a Polish film director. In
1995 he graduated from the National Film School in Ł´od´z. He is the son of actress
Małgorzata Braunek and director Andrzej ˙Zuławski.
3 After an argument in a bar owned by “Left” (Michał Czernecki), ’Strong’ meets a
’Gothgirl’ Angelica (Maria Strzelecka) at night, an aspiring poet dressed in black,
also a virgin and pessimist, for whom ’suicide is a piece of cake’.
4 ’Strong’ follows Magda. He turns up at the town festival, where she takes part in a
miss competition. He cannot reach her, but instead he meets a volunteer, Ala, a girl of
his friend Casper, coming from a good family, with whom he spends the afternoon.
5 Production: The film was shot between May 6 and 18, June 2008, in locations of
Warsaw, Wejherowo, Sopot, and Gdynia outskirts. The film premiered on
Output: [2]
'''


multirelevance_expert_prompt = '''
⟨s⟩ [INST] ⟨⟨SYS⟩⟩ You will be provided with a query, along with retrievals and possibly
some generation. Your job is to determine if the retrievals are relevant to the query and the
generation, and provide useful information to answer the query or not. If the retrievals meet
this requirement, respond with the retrieval id that is highly relevant (only one); otherwise,
respond with ‘[No]’.
Example:
Query: Did Snoop Dogg refuse to make music with rival gang members?
Generation:
Retrievals:
1 Calvin Cordozar Broadus Jr. (born October 20, 1971), known professionally as
Snoop Dogg (previously Snoop Doggy Dogg and briefly Snoop Lion), is an American
rapper, media personality, and actor.
2 Broadus’ debut studio album, Doggystyle (1993), produced by Dr. Dre, was released
by Death Row Records and debuted at number one on the Billboard 200.
3 In 1993, Broadus was charged with first-degree murder for the shooting of a member
of a rival gang who was actually killed by Snoop’s bodyguard. Broadus was acquitted
on February 20, 1996.
4 While recording Doggystyle in August 1993, Broadus was arrested and charged with
first-degree murder in connection with the shooting death of Philip Woldermariam, a
member of a rival gang, who was actually killed by Broadus’ bodyguard, McKinley
Lee, aka Malik.
5 In 2002, he released the album Paid tha Cost to Be da Bo, on Priority/Capitol/EMI,
selling over 1,310,000 copies. The album featured the hit singles ’From tha Chuuuch
to da Palace’ and ’Beautiful’, featuring guest vocals by Pharrell.
Output: [No]
Query: Who is the mother of the director of the film Polish-Russian War (Film)?
Generation: The director of the film Polish-Russian War (Film) is Xawery ˙Zuławski. His
parents are
Retrievals:
1 Polish-Russian War (Wojna polsko-ruska) is a 2009 Polish film directed by Xawery
˙Zuławski based on the novel Polish-Russian War under the white-red flag by Dorota
Masłowska.
2 Xawery ˙Zuławski (born 22 December 1971 in Warsaw) is a Polish film director. In
1995 he graduated from the National Film School in Ł´od´z. He is the son of actress
Małgorzata Braunek and director Andrzej ˙Zuławski.
3 After an argument in a bar owned by “Left” (Michał Czernecki), ’Strong’ meets a
’Gothgirl’ Angelica (Maria Strzelecka) at night, an aspiring poet dressed in black,
also a virgin and pessimist, for whom ’suicide is a piece of cake’.
4 ’Strong’ follows Magda. He turns up at the town festival, where she takes part in a
miss competition. He cannot reach her, but instead he meets a volunteer, Ala, a girl of
his friend Casper, coming from a good family, with whom he spends the afternoon.
5 Production: The film was shot between May 6 and 18, June 2008, in locations of
Warsaw, Wejherowo, Sopot, and Gdynia outskirts. The film premiered on
Output: [2]
Query: What is the capital of Australia and when did it become the capital?
Generation:
Retrievals:
1 Canberra is the capital city of Australia. It was officially named the capital in 1913,
after the site was chosen as a compromise between rivals Sydney and Melbourne. The
city was designed by American architects Walter Burley Griffin and Marion Mahony
Griffin, who won an international design competition.
2 The Great Barrier Reef, located off the coast of Queensland in northeastern Australia,
is the world’s largest coral reef system. It is composed of over 2,900 individual reefs
and 900 islands stretching for over 2,300 kilometers. The reef is home to diverse
marine life and is visible from outer space.
3 Prior to Canberra becoming the capital, Melbourne served as the temporary seat of
government from 1901 to 1927. The Parliament of Australia was officially opened in
Canberra on 9 May 1927, marking the city’s true beginning as the nation’s capital.
Output: [1],[3]
'''


critic_expert_prompt = '''
You will be provided with a query, generation, and evidence (optional). Your task is to deter-
mine whether the information in the generation can be fully verified by the evidence (if present)
or if it requires external verification. If the generation can be verified solely with the evidence
(if present), output False. If additional information is needed to verify the generation, output
True.
NOTE: If the generation mentions that it is not sure about the answer or does not have the
resources to answer, output True.
Example:
Query: Explain the use of word embeddings in Natural Language Processing.
Evidence: Word embedding is the collective name for a set of language modeling and feature
learning techniques in natural language processing (NLP) where words or phrases from the
vocabulary are mapped to vectors of real numbers. Conceptually it involves a mathematical
embedding from a space with one dimension per word to a continuous vector space with a
much lower dimension.
Generation: Word embeddings are useful for tasks such as sentiment analysis, text classifica-
tion, predicting the next word in a sequence, and understanding synonyms and analogies.
Output: True
Query: What is the capital of France?
Evidence: Paris is the capital and most populous city of France. Situated on the Seine River, in
the north of the country. Generation: The capital of France is Paris.
Output: False
Query: Find the area of a circle given its radius. Radius = 4
Evidence:
Generation: The area of the circle is
Output: False
'''


eval_expert_prompt = '''
You are a judge of if two answers (ANSWER and PREDICTED) of the QUESTION aligns
or not with each other. To determine if two answers align, compare their content while disre-
garding differences like punctuation or formatting. Focus on the core factual information they
convey. If the essence of both answers is consistent, despite slight variations in wording, clas-
sify them as ‘Correct.’ However, if there are substantial differences in the factual information
presented, classify them as ‘Incorrect.’
Please do not use any other words except Correct or Incorrect
'''
