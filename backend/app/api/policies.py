import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.policy import Policy, PolicyVersion
from app.schemas.policy import PolicyCreate, PolicyUpdate, PolicyResponse
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/policies", tags=["Policy Management"])

@router.get("", response_model=List[PolicyResponse])
def list_policies(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Policy).order_by(Policy.priority)
    if category:
        query = query.filter(Policy.category == category)
    if is_active is not None:
        query = query.filter(Policy.is_active == is_active)
    return query.all()

@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
def create_policy(
    policy_in: PolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exists = db.query(Policy).filter(Policy.id == policy_in.id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Policy with this ID already exists.")

    new_policy = Policy(
        id=policy_in.id,
        name=policy_in.name,
        description=policy_in.description,
        category=policy_in.category,
        rule_type=policy_in.rule_type,
        configuration=policy_in.configuration or {},
        is_active=policy_in.is_active,
        priority=policy_in.priority
    )
    db.add(new_policy)

    v1 = PolicyVersion(
        id=f"pv-{uuid.uuid4().hex[:10]}",
        policy_id=new_policy.id,
        version_num=1,
        configuration=new_policy.configuration,
        changed_by=current_user.username,
        change_summary="Initial policy creation"
    )
    db.add(v1)

    db.commit()
    db.refresh(new_policy)
    return new_policy

@router.patch("/{policy_id}", response_model=PolicyResponse)
def update_policy(
    policy_id: str,
    update_in: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found.")

    latest_v = db.query(PolicyVersion).filter(PolicyVersion.policy_id == policy_id).order_by(PolicyVersion.version_num.desc()).first()
    next_ver_num = (latest_v.version_num + 1) if latest_v else 1

    for field, val in update_in.model_dump(exclude_unset=True).items():
        if field != "change_summary":
            setattr(policy, field, val)

    policy.updated_at = datetime.utcnow()

    version_record = PolicyVersion(
        id=f"pv-{uuid.uuid4().hex[:10]}",
        policy_id=policy.id,
        version_num=next_ver_num,
        configuration=policy.configuration,
        changed_by=current_user.username,
        change_summary=update_in.change_summary or "Policy updated"
    )
    db.add(version_record)

    db.commit()
    db.refresh(policy)
    return policy
