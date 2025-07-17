
from fastapi import HTTPException
import httpx
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://api.reporter.nih.gov/v2/projects/search"

TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 1

async def fetch_project_by_pi_number(pi_number: int) -> Dict[str, Any]:
    payload = {
        "criteria": {
            "pi_profile_ids": [pi_number]
        },
        "include_fields": [
            "ApplId","SubprojectId","FiscalYear","ProjectNum","ProjectSerialNum","Organization", "OrganizationType",
            "AwardType", "ActivityCode", "AwardAmount", "ProjectNumSplit", "PrincipalInvestigators", "ProgramOfficers",
            "AgencyIcAdmin", "AgencyIcFundings","CongDist", "ProjectStartDate","ProjectEndDate",
            "AwardNoticeDate", "CoreProjectNum", "ProjectTitle"
            ]
    }

    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                logger.info(f"Attempting to fetch data for PI {pi_number} (attempt {attempt + 1})")

                response = await client.post(BASE_URL, json=payload)
                response.raise_for_status()

                data = response.json()

                if not isinstance(data, dict):
                    raise ValueError("Invalid response format")

                logger.info(f"Successfully fetched data for PI {pi_number}")
                return data
        
        except httpx.TimeoutException as e:
            logger.warning(f"Timeout on attempt {attempt + 1} for PI {pi_number}")
            if attempt == MAX_RETRIES - 1:
                raise HTTPException(status_code=504, detail="Timeout while fetching data")
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="No data found for the given PI number")
            elif e.response.status_code == 429:
                logger.warning(f"Rate limited on attempt {attempt + 1} for PI {pi_number}")
                if attempt == MAX_RETRIES - 1:
                    raise HTTPException(status_code=429, detail="NIH API rate limit exceeded")
            else:
                logger.error(f"HTTP error {e.response.status_code} on attempt {attempt + 1}")
                if attempt == MAX_RETRIES - 1:
                    raise HTTPException(
                        status_code=e.response.status_code,
                        detail=f"NIH API Error: {e.response.text}"
                    )
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")
        
        if attempt < MAX_RETRIES - 1:
            wait_time = RETRY_DELAY * (2 ** attempt)
            logger.info(f"Waiting {wait_time}s before retrying...")
            await asyncio.sleep(wait_time)

    raise HTTPException(status_code=500, detail="Max retries reached")

