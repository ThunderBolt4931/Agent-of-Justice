from __future__ import annotations
import os
from typing import List, Dict, Optional, Union
from groq import Groq
import pandas as pd
import json

class CourtAgent:
    """Base class for all courtroom agents"""
    
    def __init__(self,
                 name: str,
                 role: str,
                 system_prompt: str,
                 model: str = "llama3-70b-8192"):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt.strip()
        self.history: List[Dict[str, str]] = []  # list of {"role": ..., "content": ...}
        self.client = Groq(api_key="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")  # make sure this env-var is set
        self.model = model
    
    def respond(self, user_msg: str, **gen_kwargs) -> str:
        """Generate a response from the agent based on the prompt and history"""
        # Format messages for Groq API
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": user_msg})
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            **gen_kwargs
        )
        
        answer = completion.choices[0].message.content
        
        # keep chat memory
        self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": answer})
        return answer


class CourtSimulation:
    """Main controller class for managing the courtroom simulation"""
    
    def __init__(self, case_id: str, case_description: str):
        self.case_id = case_id
        self.case_description = case_description
        self.transcript = []  # Complete trial transcript
        self.agents = {}  # Stores all active agents
        self.witnesses = []  # Track witnesses
        self.verdict = None  # Final verdict (1 for GRANTED, 0 for DENIED)
        
        # Initialize core agents
        self._initialize_core_agents()
    
    def _initialize_core_agents(self):
        """Initialize the minimum required agents for the trial"""
        self.agents["judge"] = CourtAgent(
            name="Judge Morgan",
            role="judge",
            system_prompt=JUDGE_SYSTEM
        )
        
        self.agents["defense_lawyer"] = CourtAgent(
            name="Alex Carter",
            role="defense_lawyer",
            system_prompt=DEFENSE_SYSTEM
        )
        
        self.agents["prosecution"] = CourtAgent(
            name="Jordan Blake",
            role="prosecution",
            system_prompt=PROSECUTION_SYSTEM
        )
        
        self.agents["defendant"] = CourtAgent(
            name="Defendant",
            role="defendant",
            system_prompt=DEFENDANT_SYSTEM
        )
        
        self.agents["plaintiff"] = CourtAgent(
            name="Plaintiff",
            role="plaintiff",
            system_prompt=PLAINTIFF_SYSTEM
        )
    
    def _log_statement(self, speaker_role: str, content: str):
        """Log a statement to the trial transcript"""
        speaker_name = self.agents[speaker_role].name
        entry = {
            "speaker_role": speaker_role,
            "speaker_name": speaker_name,
            "content": content
        }
        self.transcript.append(entry)
        print(f"{speaker_name.upper()} ({speaker_role}):\n{content}\n")
    
    def create_witness(self, name: str, background: str) -> str:
        """Dynamically create a witness agent"""
        witness_id = f"witness_{len(self.witnesses) + 1}"
        witness_prompt = WITNESS_SYSTEM.format(name=name, background=background)
        
        self.agents[witness_id] = CourtAgent(
            name=name,
            role="witness",
            system_prompt=witness_prompt
        )
        
        self.witnesses.append(witness_id)
        return witness_id
    
    def run_phase_1_opening_statements(self):
        """Phase 1: Opening statements from prosecution and defense"""
        print("==== PHASE 1: OPENING STATEMENTS ====\n")
        
        # Judge introduces the case
        intro_prompt = f"Introduce the case and invite opening statements. Case: {self.case_description}"
        intro = self.agents["judge"].respond(intro_prompt)
        self._log_statement("judge", intro)
        
        # Prosecution opening statement
        p_prompt = f"Present your opening statement about the case: {self.case_description}"
        p_open = self.agents["prosecution"].respond(p_prompt)
        self._log_statement("prosecution", p_open)
        
        # Defense opening statement
        d_prompt = f"Present your opening statement responding to the prosecution's claims: {p_open}"
        d_open = self.agents["defense_lawyer"].respond(d_prompt)
        self._log_statement("defense_lawyer", d_open)
    
    def run_phase_2_witness_examination(self):
        """Phase 2: Witness examination and arguments"""
        print("==== PHASE 2: WITNESS EXAMINATION & ARGUMENTS ====\n")
        
        # Judge invites witnesses
        judge_invite = self.agents["judge"].respond("Invite the parties to present witnesses or evidence")
        self._log_statement("judge", judge_invite)
        
        # Let's dynamically create witnesses based on the case
        witness_prompt = f"Based on the case ({self.case_description}), suggest 1-2 key witnesses who should testify, with their names and brief backgrounds"
        witnesses_suggestion = self.agents["prosecution"].respond(witness_prompt)
        self._log_statement("prosecution", witnesses_suggestion)
        
        # Parse witness suggestions and create witnesses
        # For simplicity, we'll manually create one witness for each side
        plaintiff_witness = self.create_witness(
            "Dr. Jamie Reynolds", 
            "Expert in the relevant field with knowledge of the case facts"
        )
        
        defense_witness = self.create_witness(
            "Sam Morgan",
            "Character witness who can speak to defendant's reputation and behavior"
        )
        
        # Prosecution examines their witness
        exam_prompt = f"Examine your witness Dr. Jamie Reynolds about key evidence in this case: {self.case_description}"
        examination = self.agents["prosecution"].respond(exam_prompt)
        self._log_statement("prosecution", examination)
        
        # Witness responds
        witness_resp = self.agents[plaintiff_witness].respond(f"Respond to this examination: {examination}")
        self._log_statement(plaintiff_witness, witness_resp)
        
        # Defense cross-examines
        cross_prompt = f"Cross-examine the witness Dr. Jamie Reynolds based on their testimony: {witness_resp}"
        cross_exam = self.agents["defense_lawyer"].respond(cross_prompt)
        self._log_statement("defense_lawyer", cross_exam)
        
        # Witness responds to cross
        cross_resp = self.agents[plaintiff_witness].respond(f"Respond to this cross-examination: {cross_exam}")
        self._log_statement(plaintiff_witness, cross_resp)
        
        # Defense presents their witness
        defense_exam = self.agents["defense_lawyer"].respond(f"Examine your witness Sam Morgan about this case: {self.case_description}")
        self._log_statement("defense_lawyer", defense_exam)
        
        # Defense witness responds
        def_witness_resp = self.agents[defense_witness].respond(f"Respond to this examination: {defense_exam}")
        self._log_statement(defense_witness, def_witness_resp)
        
        # Prosecution cross-examines
        pros_cross = self.agents["prosecution"].respond(f"Cross-examine the witness Sam Morgan based on their testimony: {def_witness_resp}")
        self._log_statement("prosecution", pros_cross)
        
        # Defense witness responds to cross
        def_cross_resp = self.agents[defense_witness].respond(f"Respond to this cross-examination: {pros_cross}")
        self._log_statement(defense_witness, def_cross_resp)
    
    def run_phase_3_closing_statements(self):
        """Phase 3: Closing statements"""
        print("==== PHASE 3: CLOSING STATEMENTS ====\n")
        
        # Judge invites closing statements
        judge_invite = self.agents["judge"].respond("Invite the parties to present their closing statements")
        self._log_statement("judge", judge_invite)
        
        # Prosecution closing
        trial_summary = self._summarize_trial_so_far()
        p_close_prompt = f"Present your closing statement summarizing the evidence and arguments. Trial summary: {trial_summary}"
        p_close = self.agents["prosecution"].respond(p_close_prompt)
        self._log_statement("prosecution", p_close)
        
        # Defense closing
        d_close_prompt = f"Present your closing statement responding to the prosecution's closing and summarizing your case. Prosecution closing: {p_close}"
        d_close = self.agents["defense_lawyer"].respond(d_close_prompt)
        self._log_statement("defense_lawyer", d_close)
    
    def run_phase_4_verdict(self):
        """Phase 4: Judge's ruling"""
        print("==== PHASE 4: JUDGE'S RULING ====\n")
        
        # Summarize the trial for the judge
        trial_summary = self._summarize_trial_so_far()
        
        # Judge deliberates and delivers verdict
        verdict_prompt = f"""
        Deliberate on this case and deliver your final verdict.
        Trial summary: {trial_summary}
        
        Your ruling should conclude with either GRANTED (in favor of plaintiff) or DENIED (in favor of defendant).
        """
        
        verdict_full = self.agents["judge"].respond(verdict_prompt)
        self._log_statement("judge", verdict_full)
        
        # Extract the verdict (GRANTED or DENIED)
        if "GRANTED" in verdict_full.upper():
            self.verdict = 1  # GRANTED
        else:
            self.verdict = 0  # DENIED
        
        return self.verdict
    
    def _summarize_trial_so_far(self) -> str:
        """Create a concise summary of the trial transcript for context"""
        summary = "Trial Summary:\n"
        for entry in self.transcript[-10:]:  # Use only recent entries to avoid token limits
            summary += f"- {entry['speaker_name']} ({entry['speaker_role']}): {entry['content'][:100]}...\n"
        return summary
    
    def run_full_trial(self) -> int:
        """Run the complete trial simulation"""
        print(f"\n===== BEGINNING TRIAL FOR CASE #{self.case_id} =====\n")
        print(f"CASE DESCRIPTION: {self.case_description}\n")
        
        # Run each phase of the trial
        self.run_phase_1_opening_statements()
        self.run_phase_2_witness_examination()
        self.run_phase_3_closing_statements()
        verdict = self.run_phase_4_verdict()
        
        print(f"\n===== TRIAL COMPLETED: VERDICT {'GRANTED' if verdict == 1 else 'DENIED'} =====\n")
        return verdict


# System prompts for each agent role

JUDGE_SYSTEM = """
You are **Judge Morgan**, presiding over this court case.
Goals:
• Maintain order and decorum in the courtroom
• Ensure proper legal procedure is followed
• Make rulings on objections and points of law
• Deliver a fair and impartial verdict based on the evidence and arguments presented
Style:
• Formal, authoritative, and impartial
• Use legal terminology appropriately
• Address all parties with equal respect
Ethics:
• Make decisions based solely on the law and facts presented
• Show no bias toward either party
• Ensure both sides have fair opportunity to present their case

At the end of the trial, you must deliver a verdict of either GRANTED (in favor of plaintiff) or DENIED (in favor of defendant).
"""

DEFENSE_SYSTEM = """
You are **Alex Carter**, lead *defense counsel*.
Goals:
• Protect the constitutional rights of the defendant
• Raise reasonable doubt by pointing out missing evidence or alternative explanations
• Be respectful to the Court and to opposing counsel
Style:
• Crisp, persuasive, grounded in precedent and facts provided
• When citing precedent: give short case name + year (e.g., *Miranda v. Arizona* (1966))
Ethics:
• Do not fabricate evidence; admit uncertainty when required
• Zealously advocate for your client within ethical boundaries
• Present the strongest possible defense based on the available facts
"""

PROSECUTION_SYSTEM = """
You are **Jordan Blake**, *Assistant District Attorney* for the State.
Goals:
• Present the strongest good‑faith case against the accused
• Lay out facts logically, citing exhibits or witness statements when available
• Anticipate and rebut common defense arguments
Style:
• Formal but plain English; persuasive, with confident tone
Ethics:
• Duty is to justice, not merely to win. Concede points when ethically required
• Present the evidence fairly while arguing for your interpretation of it
• Build a convincing narrative that proves the elements of the charged offense
"""

DEFENDANT_SYSTEM = """
You are the defendant in this case.
Goals:
• Answer questions truthfully but in a way that presents you in the best light
• Cooperate with your defense attorney
• Maintain composure even under challenging questioning
Style:
• Respectful to the court
• Clear and direct in your responses
• Appear sincere and credible
Ethics:
• Do not lie under oath, but you may emphasize favorable facts and minimize unfavorable ones
• Show appropriate emotion but avoid appearing defensive or confrontational
"""

PLAINTIFF_SYSTEM = """
You are the plaintiff in this case.
Goals:
• Present your grievance clearly and persuasively
• Support your claims with specific details and evidence
• Respond to questioning in a way that strengthens your case
Style:
• Sincere and straightforward
• Emphasize the harm or damages you have suffered
• Be consistent in your account of events
Ethics:
• Stick to the facts but present them from your perspective
• Avoid exaggeration while conveying the significance of your complaint
• Demonstrate why you are entitled to the remedy you seek
"""

WITNESS_SYSTEM = """
You are {name}, a witness in this court case.
Background:
{background}

Goals:
• Provide testimony based on your personal knowledge or expertise
• Answer questions truthfully and to the best of your ability
• Maintain your credibility through consistent testimony
Style:
• Direct and factual in your responses
• Use language appropriate to your background and expertise
• Show appropriate confidence about what you know and uncertainty about what you don't
Ethics:
• Tell the truth as you understand it
• Do not speculate beyond your knowledge or expertise unless asked to
• Maintain composure during cross-examination
"""


def process_case_file(csv_path: str):
    """Process a CSV file of cases and return predictions"""
    # Read the case data
    df = pd.read_csv(csv_path)
    
    # Store predictions
    predictions = []
    
    # Process each case
    for _, row in df.iterrows():
        case_id = row['id']
        case_text = row['text']
        
        # Skip if case text is too short or malformed
        if not isinstance(case_text, str) or len(case_text) < 10:
            predictions.append((case_id, 0))  # Default to DENIED
            continue
            
        # Run the simulation
        try:
            simulation = CourtSimulation(case_id, case_text)
            verdict = simulation.run_full_trial()
            predictions.append((case_id, verdict))
        except Exception as e:
            print(f"Error processing case {case_id}: {e}")
            predictions.append((case_id, 0))  # Default to DENIED on error
    
    # Create submission dataframe
    submission = pd.DataFrame(predictions, columns=['ID', 'VERDICT'])
    return submission


# Example usage
if __name__ == "__main__":
    # For testing with a single case
    test_case = """
    The plaintiff alleges that the defendant, a former employee, violated a non-compete agreement
    by establishing a competing business within 6 months of employment termination. The agreement
    specified a 1-year restriction. The defendant claims the non-compete is overly broad and therefore
    unenforceable, covering an unreasonable geographic area. Evidence shows the defendant opened 
    a similar business 8 miles from the plaintiff's location.
    """
    
    simulation = CourtSimulation("test_1", test_case)
    verdict = simulation.run_full_trial()
    print(f"Final verdict: {'GRANTED' if verdict == 1 else 'DENIED'}")
    
    # To process the actual competition data:
    submission = process_case_file("/content/data2 (1).csv")
    submission.to_csv("/content/submission.csv", index=False)
