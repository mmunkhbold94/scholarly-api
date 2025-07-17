import httpx

BASE_URL = "https://api.reporter.nih.gov/v2/projects/search"

async def fetch_project_by_pi_number(pi_number: int):
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

    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=payload)
        response.raise_for_status()
        return response.json()
