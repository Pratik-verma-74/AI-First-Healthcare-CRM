import datetime
from sqlalchemy.orm import Session
from app.models.schema import HCP, Interaction, FollowUp, AuditLog, ChatHistory


def seed_initial_data(db: Session):
    """
    Seeds initial Healthcare Professionals and past interaction logs into the database
    if they do not already exist (e.g. on fresh local SQLite startup or clean Supabase DB).
    """
    hcps_data = [
        {"name": "Dr. Rakesh Sharma", "specialty": "Cardiology", "hospital": "Apollo Hospital, New Delhi", "contact_email": "rakesh.sharma@apollo.com", "phone": "+91-9811098110", "city": "New Delhi"},
        {"name": "Dr. Anjali Gupta", "specialty": "Oncology", "hospital": "AIIMS, New Delhi", "contact_email": "anjali.gupta@aiims.edu", "phone": "+91-9876543210", "city": "New Delhi"},
        {"name": "Dr. Vikram Mehta", "specialty": "Endocrinology", "hospital": "Fortis Healthcare, Mumbai", "contact_email": "v.mehta@fortis.com", "phone": "+91-9822334455", "city": "Mumbai"},
        {"name": "Dr. Sunita Rao", "specialty": "Pediatrics", "hospital": "Manipal Hospital, Bangalore", "contact_email": "s.rao@manipal.com", "phone": "+91-9844556677", "city": "Bangalore"},
        {"name": "Dr. Rajesh Khanna", "specialty": "Neurology", "hospital": "Medanta The Medicity, Gurgaon", "contact_email": "r.khanna@medanta.org", "phone": "+91-9911223344", "city": "Gurgaon"},
    ]

    hcp_map = {}
    for data in hcps_data:
        h = db.query(HCP).filter(HCP.name.ilike(f"%{data['name'].replace('Dr. ', '').strip()}%")).first()
        if not h:
            h = HCP(**data)
            db.add(h)
            db.commit()
            db.refresh(h)
        hcp_map[data["name"]] = h

    # Check if interactions exist for Dr. Rakesh Sharma & Dr. Anjali Gupta
    if db.query(Interaction).count() == 0:
        interactions = [
            Interaction(
                hcp_id=hcp_map["Dr. Rakesh Sharma"].id,
                interaction_type="Meeting",
                interaction_date=datetime.date(2025, 4, 10),
                interaction_time="11:30",
                attendees="Dr. Rakesh Sharma, Amit Kumar (MR)",
                topics_discussed="Discussed clinical efficacy of CardioPlus in hypertensive patients with Type 2 diabetes. Highlighted 24-hour blood pressure control.",
                materials_shared="CardioPlus Clinical Trial Monograph, Dosage Flowchart Brochure",
                samples_distributed='{"product": "CardioPlus 50mg", "quantity": 15}',
                observed_sentiment="Positive",
                outcomes="Doctor appreciated the once-daily dosing and agreed to prescribe CardioPlus to 5 new patients this week.",
                ai_summary="Medical Representative met Dr. Rakesh Sharma at Apollo Hospital to discuss CardioPlus clinical trials. Shared monograph brochure and 15 trial samples. Doctor showed strong interest and agreed to initiate prescriptions.",
                status="Saved"
            ),
            Interaction(
                hcp_id=hcp_map["Dr. Anjali Gupta"].id,
                interaction_type="Advisory Board",
                interaction_date=datetime.date(2025, 4, 12),
                interaction_time="14:00",
                attendees="Dr. Anjali Gupta, Dr. Neha Verma, Medical Affairs Team",
                topics_discussed="OncoBoost Phase III survival data presentation and discussion on immune-related adverse event management.",
                materials_shared="OncoBoost Phase III Clinical Deck, Management Guidelines Booklet",
                samples_distributed='{"product": "OncoBoost Starter Kit", "quantity": 5}',
                observed_sentiment="Positive",
                outcomes="Dr. Gupta consented to participate as a keynote speaker at the upcoming National Oncology Summit.",
                ai_summary="Conducted Advisory Board session with Dr. Anjali Gupta at AIIMS regarding OncoBoost Phase III survival data. Shared complete clinical deck and 5 starter kits. Dr. Gupta accepted invitation to speak at National Summit.",
                status="Saved"
            ),
            Interaction(
                hcp_id=hcp_map["Dr. Vikram Mehta"].id,
                interaction_type="Meeting",
                interaction_date=datetime.date(2025, 4, 15),
                interaction_time="16:00",
                attendees="Dr. Vikram Mehta, Priya Singh (MR)",
                topics_discussed="Reviewed GlucoFix ER efficacy compared to standard metformin therapy.",
                materials_shared="GlucoFix ER Patient Care Guide",
                samples_distributed='{"product": "GlucoFix ER 1000mg", "quantity": 10}',
                observed_sentiment="Neutral",
                outcomes="Doctor requested additional post-marketing surveillance data on gastrointestinal tolerability before switching ongoing patients.",
                ai_summary="Discussed GlucoFix ER with Dr. Vikram Mehta at Fortis Healthcare. Shared patient guides and 10 samples. Doctor expressed neutral sentiment, requesting further GI tolerability data before expanding usage.",
                status="Saved"
            ),
        ]
        db.add_all(interactions)
        db.commit()

        for i in interactions:
            db.refresh(i)

        follow_ups = [
            FollowUp(
                interaction_id=interactions[0].id,
                hcp_id=hcp_map["Dr. Rakesh Sharma"].id,
                action_description="Deliver updated CardioPlus patient support brochures and check initial prescription feedback.",
                due_date=datetime.date(2025, 4, 24),
                status="Pending"
            ),
            FollowUp(
                interaction_id=interactions[1].id,
                hcp_id=hcp_map["Dr. Anjali Gupta"].id,
                action_description="Send official speaker invitation packet and travel itinerary for National Oncology Summit.",
                due_date=datetime.date(2025, 4, 25),
                status="Pending"
            ),
            FollowUp(
                interaction_id=interactions[2].id,
                hcp_id=hcp_map["Dr. Vikram Mehta"].id,
                action_description="Provide medical affairs GI tolerability study report for GlucoFix ER.",
                due_date=datetime.date(2025, 4, 22),
                status="Pending"
            ),
        ]
        db.add_all(follow_ups)

        audit_logs = [
            AuditLog(entity_type="Interaction", entity_id=interactions[0].id, action="AI_SAVE", changes='{"status": "Saved", "ai_summary": "Generated automatically via Log Interaction tool"}'),
            AuditLog(entity_type="Interaction", entity_id=interactions[1].id, action="AI_SAVE", changes='{"status": "Saved", "ai_summary": "Generated automatically via Log Interaction tool"}'),
            AuditLog(entity_type="Interaction", entity_id=interactions[2].id, action="AI_SAVE", changes='{"status": "Saved", "ai_summary": "Generated automatically via Log Interaction tool"}'),
        ]
        db.add_all(audit_logs)

        chat_histories = [
            ChatHistory(session_id="demo-session-101", sender="user", message="I met Dr Rakesh Sharma at Apollo Hospital today morning. Discussed CardioPlus clinical trials and shared the clinical monograph brochure. Gave 15 samples of CardioPlus 50mg. Doctor was very interested. Schedule follow up in two weeks.", tool_called=None),
            ChatHistory(session_id="demo-session-101", sender="ai", message="I have extracted the interaction details for Dr. Rakesh Sharma at Apollo Hospital. I filled out the structured form with CardioPlus clinical discussions, brochure shared, 15 samples distributed, and positive sentiment. Would you like me to save this interaction and schedule the follow-up for April 24, 2025?", tool_called="log_interaction"),
        ]
        db.add_all(chat_histories)
        db.commit()
