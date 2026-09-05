"""
Crop disease and pest identification schema.
"""
from typing import Optional, List
from pydantic import Field
from app.schemas.evidence import EvidentiaryDomainModel, Evidence


class DiseaseDiagnostic(EvidentiaryDomainModel):
    """
    Diagnostic profile and treatment protocol for a plant disease/pest.
    """
    disease_id: str = Field(..., description="Unique code for disease/pest entry")
    crop_name: str = Field(..., description="Target crop affected")
    disease_name: str = Field(..., description="Name of disease or pest (e.g. Yellow Rust, Pink Bollworm)")
    causal_agent: str = Field(..., description="Type: Fungal, Bacterial, Viral, Insect, Deficiency")
    symptoms: List[str] = Field(default_factory=list, description="Visual symptom descriptors")
    favorable_conditions: str = Field(..., description="Weather/environmental conditions promoting disease")
    preventative_measures: List[str] = Field(default_factory=list)
    organic_control: str = Field(...)
    chemical_control: str = Field(...)
    dosage_per_acre: str = Field(..., description="Recommended active chemical & dosage")
    evidence: list[Evidence] = Field(default_factory=list, description="Diagnostic evidence sources")
