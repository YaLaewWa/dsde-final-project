import google.generativeai as genai
from google.api_core import retry_async
from googletrans import Translator
import os
from dotenv import load_dotenv
import asyncio
load_dotenv() 

def is_retryable(e) -> bool:
    if retry_async.if_transient_error(e):
        return True
    elif (isinstance(e, genai.errors.ClientError) and e.code == 429):
        return True
    elif (isinstance(e, genai.errors.ServerError) and e.code == 503):
        return True
    else:
        return False

def is_retryable(e) -> bool:
    if retry_async.if_transient_error(e):
        return True
    elif (isinstance(e, genai.errors.ClientError) and e.code == 429):
        return True
    elif (isinstance(e, genai.errors.ServerError) and e.code == 503):
        return True
    else:
        return False

class Judge:
  def __init__(self):
    genai.configure(api_key=os.getenv('API_KEY'))
    generation_config = genai.GenerationConfig(
            temperature=0,
    )
    self.model = genai.GenerativeModel("gemini-2.0-flash-001", generation_config=generation_config)
    self.translator = Translator()

  async def backTranslation(self,inp):
    att = 10
    out = []
    for i in range(att):
        try:
            translated_text = await self.translator.translate(inp, src='th', dest='en')
            return translated_text.text
            break
        except:
            continue

  @retry_async.AsyncRetry(predicate=is_retryable)
  async def getAnswer(self,inp):
    inp = await self.backTranslation(inp)
    prompt = (
      "You are a specialized evaluation system called “The Urban Issue Severity Judge.” "
      "Your only task is to rate the severity of a given urban issue. "
      "You MUST output EXACTLY ONE RATING from this list: Very Low, Low, Medium, High, or Very High. "
      "DO NOT output any explanation, reasoning, additional text, quotation marks, or numbers.\n\n"
      "Please think carefully before output anything"
      "Please evaluate this urban issue based on these criteria:\n"
      "  - Geographic Scale (area affected)\n"
      "  - Human Impact (casualties & displaced persons)\n"
      "  - Infrastructure Damage (critical facilities, utilities)\n"
      "  - Environmental Consequences (short- and long-term)\n"
      "  - Response Urgency (need for immediate intervention)\n\n"
      "Rating definitions:\n"
      "  - Very Low: Minimal impact; localized and easily managed.\n"
      "  - Low: Noticeable disruptions; manageable with standard resources.\n"
      "  - Medium: Moderate damage; disrupts critical services and infrastructure; may create risk to citizen.\n"
      "  - High: Significant damage; widespread disruption; demands urgent, large-scale multi-agency response (e.g., major flooding closing highways, multi-block power outage).\n"
      "  - Very High: Severe destruction; large-scale mobilization and external aid needed (e.g., major gas leak endangering lives, building fracture risking collapse).\n"
      "\n\n"
      "urban issue\n"
      f"{inp}\n\n"

      "As an evaluation system I would rate this urban issue as "
    )
    return self.model.generate_content(prompt).text

# test = Judge()
# print(asyncio.run(test.getAnswer('ท่อน้ำแตก')).strip("\n"))