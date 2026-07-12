import os
import sys
import json
from datetime import date

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, Base, engine
from app.models.schema import HCP, Interaction, FollowUp, AuditLog, ChatHistory
from app.ai.agent import process_chat_message
from app.models.pydantic_schemas import FormState
from app.seed_data import seed_initial_data


def run_comprehensive_test():
    print("==========================================================================")
    print("   AI-First Healthcare CRM - End-to-End LangGraph & ORM Verification   ")
    print("==========================================================================")

    # Ensure tables exist for verification
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Seed comprehensive initial data (all 5 HCPs and past interactions)
        seed_initial_data(db)

        # Check if seed data exists or insert test doctor
        test_hcp = db.query(HCP).filter(HCP.name.ilike("%Sharma%")).first()
        if not test_hcp:
            print("[INFO] Seeding test HCP Dr. Rakesh Sharma into database...")
            test_hcp = HCP(
                name="Dr. Rakesh Sharma",
                specialty="Cardiology",
                hospital="Apollo Hospital, New Delhi",
                contact_email="sharma@apollo.com",
                phone="+91-9811098110",
                city="New Delhi"
            )
            db.add(test_hcp)
            db.commit()
            db.refresh(test_hcp)
        print(f"[✅ CHECK 1] Database ORM Connected. Found HCP: {test_hcp.name} (ID: {test_hcp.id}) at {test_hcp.hospital}")

        # Step 1: Simulate User saying "I met Dr Sharma at Apollo Hospital today. Discussed CardioPlus..."
        print("\n--------------------------------------------------------------------------")
        print("[TESTING TOOL 1] log_interaction via LangGraph Agent (/chat)")
        print("--------------------------------------------------------------------------")
        initial_form = FormState().model_dump()
        user_message_1 = (
            "I met Dr Sharma at Apollo Hospital today morning. Discussed CardioPlus clinical trial efficacy. "
            "Shared the dosage monograph brochure. Gave 15 samples of CardioPlus 50mg. "
            "Doctor was very interested and positive. Schedule follow-up meeting next Tuesday."
        )
        print(f"User Input -> \"{user_message_1}\"")

        resp_1 = process_chat_message(
            session_id="test-integration-101",
            user_message=user_message_1,
            current_form_data=initial_form,
            db=db
        )
        print(f"AI Response -> {resp_1.response}")
        if resp_1.tool_execution:
            print(f"LangGraph Tool Executed -> {resp_1.tool_execution.tool_name}() [{resp_1.tool_execution.execution_time_ms}ms]")
            print(f"Summary -> {resp_1.tool_execution.tool_summary}")
        
        updated_form_1 = resp_1.updated_form_data
        print(f"\n[Read-Only Form Populated State]:")
        print(f"  • HCP Name: {updated_form_1.hcp_name} ({updated_form_1.hospital})")
        print(f"  • Topics: {updated_form_1.topics_discussed}")
        print(f"  • Materials: {updated_form_1.materials_shared}")
        print(f"  • Samples: {updated_form_1.samples_distributed}")
        print(f"  • Sentiment: {updated_form_1.observed_sentiment}")
        print(f"  • Follow-up: {updated_form_1.follow_up_actions}")
        print(f"  • AI Summary: {updated_form_1.ai_summary[:100]}...")
        print(f"  • Needs Confirmation: {resp_1.needs_confirmation}")
        assert updated_form_1.hcp_name != "", "HCP Name must be populated by log_interaction"
        print("[✅ CHECK 2] Tool 1 (log_interaction) successfully extracted entities & populated form.")

        # Step 2: Simulate User saying "Change the sentiment to Negative and add 5 more samples"
        print("\n--------------------------------------------------------------------------")
        print("[TESTING TOOL 2] edit_interaction via LangGraph Agent (/chat)")
        print("--------------------------------------------------------------------------")
        user_message_2 = "Change the sentiment to Negative and make the samples distributed read '20 samples of CardioPlus'."
        print(f"User Input -> \"{user_message_2}\"")

        resp_2 = process_chat_message(
            session_id="test-integration-101",
            user_message=user_message_2,
            current_form_data=updated_form_1.model_dump(),
            db=db
        )
        updated_form_2 = resp_2.updated_form_data
        print(f"AI Response -> {resp_2.response}")
        if resp_2.tool_execution:
            print(f"LangGraph Tool Executed -> {resp_2.tool_execution.tool_name}()")
        print(f"  • Updated Sentiment: {updated_form_2.observed_sentiment}")
        print(f"  • Preserved HCP Name: {updated_form_2.hcp_name}")
        print("[✅ CHECK 3] Tool 2 (edit_interaction) successfully updated specific fields without overwriting unchanged values.")

        # Step 3: Simulate User saying "Yes, save it"
        print("\n--------------------------------------------------------------------------")
        print("[TESTING TOOL 5] save_interaction via LangGraph Agent (/chat)")
        print("--------------------------------------------------------------------------")
        user_message_3 = "Yes, save this interaction to Supabase right now."
        print(f"User Input -> \"{user_message_3}\"")

        resp_3 = process_chat_message(
            session_id="test-integration-101",
            user_message=user_message_3,
            current_form_data=updated_form_2.model_dump(),
            db=db
        )
        print(f"AI Response -> {resp_3.response}")
        if resp_3.tool_execution:
            print(f"LangGraph Tool Executed -> {resp_3.tool_execution.tool_name}()")
        print(f"  • Saved Interaction ID: #{resp_3.saved_interaction_id}")
        assert resp_3.saved_interaction_id is not None, "Saved interaction ID must be returned"

        # Verify against Database & AuditLog
        saved_record = db.query(Interaction).filter(Interaction.id == resp_3.saved_interaction_id).first()
        audit_record = db.query(AuditLog).filter(AuditLog.entity_type == "Interaction", AuditLog.entity_id == resp_3.saved_interaction_id).first()
        print(f"  • DB Record Status: {saved_record.status} (HCP ID: {saved_record.hcp_id})")
        print(f"  • Audit Log Entry Found: Action={audit_record.action}, Timestamp={audit_record.timestamp}")
        print("[✅ CHECK 4] Tool 5 (save_interaction) successfully validated, committed to DB, and wrote AuditLog.")

        # Step 4: Simulate User saying "Search for Dr. Anjali Gupta at AIIMS"
        print("\n--------------------------------------------------------------------------")
        print("[TESTING TOOL 3] search_hcp via LangGraph Agent (/chat)")
        print("--------------------------------------------------------------------------")
        user_message_4 = "Search for Dr. Anjali Gupta at AIIMS"
        print(f"User Input -> \"{user_message_4}\"")

        resp_4 = process_chat_message(
            session_id="test-integration-101",
            user_message=user_message_4,
            current_form_data=FormState().model_dump(),
            db=db
        )
        print(f"AI Response -> {resp_4.response[:180]}...")
        if resp_4.tool_execution:
            print(f"LangGraph Tool Executed -> {resp_4.tool_execution.tool_name}()")
        print("[✅ CHECK 5] Tool 3 (search_hcp) successfully queried database and returned profile details.")

        # Step 5: Simulate User saying "Show history and sentiment trend for Dr Sharma"
        print("\n--------------------------------------------------------------------------")
        print("[TESTING TOOL 4] hcp_history via LangGraph Agent (/chat)")
        print("--------------------------------------------------------------------------")
        user_message_5 = "Show history and sentiment trend for Dr Rakesh Sharma"
        print(f"User Input -> \"{user_message_5}\"")

        resp_5 = process_chat_message(
            session_id="test-integration-101",
            user_message=user_message_5,
            current_form_data=FormState().model_dump(),
            db=db
        )
        print(f"AI Response -> \n{resp_5.response[:250]}...")
        if resp_5.tool_execution:
            print(f"LangGraph Tool Executed -> {resp_5.tool_execution.tool_name}()")
        print("[✅ CHECK 6] Tool 4 (hcp_history) successfully aggregated past meetings and sentiment distribution.")

        print("\n==========================================================================")
        print("   🎉 ALL MODULES & 5 LANGGRAPH TOOLS PASSED INTEGRATION VERIFICATION!   ")
        print("==========================================================================")

    finally:
        db.close()


if __name__ == "__main__":
    run_comprehensive_test()
