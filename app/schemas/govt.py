"""
Government scheme and subsidy schemas.
"""
from typing import Optional, List
from pydantic import Field
from app.schemas.evidence import EvidentiaryDomainModel, Evidence


class GovtScheme(EvidentiaryDomainModel):
    """
    Punjab / Federal Government Agricultural Subsidy or Assistance Scheme.
    """
    scheme_id: str = Field(...)
    scheme_name: str = Field(..., description="Name of government scheme")
    department: str = Field(default="Punjab Agriculture Department")
    eligibility_criteria: List[str] = Field(default_factory=list)
    benefit_summary: str = Field(..., description="Detailed description of benefits provided")
    subsidy_details: str = Field(..., description="Subsidy amount or percentage discount")
    application_deadline: Optional[str] = Field(None)
    required_documents: List[str] = Field(default_factory=list)
    contact_helpline: str = Field(default="0800-17000")
    evidence: list[Evidence] = Field(default_factory=list, description="Government notification evidence")
