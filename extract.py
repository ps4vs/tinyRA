import asyncio
import os
from langchain.text_splitter import TokenTextSplitter
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from typing import List
from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator

DEFAULT_CHUNK_LENGTH = 4096 * 3 / 4  # 3/4ths of the context window size
LLM=None
RETRIES = 5

def create_chunks(tweet_data):
    tweet = tweet_data.get('tweet', '')  # Safely get the tweet text
    text_splitter = TokenTextSplitter(chunk_size=1024, chunk_overlap=100)
    tweet_chunks = [Document(page_content=tweet)]
    tweet_chunks = text_splitter.split_documents(tweet_chunks)
    return tweet_chunks

def summarize_tweet(tweet_chunks, tweet_data):
    research_topic = tweet_data.get('research_topic', 'your research topic')
    
    prompt_template = (
        "Please provide a concise summary of the following Twitter thread. "
        "Include key points of discussion and mention who is saying what:\n\n"
        "{text}\n\n"
        "Summary:"
    )

    refine_prompt_template = (
        f"As a researcher focusing on {research_topic}, I need to refine an existing summary "
        "with additional context provided below. The goal is to capture the essence of the Twitter thread, "
        "highlighting main points and contributors in the discussion:\n\n"
        "Existing Summary: {existing_answer}\n\n"
        "Additional Context:\n"
        "------------\n"
        "{text}\n"
        "------------\n"
        "Refined Summary:"
    )

    question_prompt = PromptTemplate.from_template(prompt_template)
    refine_prompt = PromptTemplate.from_template(refine_prompt_template)
    
    chain = load_summarize_chain(
        LLM,
        chain_type="refine",
        verbose=True,
        question_prompt=question_prompt,
        refine_prompt=refine_prompt,
    )
  
    query = """Provide a detailed summary of the Twitter thread, focusing on the main topics of discussion. \n
        Identify the key contributors and summarize the specific points or arguments each person is making. \n
        Highlight any significant interactions or agreements/disagreements among the participants."""
    summary_result = chain({"input_documents": tweet_chunks, "question": query})

    return summary_result

async def validate_claims(claims):
    # code to check whether claims are valid or not
    return
async def store_claims(claims, tweet_summary, tweet_data):
    # code to store new claims should be created here, how to match claims together this can be done in clustering part???
    # if claim is unique then create new entry in the database, if claim is append meta_data to exiting authors list
    return

async def extract_claim_from_chunk(chunk, tweet_summary, tweet_data):
    
    class Claim(BaseModel):
        source: str = Field(description="The exact source text from which the claim has been extracted")
        claim: str = Field(description="A factual claim made in the source text")
        relevant: bool = Field(description="Determine whether this claim is relevant to the research topic. If it is not relevant, set this to False, otherwise set it to True.")
        author: str = Field(description="Who is the author of the claim, i.e. the person who is stating it? String or 'None' if not sure. The article author should be assumed if that is known and the claim is not a quote.")
        debate_question: str = Field(description="A debate question which the claim is relevant to or answers directly.")
    
        @validator("author")
        def check_author(cls, field):
            if field!=tweet_data['author']:
                raise ValueError("author not matching")
            return field
        
    class Claims(BaseModel):
        claims: List(Claim) = Field(description=f"list of claims made by the author {tweet_data['author']}")
    
    claims = []
    
    extract_claim_prompt_template = """\
    I am a researcher with the following research topic:
    {research_topic}
    
    I am extracting claims from twitter thread discussion. Extract claims made by author {author} only.
    
    Summary of full twitter thread discussion:
    {tweet_summary}
    
    Current section of the twitter thread is:
    {chunk}
    
    TASK: Extract claims made by author {author} from the currect tweet discussion section I am working on.
    - Include the specific passage of source text that the claim references as the source parameter.
    - Please extract the specific and distinct claims from this text, and respond with all factual claims as a JSON array. Avoid duplicate claims.
    - Each claim should be one statement. Ignore questions, section headers, fiction, feelings and rhetoric: they are not factual claims.
    - DO NOT just of use pronouns or shorthand like 'he' or 'they' in claims. Use the actual complete name of the person or thing you are referring to and be very detailed and specific.
    - Claims should include extensive detail so that they can stand alone without the source text. This includes detailed descriptions of who, what and when.
    - ALWAYS use the full name and title of people along with any relationship to organizations. For example, instead of 'the president', use 'Current U.S. President Joe Biden'. Do not use nicknames or short names when referring to people. Instead of "Mayor Pete", use "Pete Buttigieg".
    - Ignore anything that isn't relevant to the research topic, including political opinions, feelings, and rhetoric. We are only interested in claims that are factual, i.e. can be proven or disproven.
    - Please disambiguate and fully describe known entities. For example, instead of 'Kim the Rocketman', use 'North Korean leader Kim Jong Un'. Instead of 'the 2016 election', use 'the 2016 U.S. presidential election'.
    - Split claims up into specific statements, even if the source text has combined the claims into a single statement. There can be multiple claims for a source. For example, if a source sentence makes multiple claims, these should be separated
    """

    claims_parser = PydanticOutputParser(pydantic_object=Claims)
    
    extract_claim_prompt = PromptTemplate(
        template=extract_claim_prompt_template,
        input_variables=["research_topic", "author", "tweet_summary", "chunk"]
    )
    
    extract_claims_input = extract_claim_prompt.format_prompt({
        "research_topic": tweet_data["research_topic"],
        "author": tweet_data["author"],
        "tweet_summary": tweet_summary,
        "chunk": chunk
    }).to_string()
    
    for _ in range(RETRIES):
        try:
            claims_response = await LLM(extract_claims_input)
            claims = claims_parser.parse(claims_response)
            if validate_claims(claims):
                return claims
        except Exception as e:
            print(f"Error during claim extraction: {e}")
            
    return []

async def async_main(context):
    project_dir = context.get('project_dir', None)
    try:
        tweets = context['tweets']
    except:
        raise Exception("No Relevant Authors")
    
    if project_dir is None:
        project_dir = f'./project_data/{context["project_name"]}'
        os.makedirs(project_dir, exist_ok=True)
        context['project_dir'] = project_dir
    
    tasks = []
    for tweet_data in tweets:
        tweet_chunks = await create_chunks(tweet_data)
        tweet_summary = await summarize_tweet(tweet_chunks, tweet_data)
        # improve asyncronosity here using tasks
        for chunk in tweet_chunks:
            claims = await extract_claim_from_chunk(chunk, tweet_summary, tweet_data)
            if len(claims)!=0:
                await store_claims(claims, tweet_summary, tweet_data)
        # grouping tweets is done earlier, just extract claims
    return context

async def extract(context):
    context = await async_main(context)
    return context


if __name__ == "__main__":
    context = {
        "project_dir": "test",
        "tweets": None,
        "author": None,
        "research_topic": None,
        "sample_queries_file": None
    }
    asyncio.run(extract(context))
