from datetime import date, time

from pydantic import BaseModel, Field, create_model

from app.visits.field_lists import ALL_SCALAR_FIELDS, field_default, field_type


class PatientIn(BaseModel):
    tz: str = Field(min_length=9, max_length=9)
    fname: str = Field(min_length=1, max_length=20)
    surname: str = Field(min_length=1, max_length=20)
    email: str = Field(max_length=30)
    phone: str = Field(max_length=12)
    dob: date
    male: bool
    smoker: bool
    consent: bool


class PatientOut(BaseModel):
    tz: str
    fname: str
    surname: str
    email: str
    phone: str
    dob: date
    male: bool
    smoker: bool
    consent: bool
    visit_count: int


class PatientSummary(BaseModel):
    tz: str
    fname: str
    surname: str
    visit_count: int


class TzChangeIn(BaseModel):
    new_tz: str = Field(min_length=9, max_length=9)


class VisitSummaryOut(BaseModel):
    visits: int
    visits_with_procedures: int


class LoginIn(BaseModel):
    username: str
    password: str


class PastHistoryIn(BaseModel):
    hypertension: bool = False
    diabetes: bool = False
    blood: bool = False
    blood_descr: str = ""
    malignancy: bool = False
    malignancy_date: str = Field("", max_length=15)
    malignancy_details: str = ""
    malignancy_remiss: bool = False
    disable: bool = False
    disable_details: str = ""
    operations: str = ""
    trauma: str = ""
    nacs: list[str] = Field(default_factory=list)
    acs: list[str] = Field(default_factory=list)


class PastHistoryOut(PastHistoryIn):
    pass


# Built from field_lists.ALL_SCALAR_FIELDS (252 fields) rather than typed
# out by hand, so the schema can't drift from the field-order lists that
# app/visits/routes.py uses to build save_visit()'s positional tuples --
# one source of truth for "what fields exist", field_lists.py for "what
# order they go in".
_visit_scalar_fields = {
    name: (field_type(name), field_default(name)) for name in ALL_SCALAR_FIELDS
}
_visit_scalar_fields.update(
    {
        "examination": (str, ""),
        "tests": (str, ""),
        "recommendation": (str, ""),
    }
)

VisitIn = create_model(
    "VisitIn",
    procedures=(dict[str, str], Field(default_factory=dict)),
    diagnoses=(dict[str, str], Field(default_factory=dict)),
    **_visit_scalar_fields,
)


class VisitOut(VisitIn):
    visit_date: date
    is_new: bool = False


class VisitDatesOut(BaseModel):
    dates: list[date]
    today: date


class BloodReadingIn(BaseModel):
    pulse: int | None = None
    systolic: int | None = None
    diastolic: int | None = None


class BloodReadingOut(BaseModel):
    time: time
    pulse: int | None = None
    systolic: int | None = None
    diastolic: int | None = None


class PatientBasicOut(BaseModel):
    tz: str
    fname: str
    surname: str
